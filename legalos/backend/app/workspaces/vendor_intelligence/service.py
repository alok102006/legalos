import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.workspaces.vendor_intelligence import repository
from app.workspaces.vendor_intelligence.models import VendorCheck
from app.workspaces.vendor_intelligence.mocks.gstin_mock import VendorVerificationProvider


async def verify_and_log_vendor(
    session: AsyncSession,
    gstin: str,
    user_id: uuid.UUID
) -> VendorCheck:
    """
    Triggers GSTIN verification via mock provider, log audits, and persists results.
    """
    # 1. Fetch mock response details
    raw_response = VendorVerificationProvider.verify_gstin(gstin)
    
    # 2. Persist audit trail to Postgres
    db_check = await repository.create_vendor_check(
        session=session,
        gstin=raw_response["gstin"],
        company_name=raw_response["company_name"],
        is_valid=raw_response["is_valid"],
        registration_date=raw_response["registration_date"],
        trust_score=raw_response["trust_score"],
        fraud_flagged=raw_response["fraud_flagged"],
        raw_mock_response=raw_response,
        checked_by=user_id
    )
    
    return db_check


async def get_vendor_checks_history(
    session: AsyncSession
) -> List[VendorCheck]:
    """
    Retrieves full listing of prior GSTIN audits.
    """
    return await repository.list_vendor_checks(session)
