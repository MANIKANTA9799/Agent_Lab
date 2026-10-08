

from typing import Any
from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        chunks: list[dict[str, Any]],
        top_k: int = 3,
    ) -> list[dict[str, Any]]:

        pairs = []

        for chunk in chunks:
         text = chunk["payload"]["text"]
         pair = (query, text)
         pairs.append(pair)

        scores = self.model.predict(pairs)

        for chunk, score in zip(chunks, scores):
            chunk["rerank_score"] = float(score)

        chunks.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return chunks[:top_k]