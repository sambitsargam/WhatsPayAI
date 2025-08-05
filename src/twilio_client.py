"""
Twilio WhatsApp Client

Handles sending WhatsApp messages via Twilio REST API.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Twilio configuration
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Initialize Twilio client
twilio_client = None
if TWILIO_SID and TWILIO_TOKEN:
    try:
        twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
        logger.info("Twilio client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {e}")
else:
    logger.warning("Twilio credentials not found in environment variables")


async def send_whatsapp_message(to_number: str, message: str) -> bool:
    """
    Send a WhatsApp message via Twilio.
    
    Args:
        to_number: Recipient's phone number (without whatsapp: prefix)
        message: Message content to send
        
    Returns:
        True if message sent successfully, False otherwise
    """
    if not twilio_client:
        logger.error("Twilio client not initialized")
        return False
    
    if not TWILIO_WHATSAPP_NUMBER:
        logger.error("Twilio WhatsApp number not configured")
        return False
    
    try:
        # Ensure recipient number has whatsapp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        # Send message via Twilio
        message_instance = twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )
        
        logger.info(f"Message sent successfully. SID: {message_instance.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        return False


def validate_phone_number(phone_number: str) -> Optional[str]:
    """
    Validate and normalize phone number format.
    
    Args:
        phone_number: Raw phone number string
        
    Returns:
        Normalized phone number or None if invalid
    """
    if not phone_number:
        return None
    
    # Remove whatsapp: prefix if present
    if phone_number.startswith("whatsapp:"):
        phone_number = phone_number[9:]
    
    # Basic validation - should start with + and contain only digits
    if phone_number.startswith("+") and phone_number[1:].isdigit():
        return phone_number
    
    logger.warning(f"Invalid phone number format: {phone_number}")
    return None


async def send_whatsapp_message_safe(to_number: str, message: str) -> bool:
    """
    Safe wrapper for sending WhatsApp messages with validation.
    
    Args:
        to_number: Recipient's phone number
        message: Message content to send
        
    Returns:
        True if message sent successfully, False otherwise
    """
    # Validate phone number
    validated_number = validate_phone_number(to_number)
    if not validated_number:
        logger.error(f"Invalid phone number: {to_number}")
        return False
    
    # Validate message content
    if not message or not message.strip():
        logger.error("Empty message content")
        return False
    
    # Truncate message if too long (WhatsApp limit is ~4096 characters)
    if len(message) > 4000:
        message = message[:3997] + "..."
        logger.warning("Message truncated due to length limit")
    
    return await send_whatsapp_message(validated_number, message)
