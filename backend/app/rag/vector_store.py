"""
Vector store module using ChromaDB for embedding storage and retrieval.
"""
import os
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
import uuid


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""
    
    def __init__(self, db_path: str = "vector_db"):
        """
        Initialize vector store.
        
        Args:
            db_path: Path to ChromaDB database directory
        """
        import json, traceback
        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"vector_store.py:21","message":"Initializing ChromaDB","data":{"db_path":db_path},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        os.makedirs(db_path, exist_ok=True)
        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"vector_store.py:25","message":"Creating ChromaDB PersistentClient","data":{"step":"chromadb_client_create"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        try:
            self.client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            # #region agent log
            try:
                with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"vector_store.py:31","message":"ChromaDB client created successfully","data":{"step":"chromadb_client_ready"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            self.collections = {}  # Cache for collections
        except Exception as e:
            # #region agent log
            try:
                with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"vector_store.py:36","message":"ChromaDB client creation failed","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            raise
    
    def get_or_create_collection(self, paper_id: str) -> chromadb.Collection:
        """
        Get or create a ChromaDB collection for a paper.
        
        Args:
            paper_id: Unique identifier for the paper
            
        Returns:
            ChromaDB collection
        """
        if paper_id not in self.collections:
            collection_name = f"paper_{paper_id}"
            self.collections[paper_id] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"paper_id": paper_id}
            )
        return self.collections[paper_id]
    
    def add_chunks(
        self,
        paper_id: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> None:
        """
        Add chunks and embeddings to the vector store.
        
        Args:
            paper_id: Unique identifier for the paper
            chunks: List of chunk dictionaries with 'text' and 'metadata'
            embeddings: List of embedding vectors
        
        NOTE: This writes to vector_db/ directory only. No .py files are modified.
        """
        print(f"[Vector Store] Preparing {len(chunks)} chunks for paper {paper_id}")
        collection = self.get_or_create_collection(paper_id)
        
        # Prepare data for ChromaDB
        ids = [f"{paper_id}_chunk_{i}" for i in range(len(chunks))]
        texts = [chunk['text'] for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            # ChromaDB requires metadata values to be strings, numbers, or booleans
            clean_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    clean_metadata[key] = value
                else:
                    clean_metadata[key] = str(value)
            metadatas.append(clean_metadata)
        
        print(f"[Vector Store] Writing to ChromaDB collection...")
        # Add to collection
        # NOTE: This writes to vector_db/ directory (not app/), so it won't trigger hot-reload
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print(f"[Vector Store] Write complete: {len(chunks)} chunks stored")
    
    def search(
        self,
        paper_id: str,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks in the vector store.
        
        Args:
            paper_id: Unique identifier for the paper
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of retrieved chunks with scores
        """
        try:
            collection = self.get_or_create_collection(paper_id)
            
            # Query ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Process results
            retrieved_chunks = []
            
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    # ChromaDB returns distances (lower is better), convert to similarity
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    raw_similarity = 1.0 - distance  # Convert distance to similarity
                    
                    # Normalize similarity from [-1, 1] to [0, 1] range
                    # This ensures scores are always non-negative for API validation
                    normalized_similarity = (raw_similarity + 1.0) / 2.0
                    
                    # Safety clamp to ensure [0, 1] range
                    normalized_similarity = max(0.0, min(1.0, normalized_similarity))
                    
                    # If threshold is 0.0, include all results (for fallback retrieval)
                    # Otherwise filter by threshold (using normalized score)
                    if score_threshold == 0.0 or normalized_similarity >= score_threshold:
                        retrieved_chunks.append({
                            'text': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i],
                            'score': normalized_similarity,  # Use normalized score
                            'distance': distance
                        })
            
            return retrieved_chunks
        
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    def search_multiple(
        self,
        paper_ids: List[str],
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple papers.
        
        Args:
            paper_ids: List of paper identifiers
            query_embedding: Query embedding vector
            top_k: Number of top results per paper
            score_threshold: Minimum similarity score threshold
            
        Returns:
            Dictionary mapping paper_id to list of retrieved chunks
        """
        results = {}
        for paper_id in paper_ids:
            results[paper_id] = self.search(
                paper_id, query_embedding, top_k, score_threshold
            )
        return results
    
    def delete_paper(self, paper_id: str) -> None:
        """
        Delete all chunks for a paper.
        
        Args:
            paper_id: Unique identifier for the paper
        """
        try:
            collection = self.get_or_create_collection(paper_id)
            # Delete collection
            self.client.delete_collection(name=f"paper_{paper_id}")
            if paper_id in self.collections:
                del self.collections[paper_id]
        except Exception as e:
            print(f"Error deleting paper from vector store: {e}")
    
    def get_paper_stats(self, paper_id: str) -> Dict[str, Any]:
        """
        Get statistics about stored chunks for a paper.
        
        Args:
            paper_id: Unique identifier for the paper
            
        Returns:
            Dictionary with statistics
        """
        try:
            collection = self.get_or_create_collection(paper_id)
            count = collection.count()
            return {
                'paper_id': paper_id,
                'chunk_count': count
            }
        except Exception as e:
            print(f"Error getting paper stats: {e}")
            return {'paper_id': paper_id, 'chunk_count': 0}

