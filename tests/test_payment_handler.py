"""
Tests for Payment Handler Module
"""

from unittest.mock import Mock, patch

import pytest

from src.handlers.payment import (
    extract_amount_from_message,
    handle_deposit_confirmation,
    handle_payment_request,
)


class TestPaymentHandler:
    """Test cases for payment handler."""

    def test_extract_amount_from_message(self):
        """Test amount extraction from various message formats."""
        test_cases = [
            ("top up 1 HTR", 1.0),
            ("add 0.5 htr to my account", 0.5),
            ("deposit 2.5", 2.5),
            ("I want to top up 10 HTR", 10.0),
            ("charge 0.001 HTR", 0.001),
            ("top up 1000 HTR", 1000.0),
        ]

        for message, expected in test_cases:
            result = extract_amount_from_message(message)
            assert result == expected, f"Failed for message: {message}"

    def test_extract_amount_invalid_messages(self):
        """Test amount extraction from invalid messages."""
        invalid_cases = [
            "top up some HTR",
            "add money please",
            "deposit abc HTR",
            "top up 0 HTR",  # Zero amount  
            "top up 10000 HTR",  # Too large
        ]

        for message in invalid_cases:
            result = extract_amount_from_message(message)
            assert result is None, f"Should return None for: {message}"

    @pytest.mark.asyncio
    @patch("src.hathor_client.get_user_address")
    async def test_handle_payment_request_valid_amount(
        self, mock_get_address, clear_app_state
    ):
        """Test handling valid payment request."""
        from src.app import deposit_queue

        mock_get_address.return_value = "WYBwT1234567890abcdef"

        result = await handle_payment_request("+1234567890", "top up 1 HTR")

        assert "Deposit Instructions" in result
        assert "1.0 HTR" in result  # Updated to match actual output format
        assert "WYBwT1234567890abcdef" in result
        assert len(deposit_queue) == 1

    @pytest.mark.asyncio
    async def test_handle_payment_request_invalid_amount(self, clear_app_state):
        """Test handling payment request with invalid amount."""
        result = await handle_payment_request("+1234567890", "top up some money")

        assert "specify the amount" in result
        assert "Examples:" in result

    @pytest.mark.asyncio
    async def test_handle_deposit_confirmation(self, clear_app_state):
        """Test deposit confirmation message generation."""
        from src.app import balances

        balances["+1234567890"] = 1.5

        result = await handle_deposit_confirmation("+1234567890", "tx123456", 1.0)

        assert "Deposit Confirmed!" in result
        assert "1.0 HTR" in result
        assert "1.5 HTR" in result
        assert "tx123456" in result

    @pytest.mark.asyncio
    @patch("src.hathor_client.get_user_address")
    async def test_handle_payment_request_exception(
        self, mock_get_address, clear_app_state
    ):
        """Test handling payment request with exception."""
        mock_get_address.side_effect = Exception("Test error")

        result = await handle_payment_request("+1234567890", "top up 1 HTR")

        assert "error processing your payment request" in result
