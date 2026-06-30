import random
from typing import Dict, Any

# Hardcoded demo GSTIN triggers for fraud flags
FRAUD_GSTINS = {
    "27AAAAA1111A1Z1": {
        "company_name": "Apex Shell Logistics Pvt Ltd",
        "is_valid": False,
        "registration_date": "2023-01-15",
        "trust_score": 8,
        "fraud_flagged": True,
        "reason": "Entity flagged by GST Network (GSTN) as a high-risk dummy firm used for circular trading and ITC tax credit evasion."
    },
    "27BBBBB2222B2Z2": {
        "company_name": "Karnavati Steel Trading",
        "is_valid": True,
        "registration_date": "2020-06-18",
        "trust_score": 29,
        "fraud_flagged": True,
        "reason": "Multiple compliance delay notices served. Substituted active PAN holder with blacklisted directors."
    }
}

class VendorVerificationProvider:
    """Mock verification client for Indian GSTIN compliance audit."""

    @staticmethod
    def verify_gstin(gstin: str) -> Dict[str, Any]:
        """
        # MOCKED — replace with real GSTIN verification API integration
        Simulates call to a government GSTIN registry.
        """
        # Cleanup input
        clean_gstin = gstin.upper().strip()

        # 1. Check if it's one of the deterministic fraud triggers
        if clean_gstin in FRAUD_GSTINS:
            payload = FRAUD_GSTINS[clean_gstin]
            return {
                "gstin": clean_gstin,
                "company_name": payload["company_name"],
                "is_valid": payload["is_valid"],
                "registration_date": payload["registration_date"],
                "trust_score": payload["trust_score"],
                "fraud_flagged": payload["fraud_flagged"],
                "reason": payload["reason"]
            }

        # 2. Validate format (India GSTIN is exactly 15 characters long)
        if len(clean_gstin) != 15:
            return {
                "gstin": clean_gstin,
                "company_name": "Unknown Entity",
                "is_valid": False,
                "registration_date": None,
                "trust_score": 0,
                "fraud_flagged": False,
                "reason": "Invalid GSTIN format. Must be exactly 15 characters."
            }

        # 3. Standard successful lookup mock generator
        # Trust score for unrecognized (but format-valid) GSTINs: random.randint(40, 95)
        trust_score = random.randint(40, 95)
        
        # Determine company name based on a portion of the GSTIN (PAN part) for demo consistency
        pan_slug = clean_gstin[2:7]
        company_name = f"Vardhaman Ind-Commercial {pan_slug} Corp"
        
        return {
            "gstin": clean_gstin,
            "company_name": company_name,
            "is_valid": True,
            "registration_date": "2019-11-20",
            "trust_score": trust_score,
            "fraud_flagged": False,
            "reason": "Entity verified successfully with active status."
        }
