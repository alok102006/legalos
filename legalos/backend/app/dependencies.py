from typing import Optional
from fastapi import Header, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.db.session import get_db_session
from app.shared.auth import auth_service
from app.shared.auth.auth_service import UserStub


async def get_current_user(
    x_user_role: Optional[str] = Header(None),
    role: Optional[str] = Query(None)
) -> UserStub:
    """
    Dependency to resolve the current active user stub.
    Checks 'X-User-Role' header first, then 'role' query parameter.
    Defaults to 'owner' profile if none provided.
    """
    resolved_role = x_user_role or role or "owner"
    user = auth_service.get_user_by_role(resolved_role)
    return user
