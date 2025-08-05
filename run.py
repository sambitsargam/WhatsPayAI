#!/usr/bin/env python3
"""
WhatsPayAI Startup Script

Run the WhatsApp AI assistant server.
"""

import os
import sys

import uvicorn
from dotenv import load_dotenv

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Load environment variables
load_dotenv()


def main():
    """Start the FastAPI server."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    print(f"🚀 Starting WhatsPayAI server on {host}:{port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🌐 Network: {os.getenv('HATHOR_NETWORK', 'testnet')}")

    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning",
    )


if __name__ == "__main__":
    main()
