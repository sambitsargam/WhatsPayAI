"""
Tests for Balance Handler Module
"""

import pytest
from datetime import datetime, timedelta
from src.handlers.balance import handle_balance_query, calculate_cost_estimate, format_htr_amount


class TestBalanceHandler:
    """Test cases for balance handler."""
    
    @pytest.mark.asyncio
    async def test_handle_balance_query_empty_account(self, clear_app_state):
        """Test balance query for account with no balance."""
        result = await handle_balance_query("+1234567890")
        
        assert "Account Summary" in result
        assert "0.0000 HTR" in result
        assert "Low Balance Warning" in result
        assert "top up" in result.lower()
    
    @pytest.mark.asyncio
    async def test_handle_balance_query_with_balance(self, clear_app_state):
        """Test balance query for account with balance."""
        from src.app import balances, usage_logs
        
        # Set up test data
        balances["+1234567890"] = 0.5
        usage_logs["+1234567890"] = [
            {
                'timestamp': datetime.now().isoformat(),
                'cost': 0.02,
                'type': 'ai_query'
            }
        ]
        
        result = await handle_balance_query("+1234567890")
        
        assert "Account Summary" in result
        assert "0.5000 HTR" in result
        assert "0.02" in result  # Total spent
        assert "Last 24 Hours" in result
    
    @pytest.mark.asyncio
    async def test_handle_balance_query_low_balance_warning(self, clear_app_state):
        """Test low balance warning."""
        from src.app import balances
        
        balances["+1234567890"] = 0.005  # Low balance
        
        result = await handle_balance_query("+1234567890")
        
        assert "Low Balance Warning" in result
        assert "running low" in result
    
    def test_calculate_cost_estimate(self):
        """Test cost estimation for tokens."""
        test_cases = [
            (100, 0.01),   # 100 tokens = 0.01 HTR
            (200, 0.02),   # 200 tokens = 0.02 HTR
            (50, 0.005),   # 50 tokens = 0.005 HTR
            (1000, 0.1),   # 1000 tokens = 0.1 HTR
        ]
        
        for tokens, expected_cost in test_cases:
            result = calculate_cost_estimate(tokens)
            assert result == expected_cost
    
    def test_format_htr_amount(self):
        """Test HTR amount formatting."""
        test_cases = [
            (0.000001, "0.000001 HTR"),  # Very small amount
            (0.001, "0.0010 HTR"),       # Small amount
            (0.01, "0.010 HTR"),         # Medium amount
            (1.0, "1.000 HTR"),          # Large amount
            (10.5, "10.500 HTR"),        # Very large amount
        ]
        
        for amount, expected in test_cases:
            result = format_htr_amount(amount)
            assert result == expected
