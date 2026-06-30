import pytest
from unittest.mock import AsyncMock
from app.workspaces.vendor_intelligence.mocks.gstin_mock import VendorVerificationProvider
from app.workspaces.vendor_intelligence import service, repository


def test_gstin_mock_provider_fraud_detection():
    """Verify that gstin_mock identifies fraud-flagged GSTINs correctly."""
    # Apex Shell Logistics check
    res_fraud_1 = VendorVerificationProvider.verify_gstin("27AAAAA1111A1Z1")
    assert res_fraud_1["fraud_flagged"] is True
    assert res_fraud_1["is_valid"] is False
    assert "circular trading" in res_fraud_1["reason"]

    # Karnavati Steel check
    res_fraud_2 = VendorVerificationProvider.verify_gstin("27BBBBB2222B2Z2")
    assert res_fraud_2["fraud_flagged"] is True
    assert res_fraud_2["is_valid"] is True
    assert res_fraud_2["trust_score"] < 30


def test_gstin_mock_provider_standard_validation():
    """Verify standard GSTIN mock generation rules."""
    # Invalid length GSTIN
    res_invalid = VendorVerificationProvider.verify_gstin("12345")
    assert res_invalid["is_valid"] is False
    assert res_invalid["trust_score"] == 0

    # Normal valid lookup
    res_valid = VendorVerificationProvider.verify_gstin("27ABCDE1234F1Z5")
    assert res_valid["is_valid"] is True
    assert res_valid["fraud_flagged"] is False
    assert 40 <= res_valid["trust_score"] <= 95
    assert "Vardhaman Ind-Commercial" in res_valid["company_name"]


@pytest.mark.asyncio
async def test_vendor_service_logging():
    """Verify that service correctly routes verify requests and invokes db repository logs."""
    # Mock database session
    mock_session = AsyncMock()
    
    # Mock user_id and gstin
    user_id = AsyncMock()
    gstin = "27AAAAA1111A1Z1"

    # Call service
    result = await service.verify_and_log_vendor(
        session=mock_session,
        gstin=gstin,
        user_id=user_id
    )

    # Verify that add was called in session
    assert mock_session.add.call_count == 1
    assert result.gstin == gstin
    assert result.fraud_flagged is True
    assert result.company_name == "Apex Shell Logistics Pvt Ltd"
