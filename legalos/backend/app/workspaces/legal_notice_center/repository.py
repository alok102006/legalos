import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.shared.db.models import Document
from app.workspaces.legal_notice_center.models import Notice, DraftReply


async def create_document(
    session: AsyncSession,
    workspace: str,
    original_filename: str,
    storage_path: str,
    uploaded_by: Optional[uuid.UUID] = None
) -> Document:
    """Inserts an uploaded document record in the core schema."""
    doc = Document(
        workspace=workspace,
        original_filename=original_filename,
        storage_path=storage_path,
        uploaded_by=uploaded_by
    )
    session.add(doc)
    await session.flush()
    return doc


async def create_notice(
    session: AsyncSession,
    document_id: Optional[uuid.UUID],
    raw_text: str,
    notice_type: Optional[str] = None,
    urgency: Optional[str] = None
) -> Notice:
    """Inserts a new notice metadata entry."""
    notice = Notice(
        document_id=document_id,
        raw_text=raw_text,
        notice_type=notice_type,
        urgency=urgency
    )
    session.add(notice)
    await session.flush()
    return notice


async def get_notice_by_id(
    session: AsyncSession,
    notice_id: uuid.UUID
) -> Optional[Notice]:
    """Retrieves notice details including all generated draft replies."""
    stmt = (
        select(Notice)
        .where(Notice.id == notice_id)
        .options(selectinload(Notice.replies))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_notices_with_filenames(
    session: AsyncSession
) -> List[dict]:
    """Retrieves all notice audit trails, joining core.documents to get names."""
    stmt = (
        select(Notice, Document.original_filename)
        .outerjoin(Document, Notice.document_id == Document.id)
        .order_by(Notice.created_at.desc())
    )
    result = await session.execute(stmt)
    rows = result.all()

    notices_list = []
    for notice, filename in rows:
        notices_list.append({
            "id": notice.id,
            "document_id": notice.document_id,
            "notice_type": notice.notice_type,
            "urgency": notice.urgency,
            "created_at": notice.created_at,
            "original_filename": filename or "Pasted Notice Text"
        })
    return notices_list


async def add_draft_reply(
    session: AsyncSession,
    notice_id: uuid.UUID,
    reply_text: str
) -> DraftReply:
    """Appends an AI-generated reply draft to the notice history."""
    draft = DraftReply(
        notice_id=notice_id,
        reply_text=reply_text
    )
    session.add(draft)
    await session.flush()
    return draft
