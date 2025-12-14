from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.packages.infrastructure.qdrant import qdrant_client
from app.config import settings
import numpy as np
from typing import Optional


class QdrantVectorStore:
    client: QdrantClient
    collection_name: str

    def __init__(self, collection_name: Optional[str] = None):
        self.client = qdrant_client
        self.collection_name = collection_name or settings.qdrant_collection_name
        self._ensure_collection_exists()

    def _ensure_collection_exists(self, vector_size: int = 384) -> None:
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if self.collection_name not in collection_names:
                print(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                print(f"Collection {self.collection_name} created successfully")
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
            raise

    def recreate_collection(self, vector_size: int = 384) -> None:
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Collection might not exist: {e}")

        self._ensure_collection_exists(vector_size=vector_size)

    def add_documents(
            self,
            file_id: str,
            chunks: list[str],
            embeddings: np.ndarray,
    ) -> dict:
        if len(chunks) != len(embeddings):
            raise ValueError(f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})")

        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=hash(f"{file_id}_{idx}") % (10 ** 12),
                vector=embedding.tolist(),
                payload={
                    "file_id": file_id,
                    "chunk_index": idx,
                    "text": chunk,
                    "chunk_length": len(chunk),
                }
            )
            points.append(point)

        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

        return {
            "status": operation_info.status,
            "file_id": file_id,
            "num_chunks": len(chunks),
        }

    def search(
            self,
            query_embedding: np.ndarray,
            limit: int = 5,
            file_id: Optional[str] = None,
            score_threshold: Optional[float] = None,
    ) -> list[dict]:
        search_filter = None
        if file_id:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="file_id",
                        match=MatchValue(value=file_id),
                    )
                ]
            )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=limit,
            query_filter=search_filter,
            score_threshold=score_threshold,
        )

        return [
            {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text"),
                "file_id": result.payload.get("file_id"),
                "chunk_index": result.payload.get("chunk_index"),
            }
            for result in results
        ]

    def delete_by_file_id(self, file_id: str) -> dict:
        """Delete all chunks for a specific file."""
        from qdrant_client.models import FilterSelector

        result = self.client.delete(
            collection_name=self.collection_name,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="file_id",
                            match=MatchValue(value=file_id),
                        )
                    ]
                )
            ),
        )

        return {
            "status": result.status,
            "file_id": file_id,
        }

    def get_collection_info(self) -> dict:
        """Get information about the collection."""
        info = self.client.get_collection(collection_name=self.collection_name)
        return {
            "collection_name": self.collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
        }


qdrant_store = QdrantVectorStore()
