"""
Service for managing papers and RAG operations.
"""
import os
import uuid
from typing import Dict, Any, List
import aiofiles
from fastapi import UploadFile

from app.rag.document_processor import DocumentProcessor
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.rag.llm_client import OllamaClient


# Query expansion keywords to improve matching for numeric/methods questions
QUERY_EXPANSION_KEYWORDS = [
    "sample size", "methods", "study design", "patients", "cohort", 
    "statistics", "measurements", "data", "results", "findings",
    "participants", "subjects", "measurement", "count", "number"
]


def normalize_relevance_score(score: float) -> float:
    """
    Normalize and clamp relevance score to [0, 1] range.
    
    Args:
        score: Raw similarity score (may be in [-1, 1] or already normalized)
        
    Returns:
        Score clamped to [0, 1] range
    """
    # If score is already in [0, 1], just clamp
    # If score is in [-1, 1], normalize first
    if score < 0.0:
        # Normalize from [-1, 1] to [0, 1]
        normalized = (score + 1.0) / 2.0
    else:
        normalized = score
    
    # Safety clamp to ensure [0, 1] range
    return max(0.0, min(1.0, normalized))


def detect_question_type(question: str) -> str:
    """
    Detect question type to determine retrieval strategy.
    
    Returns:
        'overview': Conceptual/descriptive questions (what, which, why, how, describe, explain)
        'numerical': Questions requiring specific numbers/statistics
        'methods': Questions about study design/methods
    """
    q_lower = question.lower().strip()
    
    # Overview-style questions (soft relevance mode)
    overview_starters = ["what", "which", "why", "how", "describe", "explain", "what are", "what is"]
    if any(q_lower.startswith(starter) for starter in overview_starters):
        # But exclude "how many" which is numerical
        if not q_lower.startswith("how many"):
            return 'overview'
    
    # Numerical questions (strict relevance)
    numerical_indicators = [
        "how many", "count", "number of", "sample size", "n=", "n =",
        "p-value", "p value", "p<", "p<=", "statistical significance",
        "percentage", "percent", "%", "ratio", "proportion"
    ]
    if any(ind in q_lower for ind in numerical_indicators):
        return 'numerical'
    
    # Methods/design questions (strict relevance)
    methods_indicators = [
        "statistical method", "statistical analysis", "study design",
        "experimental design", "methodology", "statistical test"
    ]
    if any(ind in q_lower for ind in methods_indicators):
        return 'methods'
    
    # Default to overview for conceptual questions
    return 'overview'


def expand_query(question: str) -> str:
    """
    Expand query with relevant keywords to improve embedding match.
    Helps with numeric and methods questions.
    """
    q_lower = question.lower()
    
    # Check if question is about numbers, methods, or measurements
    numeric_indicators = ["how many", "count", "number", "size", "measure", "statistic"]
    methods_indicators = ["method", "design", "approach", "technique", "analysis"]
    
    is_numeric = any(ind in q_lower for ind in numeric_indicators)
    is_methods = any(ind in q_lower for ind in methods_indicators)
    
    expanded = question
    if is_numeric or is_methods:
        # Add relevant keywords to improve semantic matching
        keywords_to_add = []
        if is_numeric:
            keywords_to_add.extend(["sample size", "count", "number", "measurements"])
        if is_methods:
            keywords_to_add.extend(["methods", "study design", "statistics"])
        
        # Append keywords that aren't already in the question
        for keyword in keywords_to_add:
            if keyword not in q_lower:
                expanded += f" {keyword}"
    
    return expanded


