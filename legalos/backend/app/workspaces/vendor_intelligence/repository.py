import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workspaces.vendor_intelligence.models import VendorCheck


async def create_vendor_check(
    session: AsyncSession,
    gstin: str,
    company_name: Optional[str],
    is_valid: Optional[bool],
    registration_date: Optional[str],
    trust_score: Optional[int],
    fraud_flagged: bool,
    raw_mock_response: dict,
    checked_by: Optional[uuid.UUID] = None
) -> VendorCheck:
    """Saves a new GSTIN check audit log to the database."""
    # Convert date string if present
    parsed_date = None
    if registration_date:
        from datetime import datetime
        try:
            parsed_date = datetime.strptime(registration_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    db_check = VendorCheck(
        gstin=gstin,
        company_name=company_name,
        is_valid=is_valid,
        registration_date=parsed_date,
        trust_score=trust_score,
        fraud_flagged=fraud_flagged,
        raw_mock_response=raw_mock_response,
        checked_by=checked_by
    )
    
    session.add(db_check)
    await session.flush()
    return db_check


async def list_vendor_checks(
    session: AsyncSession,
    limit: int = 50
) -> List[VendorCheck]:
    """Retrieves list of previous GSTIN verification checks, ordered by check timestamp."""
    stmt = (
        select(VendorCheck)
        .order_by(VendorCheck.checked_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
