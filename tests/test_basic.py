"""
Basic Tests for WhatsPayAI Application Structure
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_imports():
    """Test that all main modules can be imported."""
    try:
        from src import app
        from src import intent
        from src import twilio_client
        from src import hathor_client
        from src import scheduler
        from src.handlers import ai_query, balance, help, payment
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_app_creation():
    """Test that FastAPI app can be created."""
    from src.app import app
    assert app is not None
    assert hasattr(app, 'title')


def test_state_variables():
    """Test that state variables are accessible."""
    from src.app import balances, usage_logs, deposit_queue
    
    assert isinstance(balances, dict)
    assert isinstance(usage_logs, dict)
    assert isinstance(deposit_queue, dict)


class TestBasicFunctionality:
    """Test basic functionality without external dependencies."""
    
    def test_intent_classification_keywords(self):
        """Test keyword-based intent classification."""
        from src.intent import classify_with_keywords
        
        assert classify_with_keywords("top up 1 HTR") == "payment_intent"
        assert classify_with_keywords("what's my balance") == "balance_intent"
        assert classify_with_keywords("help me") == "help_intent"
        assert classify_with_keywords("random question") == "ai_query_intent"
    
    def test_phone_number_validation(self):
        """Test phone number validation."""
        from src.twilio_client import validate_phone_number
        
        assert validate_phone_number("+1234567890") == "+1234567890"
        assert validate_phone_number("whatsapp:+1234567890") == "+1234567890"
        assert validate_phone_number("invalid") is None
    
    def test_hathor_address_validation(self):
        """Test Hathor address validation."""
        from src.hathor_client import validate_hathor_address
        
        # Mock testnet environment
        with pytest.MonkeyPatch.context() as m:
            m.setattr("src.hathor_client.HATHOR_NETWORK", "testnet")
            assert validate_hathor_address("WYBwT1234567890abcdef1234567890") is True
            assert validate_hathor_address("invalid") is False
    
    def test_token_estimation(self):
        """Test token count estimation."""
        from src.handlers.ai_query import count_tokens_estimate
        
        assert count_tokens_estimate("Hello world") > 0
        assert count_tokens_estimate("") == 1  # Minimum 1 token
    
    def test_cost_calculation(self):
        """Test cost calculation."""
        from src.handlers.balance import calculate_cost_estimate
        
        assert calculate_cost_estimate(100) == 0.01
        assert calculate_cost_estimate(200) == 0.02
