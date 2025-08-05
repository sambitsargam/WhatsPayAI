"""
Tests for Twilio Client Module
"""

from unittest.mock import Mock, patch

import pytest

from src.twilio_client import (
    send_whatsapp_message,
    send_whatsapp_message_safe,
    validate_phone_number,
)


class TestTwilioClient:
    """Test cases for Twilio client."""

    def test_validate_phone_number_valid(self):
        """Test validation of valid phone numbers."""
        valid_numbers = [
            "+1234567890",
            "+44123456789",
            "+91987654321",
        ]

        for number in valid_numbers:
            result = validate_phone_number(number)
            assert result == number

    def test_validate_phone_number_with_whatsapp_prefix(self):
        """Test validation of numbers with whatsapp: prefix."""
        result = validate_phone_number("whatsapp:+1234567890")
        assert result == "+1234567890"

    def test_validate_phone_number_invalid(self):
        """Test validation of invalid phone numbers."""
        invalid_numbers = [
            "1234567890",  # Missing +
            "+abc123456",  # Contains letters
            "",  # Empty
            None,  # None
            "+",  # Just +
        ]

        for number in invalid_numbers:
            result = validate_phone_number(number)
            assert result is None

    @pytest.mark.asyncio
    @patch("src.twilio_client.twilio_client")
    async def test_send_whatsapp_message_success(self, mock_client):
        """Test successful WhatsApp message sending."""
        # Mock Twilio client
        mock_message = Mock()
        mock_message.sid = "test_message_sid"
        mock_client.messages.create.return_value = mock_message

        result = await send_whatsapp_message("+1234567890", "Test message")

        assert result is True
        mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.twilio_client.twilio_client", None)
    async def test_send_whatsapp_message_no_client(self):
        """Test message sending with no Twilio client."""
        result = await send_whatsapp_message("+1234567890", "Test message")
        assert result is False

    @pytest.mark.asyncio
    @patch("src.twilio_client.twilio_client")
    async def test_send_whatsapp_message_exception(self, mock_client):
        """Test message sending with exception."""
        mock_client.messages.create.side_effect = Exception("Twilio error")

        result = await send_whatsapp_message("+1234567890", "Test message")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_whatsapp_message_safe_valid(self):
        """Test safe message sending with valid input."""
        with patch("src.twilio_client.send_whatsapp_message") as mock_send:
            mock_send.return_value = True

            result = await send_whatsapp_message_safe("+1234567890", "Test message")

            assert result is True
            mock_send.assert_called_once_with("+1234567890", "Test message")

    @pytest.mark.asyncio
    async def test_send_whatsapp_message_safe_invalid_number(self):
        """Test safe message sending with invalid number."""
        result = await send_whatsapp_message_safe("invalid_number", "Test message")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_whatsapp_message_safe_empty_message(self):
        """Test safe message sending with empty message."""
        result = await send_whatsapp_message_safe("+1234567890", "")
        assert result is False

        result = await send_whatsapp_message_safe("+1234567890", "   ")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_whatsapp_message_safe_long_message(self):
        """Test safe message sending with long message."""
        long_message = "A" * 4500  # Exceeds 4000 character limit

        with patch("src.twilio_client.send_whatsapp_message") as mock_send:
            mock_send.return_value = True

            result = await send_whatsapp_message_safe("+1234567890", long_message)

            assert result is True
            # Check that message was truncated
            sent_message = mock_send.call_args[0][1]
            assert len(sent_message) <= 4000
            assert sent_message.endswith("...")
