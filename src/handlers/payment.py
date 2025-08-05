"""
Payment Handler

Handles payment-related requests including top-ups and deposit processing.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def extract_amount_from_message(message: str) -> Optional[float]:
    """
    Extract HTR amount from user message.
    
    Args:
        message: User's message text
        
    Returns:
        Amount in HTR if found, None otherwise
    """
    # Patterns to match amounts like "1 HTR", "0.5 htr", "top up 2.5", etc.
    patterns = [
        r'(\d+(?:\.\d+)?)\s*htr',  # "1.5 HTR"
        r'top\s*up\s+(\d+(?:\.\d+)?)',  # "top up 1.5"
        r'add\s+(\d+(?:\.\d+)?)',  # "add 1.5"
        r'deposit\s+(\d+(?:\.\d+)?)',  # "deposit 1.5"
    ]
    
    message_lower = message.lower()
    
    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            try:
                amount = float(match.group(1))
                if 0.001 <= amount <= 1000:  # Reasonable limits
                    return amount
            except ValueError:
                continue
    
    return None


async def handle_payment_request(user_id: str, message: str) -> str:
    """
    Handle payment/top-up requests from users.
    
    Args:
        user_id: User's WhatsApp number
        message: User's message text
        
    Returns:
        Reply message for the user
    """
    try:
        # Import here to avoid circular imports
        from ..hathor_client import get_user_address
        from ..app import deposit_queue
        
        # Extract amount from message
        amount = extract_amount_from_message(message)
        
        if amount is None:
            return (
                "💰 To top up your account, please specify the amount in HTR.\n\n"
                "Examples:\n"
                "• 'Top up 1 HTR'\n"
                "• 'Add 0.5 HTR to my account'\n"
                "• 'Deposit 2.5 HTR'\n\n"
                "Minimum: 0.001 HTR\n"
                "Maximum: 1000 HTR per transaction"
            )
        
        # Get or generate user's Hathor address
        user_address = get_user_address(user_id)
        
        # Add to deposit queue for monitoring
        deposit_queue[user_address] = {
            'user_id': user_id,
            'expected_amount': amount,
            'timestamp': None  # Would be set in production
        }
        
        logger.info(f"Added deposit queue entry for user {user_id}, amount {amount} HTR")
        
        # Return deposit instructions
        return (
            f"💳 **Deposit Instructions**\n\n"
            f"Please send **{amount} HTR** to this address:\n\n"
            f"`{user_address}`\n\n"
            f"⏱️ Your deposit will be automatically detected and credited to your account within 1-2 minutes.\n\n"
            f"📱 You'll receive a confirmation message once the deposit is processed.\n\n"
            f"❓ Need help? Just type 'help' for assistance."
        )
        
    except Exception as e:
        logger.error(f"Error handling payment request from {user_id}: {e}")
        return (
            "❌ Sorry, I encountered an error processing your payment request. "
            "Please try again later or contact support."
        )


async def handle_deposit_confirmation(user_id: str, tx_hash: str, amount: float) -> str:
    """
    Generate deposit confirmation message.
    
    Args:
        user_id: User's WhatsApp number
        tx_hash: Transaction hash
        amount: Deposited amount in HTR
        
    Returns:
        Confirmation message
    """
    try:
        # Import here to avoid circular imports
        from ..app import balances
        
        current_balance = balances.get(user_id, 0.0)
        
        return (
            f"✅ **Deposit Confirmed!**\n\n"
            f"💰 Amount: {amount} HTR\n"
            f"🔗 Transaction: `{tx_hash[:16]}...`\n"
            f"💳 Current Balance: {current_balance} HTR\n\n"
            f"You can now use the AI assistant! Just send me any question or text to analyze."
        )
        
    except Exception as e:
        logger.error(f"Error generating deposit confirmation for {user_id}: {e}")
        return (
            f"✅ Deposit of {amount} HTR confirmed! "
            f"Your account has been credited."
        )
