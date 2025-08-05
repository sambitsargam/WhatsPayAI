"""
Integration Tests for WhatsPayAI Application
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


class TestWebhookIntegration:
    """Integration tests for webhook endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.app import app
        return TestClient(app)
    
    @pytest.fixture
    def mock_all_external_services(self):
        """Mock all external services for integration tests."""
        with patch('src.twilio_client.send_whatsapp_message') as mock_twilio, \
             patch('src.intent.classify_with_openai') as mock_openai_intent, \
             patch('src.handlers.ai_query.openai.ChatCompletion.create') as mock_openai_chat, \
             patch('src.hathor_client.get_user_address') as mock_address:
            
            # Configure mocks
            mock_twilio.return_value = True
            mock_openai_intent.return_value = None  # Force fallback to keywords
            
            mock_chat_response = Mock()
            mock_chat_response.choices = [Mock(message=Mock(content="Test AI response"))]
            mock_openai_chat.return_value = mock_chat_response
            
            mock_address.return_value = "WYBwT1234567890abcdef"
            
            yield {
                'twilio': mock_twilio,
                'openai_intent': mock_openai_intent,
                'openai_chat': mock_openai_chat,
                'address': mock_address
            }
    
    def test_webhook_payment_intent(self, client, mock_all_external_services, clear_app_state):
        """Test webhook with payment intent."""
        response = client.post("/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": "top up 1 HTR"
        })
        
        assert response.status_code == 200
        assert response.text == "OK"
        
        # Verify Twilio was called
        mock_all_external_services['twilio'].assert_called_once()
        call_args = mock_all_external_services['twilio'].call_args
        assert "Deposit Instructions" in call_args[0][1]
    
    def test_webhook_balance_intent(self, client, mock_all_external_services, clear_app_state):
        """Test webhook with balance intent."""
        response = client.post("/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": "what's my balance?"
        })
        
        assert response.status_code == 200
        
        # Verify balance response
        mock_all_external_services['twilio'].assert_called_once()
        call_args = mock_all_external_services['twilio'].call_args
        assert "Account Summary" in call_args[0][1]
    
    def test_webhook_help_intent(self, client, mock_all_external_services, clear_app_state):
        """Test webhook with help intent."""
        response = client.post("/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": "help me please"
        })
        
        assert response.status_code == 200
        
        # Verify help response
        mock_all_external_services['twilio'].assert_called_once()
        call_args = mock_all_external_services['twilio'].call_args
        assert "WhatsPayAI - Your AI Assistant" in call_args[0][1]
    
    def test_webhook_ai_query_insufficient_balance(self, client, mock_all_external_services, clear_app_state):
        """Test webhook with AI query but insufficient balance."""
        response = client.post("/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": "What is the capital of France?"
        })
        
        assert response.status_code == 200
        
        # Verify insufficient balance response
        mock_all_external_services['twilio'].assert_called_once()
        call_args = mock_all_external_services['twilio'].call_args
        assert "Insufficient Balance" in call_args[0][1]
    
    def test_webhook_ai_query_with_balance(self, client, mock_all_external_services, clear_app_state):
        """Test webhook with AI query and sufficient balance."""
        from src.app import balances
        
        # Set up balance
        balances["+1234567890"] = 1.0
        
        response = client.post("/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": "What is the capital of France?"
        })
        
        assert response.status_code == 200
        
        # Verify AI response
        mock_all_external_services['twilio'].assert_called_once()
        call_args = mock_all_external_services['twilio'].call_args
        response_text = call_args[0][1]
        assert "AI Response:" in response_text
        assert "Test AI response" in response_text
    
    def test_webhook_missing_data(self, client):
        """Test webhook with missing data."""
        response = client.post("/webhook", data={})
        
        assert response.status_code == 500
        assert response.text == "Error"
    
    def test_webhook_empty_message(self, client, mock_all_external_services, clear_app_state):
        """Test webhook with empty message body."""
        response = client.post("/webhook", data={
            "From": "whatsapp:+1234567890",
            "Body": ""
        })
        
        assert response.status_code == 500
    
    def test_stats_endpoint(self, client, clear_app_state):
        """Test stats endpoint."""
        from src.app import balances, deposit_queue, usage_logs
        
        # Set up test data
        balances["user1"] = 1.0
        balances["user2"] = 0.5
        deposit_queue["addr1"] = {"user_id": "user1"}
        usage_logs["user1"] = [{"cost": 0.01}]
        
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_users"] == 2
        assert data["total_balance"] == 1.5
        assert data["pending_deposits"] == 1
        assert data["total_queries"] == 1
    
    def test_root_endpoint(self, client):
        """Test root health check endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "WhatsPayAI is running"
        assert "version" in data
