from  packages.rag.interfaces import EmbeddingProvider , VectorStore

from typing import Any

class Retriever :
    def __init__(self, embedder: EmbeddingProvider, vector_store: VectorStore) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
    def retrieve(self , query :str,user_id :str, limit:int=5)->list[dict[str,Any]]:
        [vector] = self.embedder.embed([query])
        chunks = self.vector_store.search(vector ,limit,{"user_id": user_id})
        return chunks 