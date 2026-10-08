from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProvider(ABC):

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a list of text chunks into embedding vectors.

        Input:
            texts: List of strings to embed.

        Returns:
            One embedding vector per input string.
        """
        pass





class VectorStore(ABC):

    @abstractmethod
    def upsert(
        self,
        chunks: list[dict[str, Any]],
    ) -> None:
        pass

    @abstractmethod
    def search(
        self,
        vector: list[float],
        limit: int = 5 ,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        pass