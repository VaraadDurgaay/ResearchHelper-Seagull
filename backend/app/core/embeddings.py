"""
Embeddings Module
Handles embedding generation for text chunks using sentence-transformers.
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Global model instance (loaded lazily)
_model: SentenceTransformer = None
_model_name: str = "all-MiniLM-L6-v2"


def _get_model() -> SentenceTransformer:
    """Get or load the embedding model (singleton pattern)"""
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {_model_name}")
        _model = SentenceTransformer(_model_name)
        logger.info("Embedding model loaded successfully")
    return _model


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text to generate embedding for
        
    Returns:
        List of floats representing the embedding vector
    """
    if not text or len(text.strip()) == 0:
        # Return zero vector if text is empty
        model = _get_model()
        return [0.0] * model.get_sentence_embedding_dimension()
    
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently.
    
    Args:
        texts: List of texts to generate embeddings for
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    # Filter out empty texts
    non_empty_texts = [text if text and text.strip() else "" for text in texts]
    
    model = _get_model()
    embeddings = model.encode(
        non_empty_texts,
        normalize_embeddings=True,
        show_progress_bar=False,
        batch_size=32
    )
    
    return embeddings.tolist()


def get_embedding_dimensions() -> int:
    """
    Get the dimension of embeddings for the current model.
    
    Returns:
        Number of dimensions in the embedding vector
    """
    model = _get_model()
    return model.get_sentence_embedding_dimension()
