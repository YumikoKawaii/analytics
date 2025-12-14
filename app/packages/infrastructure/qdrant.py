from qdrant_client import QdrantClient
from app.config import settings

qdrant_client = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
    api_key=settings.qdrant_api_key,
    timeout=60,
)
