from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import get_settings

COLLECTION = "jarvis_memories"


class MemoryVectorStore:
    def __init__(self, dimensions: int) -> None:
        self.client = QdrantClient(url=get_settings().qdrant_url)
        self.dimensions = dimensions

    def ensure_collection(self) -> None:
        if not self.client.collection_exists(COLLECTION):
            self.client.create_collection(COLLECTION, vectors_config=VectorParams(size=self.dimensions, distance=Distance.COSINE))

    def upsert(self, memory_id: UUID, user_id: UUID, vector: list[float]) -> None:
        self.ensure_collection()
        self.client.upsert(COLLECTION, [PointStruct(id=str(memory_id), vector=vector, payload={"user_id": str(user_id)})])

    def delete(self, memory_id: UUID) -> None:
        self.client.delete(COLLECTION, points_selector=[str(memory_id)])
