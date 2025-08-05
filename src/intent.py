"""
Intent Classification Module

Classifies incoming WhatsApp messages into specific intents using OpenAI API
with fallback to keyword-based classification.
"""

import logging
import os
import re
from typing import Optional

import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

# Intent definitions
INTENTS = {
    "payment_intent": "User wants to top up their account with HTR tokens",
    "balance_intent": "User wants to check their account balance or usage",
    "ai_query_intent": "User wants to ask AI to process/analyze text or answer questions",
    "help_intent": "User needs help or instructions on how to use the service"
}

# Keyword patterns for fallback classification
PAYMENT_KEYWORDS = [
    r'\btop\s*up\b',
    r'\bdeposit\b',
    r'\bpay\b',
    r'\badd\s+money\b',
    r'\bcharge\b',
    r'\bhtr\b',
    r'\btransfer\b',
    r'\bwallet\b'
]

BALANCE_KEYWORDS = [
    r'\bbalance\b',
    r'\bhow\s+much\b',
    r'\bcredit\b',
    r'\bspent\b',
    r'\busage\b',
    r'\baccount\b',
    r'\bhistory\b'
]

HELP_KEYWORDS = [
    r'\bhelp\b',
    r'\bhow\s+to\b',
    r'\binstructions?\b',
    r'\bcommands?\b',
    r'\bwhat\s+can\b',
    r'\bstart\b',
    r'\bguide\b'
]


def classify_with_openai(message: str) -> Optional[str]:
    """
    Use OpenAI API for zero-shot intent classification.
    
    Args:
        message: The user's message text
        
    Returns:
        Classified intent or None if API fails
    """
    try:
        # Create prompt for intent classification
        intent_list = "\n".join([f"- {intent}: {desc}" for intent, desc in INTENTS.items()])
        
        prompt = f"""
        Classify the following WhatsApp message into one of these intents:
        
        {intent_list}
        
        Message: "{message}"
        
        Return only the intent name (e.g., "payment_intent", "balance_intent", etc.).
        If the message doesn't clearly fit any category, return "ai_query_intent".
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intent classifier for a WhatsApp AI assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20,
            temperature=0
        )
        
        intent = response.choices[0].message.content.strip().lower()
        
        # Validate the returned intent
        if intent in INTENTS:
            logger.info(f"OpenAI classified intent: {intent}")
            return intent
        else:
            logger.warning(f"OpenAI returned invalid intent: {intent}")
            return None
            
    except Exception as e:
        logger.error(f"OpenAI intent classification failed: {e}")
        return None


def classify_with_keywords(message: str) -> str:
    """
    Fallback keyword-based intent classification.
    
    Args:
        message: The user's message text
        
    Returns:
        Classified intent (defaults to ai_query_intent)
    """
    message_lower = message.lower()
    
    # Check for payment intent
    for pattern in PAYMENT_KEYWORDS:
        if re.search(pattern, message_lower):
            logger.info(f"Keyword-based classification: payment_intent (matched: {pattern})")
            return "payment_intent"
    
    # Check for balance intent
    for pattern in BALANCE_KEYWORDS:
        if re.search(pattern, message_lower):
            logger.info(f"Keyword-based classification: balance_intent (matched: {pattern})")
            return "balance_intent"
    
    # Check for help intent
    for pattern in HELP_KEYWORDS:
        if re.search(pattern, message_lower):
            logger.info(f"Keyword-based classification: help_intent (matched: {pattern})")
            return "help_intent"
    
    # Default to AI query
    logger.info("Keyword-based classification: ai_query_intent (default)")
    return "ai_query_intent"


def classify_intent(message: str) -> str:
    """
    Main intent classification function.
    
    First tries OpenAI API, falls back to keyword matching if that fails.
    
    Args:
        message: The user's message text
        
    Returns:
        Classified intent string
    """
    if not message or not message.strip():
        return "help_intent"
    
    # Try OpenAI classification first
    openai_intent = classify_with_openai(message)
    if openai_intent:
        return openai_intent
    
    # Fallback to keyword-based classification
    return classify_with_keywords(message)
