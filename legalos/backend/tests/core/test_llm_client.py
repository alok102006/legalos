import pytest
from unittest.mock import patch, MagicMock
from app.core.llm import llm_client
from app.config import settings

def test_llm_routing_gemini():
    """Verify routing logic switches providers correctly."""
    settings.llm_provider = "gemini"
    
    # Mock gemini generate call
    with patch("app.core.llm.llm_client.generate_gemini") as mock_gemini:
        mock_gemini.return_value = "Mocked Gemini Response"
        
        res = llm_client.generate(
            prompt="Hello", 
            system="Test system", 
            json_mode=False, 
            workspace="contract_intelligence"
        )
        
        assert res == "Mocked Gemini Response"
        mock_gemini.assert_called_once_with("Hello", system="Test system", json_mode=False)


def test_llm_routing_local():
    """Verify routing to local provider."""
    settings.llm_provider = "local"
    
    with patch("app.core.llm.llm_client.generate_local") as mock_local:
        mock_local.return_value = "Mocked Local Response"
        
        res = llm_client.generate(
            prompt="Hello Local", 
            system="Test system local", 
            json_mode=True, 
            workspace="contract_intelligence"
        )
        
        assert res == "Mocked Local Response"
        mock_local.assert_called_once_with("Hello Local", system="Test system local", json_mode=True)
