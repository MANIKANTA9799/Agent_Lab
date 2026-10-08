from packages.rag.interfaces import EmbeddingProvider
from packages.config.settings import settings
import requests
class OllamaEmbeddingProvider(EmbeddingProvider):
     def embed(self, texts: list[str]) -> list[list[float]]:
          url = f"{settings.ollama_base_url}/api/embed"
          try:
            response = requests.post(
                url,
                json={
                    "model": settings.embedding_model,
                    "input": texts,
                },
                timeout=60,
            )
            response.raise_for_status()
          except requests.RequestException as e:
            raise RuntimeError(
                f"Failed to generate embeddings using Ollama: {e}"
            ) from e

          data = response.json()
          return data["embeddings"]
