"""
Embedding generation module using sentence-transformers.
"""
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingGenerator:
    """Handles text embedding generation."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        import json, traceback
        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"embeddings.py:19","message":"Starting embedding model load","data":{"model_name":model_name},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion
        print(f"Loading embedding model: {model_name}")
        try:
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            # #region agent log
            try:
                with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"embeddings.py:25","message":"Embedding model loaded successfully","data":{"model_name":model_name},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            print("Embedding model loaded successfully")
        except Exception as e:
            # #region agent log
            try:
                with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"startup","hypothesisId":"C","location":"embeddings.py:30","message":"Embedding model load failed","data":{"error":str(e),"traceback":traceback.format_exc()},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.model.get_sentence_embedding_dimension())
        
        embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of input texts
            
        Returns:
            Numpy array of embeddings (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # Filter empty texts
        valid_texts = [text if text and text.strip() else " " for text in texts]
        
        embeddings = self.model.encode(
            valid_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 10
        )
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return self.model.get_sentence_embedding_dimension()

