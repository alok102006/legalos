import pytest
from app.core.rag import chunker, document_parser
from app.shared.exceptions import BadRequestException


def test_contract_chunking():
    """Verify that clause-based chunking identifies numbered headers properly."""
    agreement_text = """
    NON-DISCLOSURE AGREEMENT
    
    1. DEFINITIONS
    Confidential Information means all trade secrets and business materials.
    
    2. OBLIGATIONS
    The receiving party shall keep the information strictly confidential.
    
    3. PENALTIES
    If a breach occurs, the breaching party shall pay INR 5,00,000 as liquidated damages.
    """
    
    clauses = chunker.chunk_document(agreement_text, strategy="clause")
    
    assert len(clauses) >= 3
    assert clauses[0]["clause_index"] == 0
    assert "DEFINITIONS" in clauses[1]["text"]
    assert "OBLIGATIONS" in clauses[2]["text"]
    assert "PENALTIES" in clauses[3]["text"]


def test_parser_unsupported_extension():
    """Assert parser raises BadRequestException on invalid formats."""
    with pytest.raises(BadRequestException) as exc_info:
        document_parser.parse_document(b"dummy code content", "exploit.exe")
        
    assert "Unsupported file type" in str(exc_info.value.detail)


def test_parser_txt_content():
    """Verify plain text files parse cleanly."""
    txt_content = b"Sample plain text legal notice payload."
    parsed = document_parser.parse_document(txt_content, "notice.txt")
    assert parsed == "Sample plain text legal notice payload."
