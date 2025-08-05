"""
AI Query Handler

Handles AI-powered text processing and question answering requests.
"""

import logging
import os
from datetime import datetime
from typing import Optional, Tuple

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

# Configuration
COST_PER_100_TOKENS = float(os.getenv("COST_PER_100_TOKENS", "0.01"))
MAX_TOKENS = 500  # Maximum tokens for response
MAX_INPUT_LENGTH = 2000  # Maximum input message length


def count_tokens_estimate(text: str) -> int:
    """
    Estimate token count for text.

    Simple estimation: ~4 characters per token for English text.
    In production, use tiktoken for accurate counting.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    return max(1, len(text) // 4)


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost for API usage.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in HTR
    """
    total_tokens = input_tokens + output_tokens
    return (total_tokens / 100) * COST_PER_100_TOKENS


async def process_ai_query(message: str) -> Tuple[str, int, int]:
    """
    Process AI query using OpenAI API.

    Args:
        message: User's message/query

    Returns:
        Tuple of (response_text, input_tokens, output_tokens)
    """
    try:
        # Estimate input tokens
        input_tokens = count_tokens_estimate(message)

        # Create system prompt
        system_prompt = (
            "You are a helpful AI assistant integrated with WhatsApp. "
            "Provide clear, concise, and helpful responses. "
            "Keep responses under 500 tokens when possible."
        )

        # Make OpenAI API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            max_tokens=MAX_TOKENS,
            temperature=0.7,
        )

        # Extract response
        ai_response = response.choices[0].message.content.strip()
        output_tokens = count_tokens_estimate(ai_response)

        logger.info(
            f"AI query processed: {input_tokens} input + {output_tokens} output tokens"
        )

        return ai_response, input_tokens, output_tokens

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        if "openai" in str(e).lower() or "api" in str(e).lower():
            raise Exception(f"AI service error: {str(e)}")
        else:
            raise Exception("Sorry, I encountered an error processing your request.")


async def handle_ai_query(user_id: str, message: str) -> str:
    """
    Handle AI query requests with billing and balance checking.

    Args:
        user_id: User's WhatsApp number
        message: User's query text

    Returns:
        Reply message for the user
    """
    try:
        # Import here to avoid circular imports
        from ..app import balances, usage_logs

        # Validate input length
        if len(message) > MAX_INPUT_LENGTH:
            return (
                f"❌ Your message is too long ({len(message)} characters). "
                f"Please keep it under {MAX_INPUT_LENGTH} characters."
            )

        # Check user balance
        current_balance = balances.get(user_id, 0.0)

        # Estimate cost before processing
        estimated_input_tokens = count_tokens_estimate(message)
        estimated_output_tokens = min(
            MAX_TOKENS, estimated_input_tokens
        )  # Conservative estimate
        estimated_cost = calculate_cost(estimated_input_tokens, estimated_output_tokens)

        if current_balance < estimated_cost:
            return (
                f"💰 **Insufficient Balance**\n\n"
                f"Estimated cost: {estimated_cost:.4f} HTR\n"
                f"Your balance: {current_balance:.4f} HTR\n"
                f"Needed: {estimated_cost - current_balance:.4f} HTR\n\n"
                f"💡 Please top up your account to continue.\n"
                f"Type 'top up 1 HTR' to add funds."
            )

        # Process the AI query
        try:
            ai_response, input_tokens, output_tokens = await process_ai_query(message)
        except Exception as e:
            return f"❌ {str(e)}"

        # Calculate actual cost
        actual_cost = calculate_cost(input_tokens, output_tokens)

        # Deduct cost from balance
        balances[user_id] = current_balance - actual_cost

        # Log usage
        if user_id not in usage_logs:
            usage_logs[user_id] = []

        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "ai_query",
            "cost": actual_cost,
            "tokens_used": input_tokens + output_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "query_preview": message[:50] + "..." if len(message) > 50 else message,
        }
        usage_logs[user_id].append(usage_entry)

        logger.info(f"AI query completed for {user_id}: {actual_cost:.4f} HTR charged")

        # Format response with billing info
        response = f"🤖 **AI Response:**\n\n{ai_response}\n\n"
        response += (
            f"💰 Cost: {actual_cost:.4f} HTR | Balance: {balances[user_id]:.4f} HTR"
        )

        return response

    except Exception as e:
        logger.error(f"Error handling AI query from {user_id}: {e}")
        return (
            "❌ Sorry, I encountered an error processing your request. "
            "Please try again later."
        )


async def handle_text_analysis(user_id: str, message: str, analysis_type: str) -> str:
    """
    Handle specific text analysis requests.

    Args:
        user_id: User's WhatsApp number
        message: Text to analyze
        analysis_type: Type of analysis (summarize, translate, etc.)

    Returns:
        Reply message for the user
    """
    analysis_prompts = {
        "summarize": "Please provide a clear and concise summary of the following text:",
        "translate": "Please translate the following text to English:",
        "analyze": "Please analyze the following text and provide insights:",
        "keywords": "Please extract the key topics and keywords from the following text:",
    }

    if analysis_type not in analysis_prompts:
        return "❌ Unknown analysis type. Available: summarize, translate, analyze, keywords"

    # Create specialized prompt
    prompt = f"{analysis_prompts[analysis_type]}\n\n{message}"

    # Process as regular AI query
    return await handle_ai_query(user_id, prompt)
