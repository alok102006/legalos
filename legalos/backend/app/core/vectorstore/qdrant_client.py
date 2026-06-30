from qdrant_client import QdrantClient
from app.config import settings

_qdrant_client_instance = None

def get_qdrant_client() -> QdrantClient:
    """Singleton getter for Qdrant client."""
    global _qdrant_client_instance
    if _qdrant_client_instance is None:
        print(f"[QDRANT] Connecting to server at {settings.qdrant_url}...")
        _qdrant_client_instance = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
    return _qdrant_client_instance
