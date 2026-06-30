from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session, get_current_user
from app.shared.auth.auth_service import UserStub
from app.workspaces.vendor_intelligence import service, schemas

router = APIRouter()


@router.post("/verify", response_model=schemas.VendorCheckResponse)
async def verify_vendor(
    payload: schemas.GSTINVerificationRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserStub = Depends(get_current_user)
):
    """
    Submits a GSTIN to the Indian compliance audit pipeline.
    Saves verification audit details and returns results.
    """
    db_check = await service.verify_and_log_vendor(
        session=db,
        gstin=payload.gstin,
        user_id=current_user.id
    )
    # Commit database changes
    await db.commit()
    return db_check


@router.get("/", response_model=List[schemas.VendorCheckResponse])
async def list_vendor_audits(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserStub = Depends(get_current_user)
):
    """
    Lists audit logs of previous GSTIN verification checks.
    """
    return await service.get_vendor_checks_history(db)
