from typing import Any

from qdrant_client import QdrantClient, models

from packages.rag.interfaces import VectorStore


class QdrantVectorStore(VectorStore):

    def __init__(self):
        self.client = QdrantClient(path="./qdrant_data")
        self.collection_name = "research_chunks"

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=768,
                    distance=models.Distance.COSINE,
                ),
            )
    def clear(self) -> None:
     self.client.delete_collection(
        collection_name=self.collection_name
    )

     self.client.create_collection(
        collection_name=self.collection_name,
        vectors_config=models.VectorParams(
            size=768,
            distance=models.Distance.COSINE,
        ),
    )
    def upsert(self, chunks: list[dict[str, Any]]) -> None:
        points = [
            models.PointStruct(
                id=chunk["id"],
                vector=chunk["vector"],
                payload=chunk["payload"],
            )
            for chunk in chunks
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(
    self,
    vector: list[float],
    limit: int = 5,
    filters: dict[str, Any] | None = None,
     ) -> list[dict[str, Any]]:

        query_filter = None

        if filters:
            conditions = [
                models.FieldCondition(
                    key=k,
                    match=models.MatchValue(value=v),
                )
                for k, v in filters.items()
            ]

            query_filter = models.Filter(
                must=conditions #type:ignore 
            )

        results = self.client.query_points(
    collection_name=self.collection_name,
    query=vector,
    query_filter=query_filter,
    limit=limit,
)

        return [
        {
            "id": result.id,
            "score": result.score,
            "payload": result.payload,
        }
        for result in results.points
    ]

        