"""
DevMind - ChromaDB client for vector storage and retrieval.
Persistent local storage in chroma_db folder.
"""

import os
from typing import List, Optional
import chromadb
from chromadb.config import Settings

from .embeddings import EmbeddingGenerator
from .chunker import chunk_code


class ChromaClient:
    """ChromaDB client for code embedding storage and retrieval."""

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "devmind_code",
    ):
        """
        Initialize Chroma client with persistent storage.

        Args:
            persist_directory: Local folder for Chroma persistence
            collection_name: Name of the collection
        """
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=os.path.abspath(persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection_name = collection_name
        self.embedder = EmbeddingGenerator()
        self._collection = None

    def _get_collection(self):
        """Get or create the collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "DevMind code embeddings"},
            )
        return self._collection

    def add_repo(
        self,
        repo_id: str,
        file_path: str,
        content: str,
    ) -> int:
        """
        Chunk, embed, and add a single file to Chroma.

        Args:
            repo_id: Unique repo identifier (e.g. owner/repo)
            file_path: Relative path within repo
            content: File content

        Returns:
            Number of chunks added
        """
        chunks = chunk_code(content, file_path)
        if not chunks:
            return 0

        texts = [c[0] for c in chunks]
        metadatas = [
            {
                "repo_id": repo_id,
                "file_path": c[1]["file_path"],
                "start_line": str(c[1]["start_line"]),
                "end_line": str(c[1]["end_line"]),
            }
            for c in chunks
        ]
        embeddings = self.embedder.embed_documents(texts)
        ids = [f"{repo_id}::{file_path}::{i}" for i in range(len(texts))]

        # ChromaDB max batch size ~5461 - add in smaller batches
        BATCH_SIZE = 4000
        coll = self._get_collection()
        for i in range(0, len(texts), BATCH_SIZE):
            end = min(i + BATCH_SIZE, len(texts))
            coll.add(
                ids=ids[i:end],
                embeddings=embeddings[i:end],
                documents=texts[i:end],
                metadatas=metadatas[i:end],
            )
        return len(chunks)

    def delete_repo(self, repo_id: str) -> None:
        """Remove all chunks for a repo."""
        coll = self._get_collection()
        # Chroma supports filter by metadata
        coll.delete(where={"repo_id": repo_id})

    def query(
        self,
        query_text: str,
        repo_id: Optional[str] = None,
        n_results: int = 5,
    ) -> List[dict]:
        """
        Query for relevant code chunks.

        Args:
            query_text: User question
            repo_id: Optional - limit to this repo
            n_results: Number of chunks to return

        Returns:
            List of {content, metadata} dicts
        """
        coll = self._get_collection()
        query_embedding = self.embedder.embed_query(query_text)
        where = {"repo_id": repo_id} if repo_id else None
        results = coll.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas"],
        )
        out = []
        docs = results["documents"][0] if results["documents"] else []
        metas = results["metadatas"][0] if results["metadatas"] else []
        for d, m in zip(docs, metas):
            out.append({"content": d, "metadata": m or {}})
        return out
