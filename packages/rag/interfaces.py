from abc import ABC, abstractmethod


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