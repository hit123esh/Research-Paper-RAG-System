"""
Retrieval module for RAG pipeline.
"""
from typing import List, Dict, Any, Optional, Tuple
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import VectorStore


class Retriever:
    """Handles retrieval of relevant chunks for RAG."""
    
    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        vector_store: VectorStore,
        top_k: int = 5,
        similarity_threshold: float = 0.3
    ):
        """
        Initialize retriever.
        
        Args:
            embedding_generator: Embedding generator instance
            vector_store: Vector store instance
            top_k: Number of top chunks to retrieve
            similarity_threshold: Minimum similarity score for relevance
        """
        self.embedding_generator = embedding_generator
        self.vector_store = vector_store
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
    
    def retrieve(
        self,
        query: str,
        paper_id: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query text
            paper_id: Paper identifier
            top_k: Override default top_k
            similarity_threshold: Override default threshold (None = use default, can be 0.0 for no threshold)
            
        Returns:
            Tuple of (retrieved_chunks, max_similarity_score)
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        query_embedding_list = query_embedding.tolist()
        
        # Search vector store
        k = top_k if top_k is not None else self.top_k
        
        # Handle threshold: if explicitly set to 0.0, retrieve without threshold filtering
        # Otherwise use provided threshold or default
        if similarity_threshold is not None:
            threshold = similarity_threshold
        else:
            threshold = self.similarity_threshold
        
        # If threshold is 0.0, we still need to filter but get top-k regardless
        # ChromaDB will return top-k, then we filter by threshold
        retrieved_chunks = self.vector_store.search(
            paper_id=paper_id,
            query_embedding=query_embedding_list,
            top_k=k,
            score_threshold=threshold if threshold > 0.0 else 0.0
        )
        
        # If threshold was 0.0, we got top-k regardless of score
        # Get max similarity score (even if below threshold)
        max_score = max([chunk['score'] for chunk in retrieved_chunks]) if retrieved_chunks else 0.0
        
        # Ensure score is in [0, 1] range (safety clamp)
        # Scores from vector_store are already normalized, but clamp for safety
        max_score = max(0.0, min(1.0, max_score))
        
        return retrieved_chunks, max_score
    
    def retrieve_multiple(
        self,
        query: str,
        paper_ids: List[str],
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> Dict[str, Tuple[List[Dict[str, Any]], float]]:
        """
        Retrieve chunks from multiple papers.
        
        Args:
            query: User query text
            paper_ids: List of paper identifiers
            top_k: Override default top_k
            similarity_threshold: Override default threshold (None = use default, can be 0.0 for no threshold)
            
        Returns:
            Dictionary mapping paper_id to (chunks, max_score) tuple
        """
        # Generate query embedding once
        query_embedding = self.embedding_generator.generate_embedding(query)
        query_embedding_list = query_embedding.tolist()
        
        k = top_k if top_k is not None else self.top_k
        
        # Handle threshold: if explicitly set to 0.0, retrieve without threshold filtering
        if similarity_threshold is not None:
            threshold = similarity_threshold
        else:
            threshold = self.similarity_threshold
        
        results = {}
        for paper_id in paper_ids:
            retrieved_chunks = self.vector_store.search(
                paper_id=paper_id,
                query_embedding=query_embedding_list,
                top_k=k,
                score_threshold=threshold if threshold > 0.0 else 0.0
            )
            max_score = max([chunk['score'] for chunk in retrieved_chunks]) if retrieved_chunks else 0.0
            
            # Ensure score is in [0, 1] range (safety clamp)
            # Scores from vector_store are already normalized, but clamp for safety
            max_score = max(0.0, min(1.0, max_score))
            
            results[paper_id] = (retrieved_chunks, max_score)
        
        return results
    
    def is_relevant(self, max_similarity_score: float) -> bool:
        """
        Determine if query is relevant based on similarity score.
        
        Args:
            max_similarity_score: Maximum similarity score from retrieval
            
        Returns:
            True if relevant, False otherwise
        """
        return max_similarity_score >= self.similarity_threshold
    
    def get_relevance_tier(self, max_similarity_score: float) -> str:
        """
        Classify relevance into tiers for flexible handling.
        
        Args:
            max_similarity_score: Maximum similarity score from retrieval
            
        Returns:
            'high', 'medium', or 'low'
        """
        if max_similarity_score < 0.15:
            return 'low'  # Very low - likely unrelated
        elif max_similarity_score < self.similarity_threshold:
            return 'medium'  # Moderate - allow fallback retrieval
        else:
            return 'high'  # High - normal RAG flow