class PaperService:
    """Service for paper management and RAG operations."""

    def __init__(
        self,
        upload_dir: str = "uploads",
        vector_db_dir: str = "vector_db",
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        top_k: int = 5,
        similarity_threshold: float = 0.3,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        ollama_base_url: str = None,
        ollama_model: str = None
    ):
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(vector_db_dir, exist_ok=True)

        self.upload_dir = upload_dir

        self.document_processor = DocumentProcessor(chunk_size, chunk_overlap)
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.vector_store = VectorStore(vector_db_dir)

        self.retriever = Retriever(
            self.embedding_generator,
            self.vector_store,
            top_k,
            similarity_threshold
        )

        self.llm_client = OllamaClient(ollama_base_url, ollama_model)

        self.papers: Dict[str, Dict[str, Any]] = {}

    # --------------------------------------------------
    # PDF UPLOAD
    # --------------------------------------------------

    async def upload_pdf(self, file: UploadFile, paper_id: str = None) -> Dict[str, Any]:
        if paper_id is None:
            paper_id = str(uuid.uuid4())

        file_path = os.path.join(self.upload_dir, f"{paper_id}.pdf")

        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty")

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        paper_name = file.filename.replace(".pdf", "") if file.filename else paper_id
        print(f"[Progress] Processing PDF: {paper_name}")

        chunks = self.document_processor.process_pdf(file_path, paper_name)
        if not chunks:
            raise ValueError("No text could be extracted from the PDF")

        print(f"[Progress] Generating embeddings for {len(chunks)} chunks...")
        embeddings = self.embedding_generator.generate_embeddings_batch(
            [c["text"] for c in chunks]
        ).tolist()

        self.vector_store.add_chunks(paper_id, chunks, embeddings)

        self.papers[paper_id] = {
            "paper_id": paper_id,
            "name": paper_name,
            "file_path": file_path,
            "chunk_count": len(chunks),
        }

        print(f"Paper {paper_name} processed successfully")
        return self.papers[paper_id]

    # --------------------------------------------------
    # QUESTION ANSWERING
    # --------------------------------------------------

    async def ask_question(
        self,
        paper_id: str,
        question: str,
        explanation_level: str = "technical",
        paper2_id: str = None
    ) -> Dict[str, Any]:

        if paper_id not in self.papers:
            raise ValueError("Paper not found")

        # ----------------------------
        # SINGLE PAPER
        # ----------------------------
        if not paper2_id:
            # Detect question type to determine retrieval strategy
            question_type = detect_question_type(question)
            
            # Expand query to improve matching for numeric/methods questions
            expanded_query = expand_query(question)
            
            # Determine retrieval strategy based on question type
            if question_type == 'overview':
                # Soft relevance mode: Always retrieve top-k chunks, use lower threshold
                # This helps with narrative review papers where high-level questions
                # don't match individual chunks strongly
                chunks, max_score = self.retriever.retrieve(
                    expanded_query,
                    paper_id,
                    top_k=5,
                    similarity_threshold=0.0  # No threshold filtering - get top-k anyway
                )
                
                # Only reject if we got zero chunks (paper is empty or error)
                if not chunks:
                    return {
                        "answer": "The uploaded research paper does not contain information relevant to this question.",
                        "sources": [],
                        "relevance_score": 0.0,  # Already normalized (0.0)
                        "is_relevant": False,
                    }
                
                # Always proceed to LLM with retrieved chunks
                # LLM will determine if answer can be constructed from context
                
            else:  # numerical or methods - strict relevance
                # Initial retrieval with normal threshold
                chunks, max_score = self.retriever.retrieve(expanded_query, paper_id)
                
                # Get relevance tier
                relevance_tier = self.retriever.get_relevance_tier(max_score)
                
                # Handle based on relevance tier
                if relevance_tier == 'low':
                    # Very low similarity - likely unrelated question
                    return {
                        "answer": "The uploaded research paper does not contain information relevant to this question. Please ask questions related to the content of the uploaded paper.",
                        "sources": [],
                        "relevance_score": normalize_relevance_score(max_score),
                        "is_relevant": False,
                    }
                elif relevance_tier == 'medium':
                    # Medium similarity - allow fallback retrieval with lower threshold
                    chunks, max_score = self.retriever.retrieve(
                        expanded_query, 
                        paper_id, 
                        top_k=5,
                        similarity_threshold=0.15  # Lower threshold for fallback
                    )
                    # If still no chunks, try even lower
                    if not chunks:
                        chunks, max_score = self.retriever.retrieve(
                            expanded_query,
                            paper_id,
                            top_k=5,
                            similarity_threshold=0.0  # No threshold - get top-k anyway
                        )
                
                # If we have chunks (even from fallback), proceed to LLM
                if not chunks:
                    return {
                        "answer": "The uploaded research paper does not contain information relevant to this question.",
                        "sources": [],
                        "relevance_score": normalize_relevance_score(max_score),
                        "is_relevant": False,
                    }
            
            # We have chunks - always pass to LLM
            # LLM will answer strictly from context and say if information is missing
            context = "\n\n".join(c["text"] for c in chunks)
            system_prompt = self._get_system_prompt(explanation_level)

            answer = self.llm_client.generate(
                prompt=question,
                context=context,
                system_prompt=system_prompt,
            )

            return {
                "answer": answer,
                "sources": [c["text"][:200] + "..." for c in chunks[:5]],
                "relevance_score": normalize_relevance_score(max_score),
                "is_relevant": True,
            }

        # ----------------------------
        # COMPARISON
        # ----------------------------
        question_type = detect_question_type(question)
        expanded_query = expand_query(question)
        
        # Use soft relevance for overview questions in comparison mode too
        if question_type == 'overview':
            # Soft relevance: get top-k chunks regardless of threshold
            results = self.retriever.retrieve_multiple(
                expanded_query,
                [paper_id, paper2_id],
                top_k=5,
                similarity_threshold=0.0
            )
        else:
            # Strict relevance for numerical/methods questions
            results = self.retriever.retrieve_multiple(expanded_query, [paper_id, paper2_id])
        
        p1_chunks, p1_score = results[paper_id]
        p2_chunks, p2_score = results[paper2_id]
        max_score = max(p1_score, p2_score)
        
        # For strict questions, check relevance tier
        if question_type != 'overview':
            relevance_tier = self.retriever.get_relevance_tier(max_score)
            
            if relevance_tier == 'low':
                return {
                    "answer": "The uploaded papers do not contain relevant information for this comparison.",
                    "sources": [],
                    "relevance_score": normalize_relevance_score(max_score),
                    "is_relevant": False,
                }
            elif relevance_tier == 'medium':
                # Fallback retrieval with lower threshold
                results = self.retriever.retrieve_multiple(
                    expanded_query,
                    [paper_id, paper2_id],
                    top_k=5,
                    similarity_threshold=0.15
                )
                p1_chunks, p1_score = results[paper_id]
                p2_chunks, p2_score = results[paper2_id]
                max_score = max(p1_score, p2_score)
        
        # If we have chunks from either paper, proceed
        # For overview questions, always proceed if chunks exist
        if p1_chunks or p2_chunks:
            context = (
                f"Paper 1:\n{''.join(c['text'] for c in p1_chunks[:3])}\n\n"
                f"Paper 2:\n{''.join(c['text'] for c in p2_chunks[:3])}"
            )

            system_prompt = self._get_system_prompt(explanation_level, comparison=True)

            answer = self.llm_client.generate(
                prompt=question,
                context=context,
                system_prompt=system_prompt,
            )

            return {
                "answer": answer,
                "sources": [],
                "relevance_score": normalize_relevance_score(max_score),
                "is_relevant": True,
            }
        else:
            # Only reject if we got zero chunks
            return {
                "answer": "The uploaded papers do not contain relevant information for this comparison.",
                "sources": [],
                "relevance_score": normalize_relevance_score(max_score),
                "is_relevant": False,
            }

    # --------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------

    def _get_system_prompt(self, explanation_level: str, comparison: bool = False) -> str:
        prompt = (
            "You are an expert academic researcher. Answer questions based on the provided context from the research paper(s).\n\n"
            "Guidelines:\n"
            "- Answer using information from the provided context. You may summarize across sections (Abstract, Methods, Results, etc.).\n"
            "- You may infer answers that are implied across multiple chunks, but stay grounded in the context.\n"
            "- If information is not explicitly stated or cannot be reasonably inferred from the context, clearly state: 'This information is not mentioned in the provided context.'\n"
            "- Do not use external knowledge beyond what is in the context.\n"
            "- Maintain an academic and objective tone."
        )

        if comparison:
            prompt += "\n- Clearly distinguish between Paper 1 and Paper 2 when comparing."

        if explanation_level == "simple":
            prompt += "\n- Explain concepts in simple, accessible language suitable for a general audience."
        else:
            prompt += "\n- Use technical terminology and maintain academic rigor in your explanations."

        return prompt

    # --------------------------------------------------
    # METADATA
    # --------------------------------------------------

    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        return self.papers.get(paper_id)

    def list_papers(self) -> List[Dict[str, Any]]:
        return list(self.papers.values())

    # --------------------------------------------------
    # COMPARISON (BASIC)
    # --------------------------------------------------
    async def compare_papers(
        self,
        paper1_id: str,
        paper2_id: str,
        aspects: List[str]
    ) -> Dict[str, Any]:
        """
        Basic comparison between two papers.

        Returns a lightweight structure with top retrieved context for each aspect.
        No LLM comparison to keep current client compatible.
        """
        if paper1_id not in self.papers or paper2_id not in self.papers:
            raise ValueError("One or both papers not found")

        paper1_name = self.papers[paper1_id].get("name", "Paper 1")
        paper2_name = self.papers[paper2_id].get("name", "Paper 2")

        comparison_results: Dict[str, Any] = {}

        for aspect in aspects:
            # Simple aspect query
            query = f"What is the {aspect} of this research?"

            # Retrieve top chunks without strict threshold to ensure context
            p1_chunks, _ = self.retriever.retrieve(
                query, paper1_id, top_k=3, similarity_threshold=0.0
            )
            p2_chunks, _ = self.retriever.retrieve(
                query, paper2_id, top_k=3, similarity_threshold=0.0
            )

            p1_text = "\n".join([c["text"] for c in p1_chunks]) if p1_chunks else "Not available"
            p2_text = "\n".join([c["text"] for c in p2_chunks]) if p2_chunks else "Not available"

            comparison_results[aspect] = {
                "paper1": p1_text,
                "paper2": p2_text,
                "differences": "Not available",
                "raw_text": ""
            }

        return {
            "comparison": comparison_results,
            "paper1_name": paper1_name,
            "paper2_name": paper2_name
        }
