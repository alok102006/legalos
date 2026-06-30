import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class GSTINVerificationRequest(BaseModel):
    gstin: str = Field(..., min_length=15, max_length=15, description="15-character Indian GSTIN number.")


class VendorCheckResponse(BaseModel):
    id: uuid.UUID
    gstin: str
    company_name: Optional[str] = None
    is_valid: Optional[bool] = None
    registration_date: Optional[date] = None
    trust_score: Optional[int] = None
    fraud_flagged: bool
    raw_mock_response: Optional[Dict[str, Any]] = None
    checked_by: Optional[uuid.UUID] = None
    checked_at: datetime

    model_config = {"from_attributes": True}
