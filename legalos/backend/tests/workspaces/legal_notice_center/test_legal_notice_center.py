import pytest
from unittest.mock import AsyncMock, patch
from app.core.rag import chunker
from app.workspaces.legal_notice_center import service, repository
from app.workspaces.legal_notice_center.models import Notice, DraftReply


def test_notice_paragraph_chunking():
    """Verify that paragraph-based chunker splits by double newline and groups correctly."""
    notice_text = """
    This is paragraph one of the legal notice.
    It contains multiple sentences.
    
    This is paragraph two. It specifies a demand.
    
    This is paragraph three. It outlines consequences.
    """
    
    chunks = chunker.chunk_document(notice_text, strategy="paragraph")
    
    assert len(chunks) == 3
    assert chunks[0]["clause_index"] == 0
    assert "paragraph one" in chunks[0]["text"]
    assert "paragraph two" in chunks[1]["text"]
    assert "paragraph three" in chunks[2]["text"]


@pytest.mark.asyncio
@patch("app.workspaces.legal_notice_center.repository.get_notice_by_id")
@patch("app.core.rag.rag_pipeline.retrieve_and_generate")
@patch("app.workspaces.legal_notice_center.repository.add_draft_reply")
async def test_notice_reply_regeneration(
    mock_add_draft_reply,
    mock_retrieve_and_generate,
    mock_get_notice_by_id
):
    """Verify RAG regeneration calling logic."""
    mock_session = AsyncMock()
    notice_id = AsyncMock()
    document_id = AsyncMock()
    
    # 1. Setup mocks
    mock_notice = Notice(
        id=notice_id,
        document_id=document_id,
        raw_text="Notice content goes here.",
        notice_type="summons",
        urgency="critical"
    )
    mock_get_notice_by_id.return_value = mock_notice
    
    mock_retrieve_and_generate.return_value = '{"notice_type": "summons", "urgency": "critical", "reply_text": "Draft reply content."}'
    
    mock_draft = DraftReply(
        notice_id=notice_id,
        reply_text="Draft reply content."
    )
    mock_add_draft_reply.return_value = mock_draft

    # 2. Call service method
    result = await service.regenerate_reply(mock_session, notice_id)

    # 3. Assertions
    assert result.reply_text == "Draft reply content."
    mock_get_notice_by_id.assert_called_once_with(mock_session, notice_id)
    mock_retrieve_and_generate.assert_called_once()
    mock_add_draft_reply.assert_called_once_with(mock_session, notice_id, "Draft reply content.")
