"""
Tests for Intent Classification Module
"""

from unittest.mock import Mock, patch

import pytest

from src.intent import classify_intent, classify_with_keywords, classify_with_openai


class TestIntentClassification:
    """Test cases for intent classification."""

    def test_classify_payment_intent_keywords(self):
        """Test payment intent classification with keywords."""
        test_cases = [
            "top up 1 HTR",
            "I want to deposit 0.5 HTR",
            "add money to my account",
            "charge my wallet with HTR",
        ]

        for message in test_cases:
            intent = classify_with_keywords(message)
            assert intent == "payment_intent", f"Failed for message: {message}"

    def test_classify_balance_intent_keywords(self):
        """Test balance intent classification with keywords."""
        test_cases = [
            "what's my balance?",
            "how much credit do I have?",
            "show my account",
            "usage history please",
        ]

        for message in test_cases:
            intent = classify_with_keywords(message)
            assert intent == "balance_intent", f"Failed for message: {message}"

    def test_classify_help_intent_keywords(self):
        """Test help intent classification with keywords."""
        test_cases = [
            "help me please",
            "how to use this service?",
            "what commands are available?",
            "getting started guide",
        ]

        for message in test_cases:
            intent = classify_with_keywords(message)
            assert intent == "help_intent", f"Failed for message: {message}"

    def test_classify_default_to_ai_query(self):
        """Test default classification to AI query."""
        test_cases = [
            "what's the weather like?",
            "explain quantum computing",
            "translate this text",
            "random question about cats",
        ]

        for message in test_cases:
            intent = classify_with_keywords(message)
            assert intent == "ai_query_intent", f"Failed for message: {message}"

    @patch("src.intent.openai.ChatCompletion.create")
    def test_classify_with_openai_success(self, mock_create):
        """Test successful OpenAI classification."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="payment_intent"))]
        mock_create.return_value = mock_response

        result = classify_with_openai("top up 1 HTR")
        assert result == "payment_intent"
        mock_create.assert_called_once()

    @patch("src.intent.openai.ChatCompletion.create")
    def test_classify_with_openai_invalid_response(self, mock_create):
        """Test OpenAI returning invalid intent."""
        # Mock OpenAI response with invalid intent
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="invalid_intent"))]
        mock_create.return_value = mock_response

        result = classify_with_openai("test message")
        assert result is None

    @patch("src.intent.openai.ChatCompletion.create")
    def test_classify_with_openai_exception(self, mock_create):
        """Test OpenAI API exception handling."""
        mock_create.side_effect = Exception("API Error")

        result = classify_with_openai("test message")
        assert result is None

    @patch("src.intent.classify_with_openai")
    def test_classify_intent_with_openai_success(self, mock_openai):
        """Test main classify_intent function with OpenAI success."""
        mock_openai.return_value = "balance_intent"

        result = classify_intent("what's my balance?")
        assert result == "balance_intent"
        mock_openai.assert_called_once()

    @patch("src.intent.classify_with_openai")
    def test_classify_intent_fallback_to_keywords(self, mock_openai):
        """Test fallback to keyword classification when OpenAI fails."""
        mock_openai.return_value = None

        result = classify_intent("top up 1 HTR")
        assert result == "payment_intent"

    def test_classify_intent_empty_message(self):
        """Test classification of empty message."""
        result = classify_intent("")
        assert result == "help_intent"

        result = classify_intent("   ")
        assert result == "help_intent"

        result = classify_intent(None)
        assert result == "help_intent"
