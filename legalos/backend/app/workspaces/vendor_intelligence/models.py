import uuid
from datetime import datetime, date
from sqlalchemy import String, ForeignKey, DateTime, Date, Integer, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.shared.db.base import Base
from app.shared.db.mixins import UUIDPrimaryKeyMixin


class VendorCheck(Base, UUIDPrimaryKeyMixin):
    """Auditing and tracking record for GSTIN verification checks."""
    __tablename__ = "vendor_checks"
    __table_args__ = {"schema": "vendor_intelligence"}

    gstin: Mapped[str] = mapped_column(String, nullable=False)
    company_name: Mapped[str] = mapped_column(String, nullable=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=True)
    registration_date: Mapped[date] = mapped_column(Date, nullable=True)
    trust_score: Mapped[int] = mapped_column(Integer, nullable=True)
    fraud_flagged: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
        default=False,
        nullable=True
    )
    raw_mock_response: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    checked_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.users.id", ondelete="SET NULL"),
        nullable=True
    )
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )
