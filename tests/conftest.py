"""
Test Configuration and Fixtures

Common test utilities and fixtures for WhatsPayAI tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import json
import tempfile
import os


@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses."""
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="This is a mock AI response."))
    ]
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
        'success': True,
        'total_amount_received': 100  # 1 HTR in centis
    }
    mock_client.get_address_history.return_value = {
        'success': True,
        'history': []
    }
    return mock_client


@pytest.fixture
def temp_state_file():
    """Create temporary state file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'balances': {'test_user': 1.0},
            'usage_logs': {'test_user': []},
            'deposit_queue': {}
        }, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def sample_webhook_data():
    """Sample Twilio webhook data."""
    return {
        'From': 'whatsapp:+1234567890',
        'Body': 'Hello, test message'
    }


@pytest.fixture
def clear_app_state():
    """Clear application state before each test."""
    # Import here to avoid circular imports during test collection
    from src.app import balances, usage_logs, deposit_queue
    
    balances.clear()
    usage_logs.clear()
    deposit_queue.clear()
    
    yield
    
    # Clean up after test
    balances.clear()
    usage_logs.clear()
    deposit_queue.clear()
