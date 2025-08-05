"""
Balance Handler

Handles balance queries and usage statistics.
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


async def handle_balance_query(user_id: str) -> str:
    """
    Handle balance and usage queries from users.
    
    Args:
        user_id: User's WhatsApp number
        
    Returns:
        Reply message with balance information
    """
    try:
        # Import here to avoid circular imports
        from ..app import balances, usage_logs
        
        # Get user's current balance
        current_balance = balances.get(user_id, 0.0)
        
        # Calculate usage statistics
        user_usage = usage_logs.get(user_id, [])
        total_spent = sum(entry.get('cost', 0) for entry in user_usage)
        
        # Calculate usage in the last 24 hours
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        recent_usage = [
            entry for entry in user_usage 
            if datetime.fromisoformat(entry.get('timestamp', '1970-01-01')) > yesterday
        ]
        recent_spent = sum(entry.get('cost', 0) for entry in recent_usage)
        recent_queries = len(recent_usage)
        
        # Generate balance report
        message = f"💳 **Account Summary**\n\n"
        message += f"💰 Current Balance: **{current_balance:.4f} HTR**\n"
        message += f"📊 Total Spent: {total_spent:.4f} HTR\n"
        message += f"🔢 Total Queries: {len(user_usage)}\n\n"
        
        if recent_queries > 0:
            message += f"📅 **Last 24 Hours:**\n"
            message += f"• Queries: {recent_queries}\n"
            message += f"• Spent: {recent_spent:.4f} HTR\n\n"
        
        # Add balance status
        if current_balance <= 0:
            message += (
                "⚠️ **Low Balance Warning**\n"
                "Your balance is empty. Please top up to continue using the AI assistant.\n\n"
                "💡 Type 'top up 1 HTR' to add funds to your account."
            )
        elif current_balance < 0.01:
            message += (
                "⚠️ **Low Balance Warning**\n"
                "Your balance is running low. Consider topping up soon.\n\n"
                "💡 Type 'top up 1 HTR' to add more funds."
            )
        else:
            estimated_queries = int(current_balance / 0.01) * 100  # Assuming 0.01 HTR per 100 tokens
            message += f"📈 Estimated remaining queries: ~{estimated_queries}"
        
        return message
        
    except Exception as e:
        logger.error(f"Error handling balance query from {user_id}: {e}")
        return (
            "❌ Sorry, I couldn't retrieve your balance information right now. "
            "Please try again later."
        )


async def handle_usage_history(user_id: str, limit: int = 10) -> str:
    """
    Generate usage history report for a user.
    
    Args:
        user_id: User's WhatsApp number
        limit: Maximum number of recent entries to show
        
    Returns:
        Usage history message
    """
    try:
        # Import here to avoid circular imports
        from ..app import usage_logs
        
        user_usage = usage_logs.get(user_id, [])
        
        if not user_usage:
            return (
                "📋 **Usage History**\n\n"
                "No usage history found. Start using the AI assistant to see your activity here!"
            )
        
        # Sort by timestamp (most recent first)
        sorted_usage = sorted(
            user_usage, 
            key=lambda x: x.get('timestamp', '1970-01-01'), 
            reverse=True
        )
        
        message = f"📋 **Usage History** (Last {min(limit, len(sorted_usage))} entries)\n\n"
        
        for i, entry in enumerate(sorted_usage[:limit]):
            timestamp = entry.get('timestamp', 'Unknown')
            cost = entry.get('cost', 0)
            query_type = entry.get('type', 'query')
            tokens = entry.get('tokens_used', 0)
            
            try:
                # Format timestamp
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%m/%d %H:%M")
            except:
                time_str = "Unknown"
            
            message += f"{i+1}. {time_str} - {query_type.title()}\n"
            message += f"   💰 {cost:.4f} HTR ({tokens} tokens)\n\n"
        
        if len(user_usage) > limit:
            message += f"... and {len(user_usage) - limit} more entries\n\n"
        
        message += "💡 Type 'balance' to see your current account summary."
        
        return message
        
    except Exception as e:
        logger.error(f"Error generating usage history for {user_id}: {e}")
        return (
            "❌ Sorry, I couldn't retrieve your usage history right now. "
            "Please try again later."
        )


def calculate_cost_estimate(tokens: int) -> float:
    """
    Calculate estimated cost for a number of tokens.
    
    Args:
        tokens: Number of tokens
        
    Returns:
        Estimated cost in HTR
    """
    # Cost per 100 tokens (configurable)
    cost_per_100_tokens = 0.01  # 0.01 HTR per 100 tokens
    
    return (tokens / 100) * cost_per_100_tokens


def format_htr_amount(amount: float) -> str:
    """
    Format HTR amount for display.
    
    Args:
        amount: Amount in HTR
        
    Returns:
        Formatted string
    """
    if amount < 0.001:
        return f"{amount:.6f} HTR"
    elif amount < 0.01:
        return f"{amount:.4f} HTR"
    else:
        return f"{amount:.3f} HTR"
