"""
Test Configuration and Fixtures

Common test utilities and fixtures for WhatsPayAI tests.
"""

import json
import os
import tempfile
from unittest.mock import AsyncMock, Mock

import pytest

# Load test environment
os.environ.setdefault("TWILIO_SID", "test_sid")
os.environ.setdefault("TWILIO_TOKEN", "test_token")
os.environ.setdefault("TWILIO_WHATSAPP_NUMBER", "whatsapp:+1234567890")
os.environ.setdefault("OPENAI_API_KEY", "test_openai_key")
os.environ.setdefault("HATHOR_NETWORK", "testnet")
os.environ.setdefault("HATHOR_NODE_URL", "https://node1.testnet.hathor.network")
os.environ.setdefault("HATHOR_WALLET_SEED", "test_seed_phrase")
os.environ.setdefault("DEBUG", "true")


@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses."""
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="This is a mock AI response."))]
    return mock_response


@pytest.fixture
def mock_twilio_client():
    """Mock Twilio client."""
    mock_client = Mock()
    mock_message = Mock()
    mock_message.sid = "mock_message_sid"
    mock_client.messages.create.return_value = mock_message
    return mock_client


@pytest.fixture
def mock_hathor_client():
    """Mock Hathor client."""
    mock_client = Mock()
    mock_client.get_address_info.return_value = {
        "success": True,
        "total_amount_received": 100,  # 1 HTR in centis
    }
    mock_client.get_address_history.return_value = {"success": True, "history": []}
    return mock_client


@pytest.fixture
def temp_state_file():
    """Create temporary state file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "balances": {"test_user": 1.0},
                "usage_logs": {"test_user": []},
                "deposit_queue": {},
            },
            f,
        )
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def sample_webhook_data():
    """Sample Twilio webhook data."""
    return {"From": "whatsapp:+1234567890", "Body": "Hello, test message"}


@pytest.fixture
def clear_app_state():
    """Clear application state before each test."""
    # Import here to avoid circular imports during test collection
    from src.app import balances, deposit_queue, usage_logs

    balances.clear()
    usage_logs.clear()
    deposit_queue.clear()

    yield

    # Clean up after test
    balances.clear()
    usage_logs.clear()
    deposit_queue.clear()
