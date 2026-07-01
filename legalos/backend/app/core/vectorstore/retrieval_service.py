from qdrant_client.http import models as qmodels
from app.core.schemas.ai_io_schemas import ChunkRecord, RetrievedChunk
from app.core.vectorstore.qdrant_client import get_qdrant_client
from app.core.embeddings.embedder import get_embedder


def upsert_chunks(collection: str, items: list[ChunkRecord]) -> None:
    """Upserts embedded document chunks to a Qdrant collection."""
    if not items:
        return
        
    client = get_qdrant_client()
    
    points = [
        qmodels.PointStruct(
            id=item.id,
            vector=item.vector,
            payload=item.payload
        )
        for item in items
    ]
    
    client.upsert(
        collection_name=collection,
        points=points,
        wait=True
    )
    print(f"[QDRANT] Upserted {len(items)} chunks to collection '{collection}'.")


def search(
    collection: str,
    query: str,
    top_k: int = 5,
    filters: dict | None = None
) -> list[RetrievedChunk]:
    """
    Performs semantic search against Qdrant.
    Generates embedding for query text internally using the embedder singleton.
    """
    client = get_qdrant_client()
    embedder = get_embedder()
    
    # Generate search vector
    query_vector = embedder.embed([query])[0]
    
    # Parse payload filters
    q_filter = None
    if filters:
        must_conditions = []
        for key, val in filters.items():
            must_conditions.append(
                qmodels.FieldCondition(
                    key=key,
                    match=qmodels.MatchValue(value=val)
                )
            )
        q_filter = qmodels.Filter(must=must_conditions)
        
    results = client.query_points(
        collection_name=collection,
        query=query_vector,
        query_filter=q_filter,
        limit=top_k
    )
    
    return [
        RetrievedChunk(
            id=str(r.id),
            score=r.score,
            payload=r.payload or {}
        )
        for r in results.points
    ]


def delete_by_document(collection: str, document_id: str) -> None:
    """Deletes all vector points associated with a specific document_id."""
    client = get_qdrant_client()
    
    client.delete(
        collection_name=collection,
        points_selector=qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchValue(value=str(document_id))
                )
            ]
        )
    )
    print(f"[QDRANT] Deleted points for document_id '{document_id}' in '{collection}'.")
