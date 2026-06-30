import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional


class DraftReplySchema(BaseModel):
    id: uuid.UUID
    notice_id: uuid.UUID
    reply_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NoticeSummarySchema(BaseModel):
    id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    notice_type: Optional[str] = None
    urgency: Optional[str] = None
    created_at: datetime
    original_filename: Optional[str] = None

    model_config = {"from_attributes": True}


class NoticeDetailSchema(BaseModel):
    id: uuid.UUID
    document_id: Optional[uuid.UUID] = None
    raw_text: str
    notice_type: Optional[str] = None
    urgency: Optional[str] = None
    created_at: datetime
    replies: List[DraftReplySchema] = []

    model_config = {"from_attributes": True}


# Schema for structural parsing of AI responses
class LegalNoticeAIResponse(BaseModel):
    notice_type: str = Field(description="Must be one of: 'demand', 'show_cause', 'summons', 'other'")
    urgency: str = Field(description="Must be one of: 'low', 'medium', 'high', 'critical'")
    reply_text: str = Field(description="The full draft reply letter text.")
