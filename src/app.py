"""
WhatsPayAI - Main FastAPI Application

A WhatsApp-based AI assistant that uses feeless Hathor micro-payments for billing
and JSON file-backed state persistence.
"""

import atexit
import json
import logging
import os
from typing import Dict, List

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from .handlers.ai_query import handle_ai_query
from .handlers.balance import handle_balance_query
from .handlers.help import handle_help_request
from .handlers.payment import handle_payment_request
from .intent import classify_intent
from .twilio_client import send_whatsapp_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state - In-memory dictionaries for fast access
balances: Dict[str, float] = {}  # user_id -> HTR balance
usage_logs: Dict[str, List[Dict]] = {}  # user_id -> list of usage entries
deposit_queue: Dict[str, Dict] = {}  # address -> user_info

# FastAPI app instance
app = FastAPI(title="WhatsPayAI", description="WhatsApp AI Assistant with Hathor Payments")

# State file path
STATE_FILE = "state.json"


def load_state():
    """Load application state from JSON file on startup."""
    global balances, usage_logs, deposit_queue
    
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                balances = state.get('balances', {})
                usage_logs = state.get('usage_logs', {})
                deposit_queue = state.get('deposit_queue', {})
            logger.info(f"Loaded state from {STATE_FILE}")
        else:
            logger.info("No state file found, starting with empty state")
    except Exception as e:
        logger.error(f"Error loading state: {e}")


def save_state():
    """Save current application state to JSON file."""
    try:
        state = {
            'balances': balances,
            'usage_logs': usage_logs,
            'deposit_queue': deposit_queue
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info(f"Saved state to {STATE_FILE}")
    except Exception as e:
        logger.error(f"Error saving state: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting WhatsPayAI application...")
    
    # Load existing state
    load_state()
    
    # Import and start scheduler
    from .scheduler import start_scheduler
    start_scheduler()
    
    # Register cleanup function for graceful shutdown
    atexit.register(save_state)
    
    logger.info("WhatsPayAI application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    logger.info("Shutting down WhatsPayAI application...")
    save_state()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "WhatsPayAI is running", "version": "1.0.0"}


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp messages from Twilio webhook.
    
    Expected webhook format from Twilio:
    - From: sender's WhatsApp number
    - Body: message text content
    """
    try:
        # Parse Twilio webhook data
        form_data = await request.form()
        sender = form_data.get("From", "").replace("whatsapp:", "")
        message_body = form_data.get("Body", "").strip()
        
        if not sender or not message_body:
            raise HTTPException(status_code=400, detail="Missing From or Body")
        
        logger.info(f"Received message from {sender}: {message_body}")
        
        # Classify user intent
        intent = classify_intent(message_body)
        logger.info(f"Classified intent: {intent}")
        
        # Route to appropriate handler based on intent
        if intent == "payment_intent":
            response = await handle_payment_request(sender, message_body)
        elif intent == "balance_intent":
            response = await handle_balance_query(sender)
        elif intent == "ai_query_intent":
            response = await handle_ai_query(sender, message_body)
        elif intent == "help_intent":
            response = await handle_help_request()
        else:
            # Default to AI query for unclassified messages
            response = await handle_ai_query(sender, message_body)
        
        # Send response back via WhatsApp
        await send_whatsapp_message(sender, response)
        
        return PlainTextResponse("OK", status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        # Send error message to user
        try:
            await send_whatsapp_message(
                sender, 
                "Sorry, I encountered an error processing your request. Please try again later."
            )
        except:
            pass
        
        return PlainTextResponse("Error", status_code=500)


@app.get("/stats")
async def get_stats():
    """Get application statistics (for monitoring)."""
    return {
        "total_users": len(balances),
        "total_balance": sum(balances.values()),
        "pending_deposits": len(deposit_queue),
        "total_queries": sum(len(logs) for logs in usage_logs.values())
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.app:app", host="0.0.0.0", port=port, reload=True)
