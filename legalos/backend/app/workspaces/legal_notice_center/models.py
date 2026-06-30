import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.db.base import Base
from app.shared.db.mixins import UUIDPrimaryKeyMixin


class Notice(Base, UUIDPrimaryKeyMixin):
    """Representing an ingested Legal Notice."""
    __tablename__ = "notices"
    __table_args__ = {"schema": "legal_notice_center"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.documents.id", ondelete="SET NULL"),
        nullable=True
    )
    raw_text: Mapped[str] = mapped_column(String, nullable=False)
    notice_type: Mapped[str] = mapped_column(
        String,
        nullable=True  # 'demand' | 'show_cause' | 'summons' | 'other'
    )
    urgency: Mapped[str] = mapped_column(
        String,
        nullable=True  # 'low' | 'medium' | 'high' | 'critical'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    # Relationships
    document = relationship("Document")
    replies: Mapped[list["DraftReply"]] = relationship(
        "DraftReply",
        back_populates="notice",
        cascade="all, delete-orphan"
    )


class DraftReply(Base, UUIDPrimaryKeyMixin):
    """Representing a generated reply draft letter for a notice."""
    __tablename__ = "draft_replies"
    __table_args__ = {"schema": "legal_notice_center"}

    notice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("legal_notice_center.notices.id", ondelete="CASCADE"),
        nullable=False
    )
    reply_text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    # Relationships
    notice: Mapped[Notice] = relationship("Notice", back_populates="replies")
