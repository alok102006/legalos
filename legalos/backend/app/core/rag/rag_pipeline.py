import uuid
from typing import Dict, Any, List
from app.core.rag.document_parser import parse_document
from app.core.rag.chunker import chunk_document
from app.core.embeddings.embedder import get_embedder
from app.core.schemas.ai_io_schemas import ChunkRecord
from app.core.vectorstore import retrieval_service
from app.core.llm import llm_client

# Map workspaces to their respective vector collections
WORKSPACE_COLLECTIONS = {
    "contract_intelligence": "contract_clauses",
    "legal_notice_center": "legal_notices",
}

def ingest_document(
    file_bytes: bytes,
    filename: str,
    workspace: str,
    metadata: Dict[str, Any]
) -> str:
    """
    Coordinates document ingestion:
    1. Parse raw document (PDF, DOCX, TXT)
    2. Chunk the text into segments
    3. Generate vector embeddings for the chunks
    4. Upsert the embedded chunks with payloads to Qdrant
    
    Returns the generated document_id.
    """
    collection = WORKSPACE_COLLECTIONS.get(workspace)
    if not collection:
        raise ValueError(f"No vector collection mapped for workspace: '{workspace}'")
        
    # Generate document ID if not provided in metadata
    document_id = metadata.get("document_id", str(uuid.uuid4()))
    
    # 1. Parse
    text = parse_document(file_bytes, filename)
    if not text.strip():
        raise ValueError("Document text extraction returned empty content.")
        
    # 2. Chunk
    # Contracts use "clause" chunking, future modules may use different strategies
    chunk_strategy = "clause" if workspace == "contract_intelligence" else "paragraph"
    chunks = chunk_document(text, strategy=chunk_strategy)
    
    if not chunks:
        print(f"[RAG] Warning: No chunks generated for document '{filename}'")
        return document_id

    # 3. Embed
    embedder = get_embedder()
    chunk_texts = [c["text"] for c in chunks]
    vectors = embedder.embed(chunk_texts)
    
    # 4. Prepare ChunkRecords and Upsert
    records = []
    for i, chunk in enumerate(chunks):
        # Generate a unique point ID (UUID) for Qdrant
        point_id = str(uuid.uuid4())
        
        # Build vector payload
        payload = {
            "document_id": str(document_id),
            "clause_index": chunk["clause_index"],
            "text": chunk["text"],
            **{k: v for k, v in metadata.items() if k != "document_id"}
        }
        
        # Keep track of point_id on the chunk object for DB linking
        chunk["point_id"] = point_id
        
        records.append(
            ChunkRecord(
                id=point_id,
                vector=vectors[i],
                payload=payload
            )
        )
        
    retrieval_service.upsert_chunks(collection, records)
    
    # Store chunks reference on metadata or log it
    print(f"[RAG] Successfully ingested document '{filename}': {len(records)} points indexed in vector store.")
    
    # We return document_id along with the analyzed text chunks so the DB can match point_ids
    metadata["processed_chunks"] = chunks
    return document_id


def retrieve_and_generate(
    query: str,
    workspace: str,
    system_prompt: str,
    top_k: int = 5,
    filters: dict | None = None,
    json_mode: bool = False
) -> str:
    """
    Executes standard RAG lookup:
    1. Retrieval: Fetch nearest chunks from Qdrant
    2. Context construction
    3. Generation: Route to LLM wrapper
    """
    collection = WORKSPACE_COLLECTIONS.get(workspace)
    if not collection:
        raise ValueError(f"No vector collection mapped for workspace: '{workspace}'")
        
    # 1. Retrieve
    print(f"[RAG] Searching top_{top_k} for query='{query}' in collection='{collection}' filters={filters}...")
    retrieved = retrieval_service.search(
        collection=collection,
        query=query,
        top_k=top_k,
        filters=filters
    )
    
    # 2. Build Context
    if not retrieved:
        print("[RAG] No context retrieved. Running LLM call without context.")
        context = "No reference text available."
    else:
        context_blocks = []
        for idx, chunk in enumerate(retrieved):
            text_snippet = chunk.payload.get("text", "")
            clause_idx = chunk.payload.get("clause_index", "N/A")
            context_blocks.append(f"--- Chunk {idx + 1} (Clause Index: {clause_idx}) ---\n{text_snippet}")
        context = "\n\n".join(context_blocks)
        
    # 3. Construct Prompt
    user_prompt = (
        f"Use the following legal context to address the query.\n"
        f"If the answer cannot be determined from the context, formulate the best legal reply based on the context rules.\n\n"
        f"### Legal Context:\n"
        f"{context}\n\n"
        f"### User Query:\n"
        f"{query}\n\n"
        f"Answer:"
    )
    
    # 4. Generate
    return llm_client.generate(
        prompt=user_prompt,
        system=system_prompt,
        json_mode=json_mode,
        workspace=workspace
    )
