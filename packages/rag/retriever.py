from packages.rag.interfaces import EmbeddingProvider, VectorStore
from packages.rag.reranker import Reranker
from typing import Any

class Retriever:
    def __init__(self, embedder: EmbeddingProvider, vector_store: VectorStore, reranker: Reranker = None) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
        self.reranker = reranker

    def retrieve(self, query: str, user_id: str, limit: int = 5) -> list[dict[str, Any]]:
        # Dense Retrieval
        [vector] = self.embedder.embed([query])
        
        # Retrieve more chunks initially to allow reranking to work effectively (e.g., 2x limit)
        initial_limit = limit * 2 if self.reranker else limit
        chunks = self.vector_store.search(vector, initial_limit, {"user_id": user_id})
        
        # Rerank if available
        if self.reranker and chunks:
            chunks = self.reranker.rerank(query, chunks, top_k=limit)
            
        return chunks