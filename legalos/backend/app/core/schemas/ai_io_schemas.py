from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChunkRecord(BaseModel):
    """Schema for upserting vector chunks."""
    id: str  # String representation of UUID
    vector: List[float]
    payload: Dict[str, Any]


class RetrievedChunk(BaseModel):
    """Schema for search results."""
    id: str
    score: float
    payload: Dict[str, Any]
