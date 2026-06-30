import uuid
from typing import Optional
from pydantic import BaseModel


class UserStub(BaseModel):
    id: uuid.UUID
    full_name: str
    role: str  # 'business_owner', 'ca', 'legal_reviewer'


# Mock users mapped by role keys
MOCK_USERS = {
    "owner": UserStub(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        full_name="Rajesh Kumar",
        role="business_owner"
    ),
    "ca": UserStub(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        full_name="Anjali Sharma",
        role="ca"
    ),
    "reviewer": UserStub(
        id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        full_name="Vikram Mehta",
        role="legal_reviewer"
    )
}

def get_user_by_role(role: str) -> Optional[UserStub]:
    """Helper to fetch a mock user based on the selected role switch."""
    role_key = role.lower().strip()
    return MOCK_USERS.get(role_key, MOCK_USERS["owner"])
