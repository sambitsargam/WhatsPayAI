"""
Tests for AI Query Handler Module
"""

import pytest
from unittest.mock import patch, Mock
from src.handlers.ai_query import handle_ai_query, count_tokens_estimate, calculate_cost


class TestAIQueryHandler:
    """Test cases for AI query handler."""
    
    def test_count_tokens_estimate(self):
        """Test token counting estimation."""
        test_cases = [
            ("Hello world", 3),          # ~12 chars / 4 = 3 tokens
            ("This is a test", 4),       # ~16 chars / 4 = 4 tokens
            ("", 1),                     # Minimum 1 token
            ("A" * 100, 25),            # 100 chars / 4 = 25 tokens
        ]
        
        for text, expected_tokens in test_cases:
            result = count_tokens_estimate(text)
            assert result == expected_tokens
    
    def test_calculate_cost(self):
        """Test cost calculation."""
        test_cases = [
            (50, 50, 0.01),    # 100 total tokens = 0.01 HTR
            (100, 100, 0.02),  # 200 total tokens = 0.02 HTR
            (25, 25, 0.005),   # 50 total tokens = 0.005 HTR
        ]
        
        for input_tokens, output_tokens, expected_cost in test_cases:
            result = calculate_cost(input_tokens, output_tokens)
            assert result == expected_cost
    
    @pytest.mark.asyncio
    async def test_handle_ai_query_insufficient_balance(self, clear_app_state):
        """Test AI query with insufficient balance."""
        from src.app import balances
        
        balances["+1234567890"] = 0.001  # Very low balance
        
        result = await handle_ai_query("+1234567890", "What is the capital of France?")
        
        assert "Insufficient Balance" in result
        assert "top up" in result.lower()
    
    @pytest.mark.asyncio
    async def test_handle_ai_query_message_too_long(self, clear_app_state):
        """Test AI query with message that's too long."""
        long_message = "A" * 2001  # Exceeds MAX_INPUT_LENGTH
        
        result = await handle_ai_query("+1234567890", long_message)
        
        assert "too long" in result
        assert "2000 characters" in result
    
    @pytest.mark.asyncio
    @patch('src.handlers.ai_query.process_ai_query')
    async def test_handle_ai_query_success(self, mock_process, clear_app_state):
        """Test successful AI query processing."""
        from src.app import balances, usage_logs
        
        # Set up sufficient balance
        balances["+1234567890"] = 1.0
        
        # Mock AI response
        mock_process.return_value = ("Paris is the capital of France.", 20, 15)
        
        result = await handle_ai_query("+1234567890", "What is the capital of France?")
        
        assert "AI Response:" in result
        assert "Paris is the capital of France." in result
        assert "Cost:" in result
        assert "Balance:" in result
        
        # Check that balance was deducted
        assert balances["+1234567890"] < 1.0
        
        # Check that usage was logged
        assert "+1234567890" in usage_logs
        assert len(usage_logs["+1234567890"]) == 1
    
    @pytest.mark.asyncio
    @patch('src.handlers.ai_query.openai.ChatCompletion.create')
    async def test_process_ai_query_success(self, mock_create):
        """Test successful AI query processing."""
        from src.handlers.ai_query import process_ai_query
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This is a test response."))]
        mock_create.return_value = mock_response
        
        response, input_tokens, output_tokens = await process_ai_query("Test question")
        
        assert response == "This is a test response."
        assert input_tokens > 0
        assert output_tokens > 0
        mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.handlers.ai_query.openai.ChatCompletion.create')
    async def test_process_ai_query_openai_error(self, mock_create):
        """Test AI query processing with OpenAI error."""
        from src.handlers.ai_query import process_ai_query
        import openai
        
        mock_create.side_effect = openai.error.OpenAIError("API Error")
        
        with pytest.raises(Exception) as exc_info:
            await process_ai_query("Test question")
        
        assert "AI service error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @patch('src.handlers.ai_query.process_ai_query')
    async def test_handle_ai_query_processing_error(self, mock_process, clear_app_state):
        """Test AI query with processing error."""
        from src.app import balances
        
        balances["+1234567890"] = 1.0
        mock_process.side_effect = Exception("Processing failed")
        
        result = await handle_ai_query("+1234567890", "Test question")
        
        assert "Processing failed" in result
