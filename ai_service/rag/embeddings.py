"""
DevMind - Embedding generation using HuggingFace sentence-transformers.
All AI/ML logic runs in Python.
"""

import os
from typing import List
from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:
    """Generates embeddings for code chunks using HuggingFace models."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.
        Uses a lightweight model suitable for code/text embeddings.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each is a list of floats)
        """
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query string.

        Args:
            query: The query text

        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode([query], convert_to_numpy=True)
        return embedding[0].tolist()
