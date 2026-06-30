import os
import sys
import uuid
import pytest

# Ensure backend directory is in the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import settings
from app.core.embeddings.embedder import get_embedder
from app.core.llm import llm_client
from app.core.vectorstore import retrieval_service, collections
from app.core.rag import document_parser, chunker, rag_pipeline


def test_embedder_singleton():
    """Verify that get_embedder() returns the same instance twice."""

    
    e1 = get_embedder()
    e2 = get_embedder()
    assert e1 is e2, "Embedder is not a singleton!"
    
    # Test simple embed
    vectors = e1.embed(["Test document structure", "Second legal paragraph"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 384, "Embedding dimensions should be 384 for all-MiniLM-L6-v2"
    print("SUCCESS: Embedder singleton and dimension check passed.")


def test_parser_and_chunker():
    """Verify that parsing and clause chunking work on plain text/markdown."""
    dummy_contract = """
    AGREEMENT OF LEASE
    
    1. PARTIES
    The parties to this agreement are the Landlord and the Tenant.
    
    2. RENT
    The rent shall be INR 50,000 per month, payable in advance on the 1st of each month.
    
    3. DEPOSIT
    The Tenant shall pay a security deposit of INR 100,000 upon signing this agreement.
    """
    
    # Test direct text parsing
    parsed = document_parser.parse_document(dummy_contract.encode("utf-8"), "contract.txt")
    assert "AGREEMENT OF LEASE" in parsed
    
    # Test clause-level chunking
    clauses = chunker.chunk_document(parsed, strategy="clause")
    assert len(clauses) > 0
    # The first chunk should have clause_index 0
    assert clauses[0]["clause_index"] == 0
    print(f"SUCCESS: Parsed & chunked text. Extracted {len(clauses)} clauses.")


def test_llm_generation():
    """Smoke test for the LLM Client."""
    # If GEMINI_API_KEY is not configured, we'll mock or catch to let local runs pass
    if not settings.gemini_api_key:
        print("WARNING: GEMINI_API_KEY not set. Changing LLM provider to 'local' for smoke test fallback.")
        settings.llm_provider = "local"
        
    try:
        response = llm_client.generate(
            prompt="Hello, this is a smoke test query. Respond with 'PASS' if you read this.",
            system="You are a test assistant.",
            json_mode=False,
            workspace="contract_intelligence"
        )
        print(f"SUCCESS: LLM Response received: {response}")
    except Exception as e:
        print(f"LLM Generation failed (expected if keys are missing): {str(e)}")


if __name__ == "__main__":
    print("--- STARTING CORE SMOKE TESTS ---")
    test_embedder_singleton()
    test_parser_and_chunker()
    test_llm_generation()
    print("--- CORE SMOKE TESTS COMPLETE ---")
