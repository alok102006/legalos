import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.shared.db.base import Base
from app.shared.db.mixins import UUIDPrimaryKeyMixin


class Contract(Base, UUIDPrimaryKeyMixin):
    """Contract intelligence Contract representation."""
    __tablename__ = "contracts"
    __table_args__ = {"schema": "contract_intelligence"}

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    title: Mapped[str] = mapped_column(String, nullable=True)
    counterparty_name: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        server_default="processing"  # 'processing' | 'analyzed' | 'failed'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="contract")
    clauses: Mapped[list["Clause"]] = relationship(
        "Clause",
        back_populates="contract",
        cascade="all, delete-orphan",
        order_by="Clause.clause_index"
    )


class Clause(Base, UUIDPrimaryKeyMixin):
    """Contract intelligence Clause representation."""
    __tablename__ = "clauses"
    __table_args__ = {"schema": "contract_intelligence"}

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contract_intelligence.contracts.id", ondelete="CASCADE"),
        nullable=False
    )
    clause_index: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_text: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=True)
    risk_type: Mapped[str] = mapped_column(
        String,
        nullable=True,
        server_default="none"  # 'penalty' | 'lock_in' | 'indemnity' | 'termination' | 'none'
    )
    risk_score: Mapped[int] = mapped_column(Integer, nullable=True)  # 0 to 100
    qdrant_point_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    # Relationships
    contract: Mapped[Contract] = relationship("Contract", back_populates="clauses")
    suggestions: Mapped[list["NegotiationSuggestion"]] = relationship(
        "NegotiationSuggestion",
        back_populates="clause",
        cascade="all, delete-orphan"
    )


class NegotiationSuggestion(Base, UUIDPrimaryKeyMixin):
    """Contract negotiation suggestion."""
    __tablename__ = "negotiation_suggestions"
    __table_args__ = {"schema": "contract_intelligence"}

    clause_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contract_intelligence.clauses.id", ondelete="CASCADE"),
        nullable=False
    )
    suggestion_text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    # Relationships
    clause: Mapped[Clause] = relationship("Clause", back_populates="suggestions")
