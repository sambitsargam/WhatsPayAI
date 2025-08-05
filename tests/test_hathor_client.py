"""
Tests for Hathor Client Module
"""

from unittest.mock import Mock, patch

import pytest

from src.hathor_client import (
    check_incoming_deposits,
    generate_deterministic_address,
    get_address_balance,
    get_user_address,
    submit_transfer,
    validate_hathor_address,
)


class TestHathorClient:
    """Test cases for Hathor client."""

    def test_generate_deterministic_address(self):
        """Test deterministic address generation."""
        user_id = "test_user_123"

        with patch("src.hathor_client.HATHOR_WALLET_SEED", "test_seed"):
            address1 = generate_deterministic_address(user_id)
            address2 = generate_deterministic_address(user_id)

            # Should be deterministic
            assert address1 == address2

            # Should start with testnet prefix
            assert address1.startswith("WYBwT")

    def test_get_user_address_cached(self):
        """Test getting cached user address."""
        from src.hathor_client import user_addresses

        user_id = "test_user_456"
        test_address = "WYBwT123456789"
        user_addresses[user_id] = test_address

        result = get_user_address(user_id)
        assert result == test_address

    def test_get_user_address_new(self):
        """Test getting new user address."""
        from src.hathor_client import user_addresses

        user_id = "new_test_user"
        # Clear any existing address
        if user_id in user_addresses:
            del user_addresses[user_id]

        with patch("src.hathor_client.HATHOR_WALLET_SEED", "test_seed"):
            result = get_user_address(user_id)

            assert result.startswith("WYBwT")
            assert user_id in user_addresses

    @patch("src.hathor_client.hathor_client.get_address_history")
    def test_check_incoming_deposits_success(self, mock_get_history):
        """Test checking incoming deposits successfully."""
        mock_get_history.return_value = {
            "success": True,
            "history": [
                {
                    "tx_id": "tx123",
                    "outputs": [
                        {
                            "decoded": {"address": "WYBwT123"},
                            "value": 100,  # 1 HTR in centis
                        }
                    ],
                }
            ],
        }

        deposits = check_incoming_deposits("WYBwT123")

        assert len(deposits) == 1
        assert deposits[0] == ("tx123", 1.0)  # Converted from centis

    @patch("src.hathor_client.hathor_client.get_address_history")
    def test_check_incoming_deposits_no_history(self, mock_get_history):
        """Test checking deposits with no history."""
        mock_get_history.return_value = {"success": False}

        deposits = check_incoming_deposits("WYBwT123")
        assert deposits == []

    @patch("src.hathor_client.hathor_client.get_address_history")
    def test_check_incoming_deposits_exception(self, mock_get_history):
        """Test checking deposits with exception."""
        mock_get_history.side_effect = Exception("Network error")

        deposits = check_incoming_deposits("WYBwT123")
        assert deposits == []

    @patch("src.hathor_client.hathor_client.get_address_info")
    def test_get_address_balance_success(self, mock_get_info):
        """Test getting address balance successfully."""
        mock_get_info.return_value = {
            "success": True,
            "total_amount_received": 250,  # 2.5 HTR in centis
        }

        balance = get_address_balance("WYBwT123")
        assert balance == 2.5

    @patch("src.hathor_client.hathor_client.get_address_info")
    def test_get_address_balance_failure(self, mock_get_info):
        """Test getting address balance with failure."""
        mock_get_info.return_value = {"success": False}

        balance = get_address_balance("WYBwT123")
        assert balance == 0.0

    @patch("src.hathor_client.hathor_client.get_address_info")
    def test_get_address_balance_exception(self, mock_get_info):
        """Test getting address balance with exception."""
        mock_get_info.side_effect = Exception("Network error")

        balance = get_address_balance("WYBwT123")
        assert balance == 0.0

    def test_validate_hathor_address_testnet_valid(self):
        """Test validation of valid testnet addresses."""
        with patch("src.hathor_client.HATHOR_NETWORK", "testnet"):
            valid_addresses = [
                "WYBwT1234567890abcdef1234567890",
                "WYBwTabcdef1234567890abcdef123456",
            ]

            for address in valid_addresses:
                result = validate_hathor_address(address)
                assert result is True

    def test_validate_hathor_address_mainnet_valid(self):
        """Test validation of valid mainnet addresses."""
        with patch("src.hathor_client.HATHOR_NETWORK", "mainnet"):
            valid_addresses = [
                "H1234567890abcdef1234567890abcd",
                "Habcdef1234567890abcdef1234567890",
            ]

            for address in valid_addresses:
                result = validate_hathor_address(address)
                assert result is True

    def test_validate_hathor_address_invalid(self):
        """Test validation of invalid addresses."""
        invalid_addresses = [
            "",
            None,
            "invalid",
            "H123",  # Too short
            "WYBwT123",  # Too short for testnet
            "X1234567890abcdef1234567890abcd",  # Wrong prefix
        ]

        for address in invalid_addresses:
            result = validate_hathor_address(address)
            assert result is False

    def test_submit_transfer_placeholder(self):
        """Test transfer submission (placeholder implementation)."""
        result = submit_transfer("from_addr", "to_addr", 1.0)
        assert result is None  # Placeholder returns None
