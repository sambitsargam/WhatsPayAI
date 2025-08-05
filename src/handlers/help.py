"""
Help Handler

Provides help and usage instructions to users.
"""

import logging

logger = logging.getLogger(__name__)


async def handle_help_request() -> str:
    """
    Generate help message with usage instructions.
    
    Returns:
        Help message for the user
    """
    help_message = """
🤖 **WhatsPayAI - Your AI Assistant**

Welcome! I'm an AI assistant powered by Hathor blockchain micro-payments. Here's how to use me:

💰 **Account Management:**
• `balance` - Check your HTR balance and usage
• `top up 1 HTR` - Add funds to your account
• `history` - View your recent usage

🤖 **AI Features:**
• Just ask me anything! I can help with:
  - Answering questions
  - Summarizing text
  - Analyzing content
  - General conversation

💡 **Examples:**
• "What's the capital of France?"
• "Summarize this article: [paste text]"
• "Top up 0.5 HTR"
• "What's my balance?"

💳 **Pricing:**
• 0.01 HTR per ~100 tokens
• Most queries cost 0.01-0.05 HTR
• Check your balance anytime

🔧 **Tips:**
• Keep messages under 2000 characters
• You'll get a cost estimate for large queries
• Funds are credited automatically after deposit

❓ **Need More Help?**
Just ask me any question - I'm here to help!

---
Powered by Hathor Network | Fast, feeless transactions
"""
    
    logger.info("Help request handled")
    return help_message.strip()


async def handle_getting_started() -> str:
    """
    Generate getting started guide for new users.
    
    Returns:
        Getting started message
    """
    message = """
🎉 **Welcome to WhatsPayAI!**

Let's get you started in 3 easy steps:

**Step 1: Add Funds** 💰
Type: `top up 1 HTR`
You'll get deposit instructions to fund your account.

**Step 2: Wait for Confirmation** ⏱️
Your deposit will be detected automatically (1-2 minutes).
You'll receive a confirmation message.

**Step 3: Start Using AI!** 🤖
Ask me anything:
• "What's the weather like today?"
• "Explain quantum computing"
• "Summarize this text: [your text]"

**Pricing is Simple:** 💡
Most questions cost just 0.01-0.05 HTR (less than a penny!)

Ready to begin? Type `top up 1 HTR` to start!
"""
    
    return message.strip()


async def handle_pricing_info() -> str:
    """
    Generate detailed pricing information.
    
    Returns:
        Pricing information message
    """
    message = """
💰 **WhatsPayAI Pricing**

**Simple Token-Based Pricing:**
• 0.01 HTR per 100 tokens
• ~4 characters = 1 token

**Typical Costs:**
• Simple question: 0.01-0.02 HTR
• Text summary: 0.02-0.05 HTR
• Detailed analysis: 0.05-0.10 HTR
• Long conversation: 0.10+ HTR

**Examples:**
• "What's 2+2?" → ~0.01 HTR
• "Explain AI" → ~0.02 HTR
• "Summarize 500-word article" → ~0.05 HTR

**No Hidden Fees:**
✅ No monthly subscriptions
✅ No minimum balance
✅ Pay only for what you use
✅ Transparent token counting

**Balance Management:**
• Check anytime: Type `balance`
• Add funds: Type `top up X HTR`
• Low balance warnings included

Ready to try? Your first question might cost just 0.01 HTR!
"""
    
    return message.strip()


async def handle_technical_info() -> str:
    """
    Generate technical information about the service.
    
    Returns:
        Technical information message
    """
    message = """
🔧 **Technical Information**

**Powered By:**
• 🤖 OpenAI GPT-3.5 Turbo
• ⚡ Hathor Network (feeless transactions)
• 📱 Twilio WhatsApp API
• ☁️ FastAPI backend

**Key Features:**
• ⚡ Real-time payment processing
• 🔄 Automatic balance management
• 📊 Detailed usage tracking
• 🛡️ Secure wallet integration

**Network Details:**
• Blockchain: Hathor Network
• Payment Method: HTR tokens
• Confirmation Time: ~30 seconds
• Transaction Fees: None (feeless)

**Privacy & Security:**
• Messages are not stored permanently
• Payments are blockchain-verified
• No personal data collection beyond WhatsApp number

**Supported Features:**
• Natural language queries
• Text summarization
• Content analysis
• Multi-language support

Questions about the technology? Just ask!
"""
    
    return message.strip()


def get_command_list() -> str:
    """
    Generate list of available commands.
    
    Returns:
        Command list message
    """
    commands = """
📋 **Available Commands:**

**Balance & Payments:**
• `balance` - Check account balance
• `top up X HTR` - Add funds (e.g., "top up 1 HTR")
• `history` - View usage history

**Help & Info:**
• `help` - Show this help message
• `start` - Getting started guide
• `pricing` - Pricing information
• `commands` - List all commands

**AI Features:**
Just ask naturally! No special commands needed.
• Ask questions
• Request summaries
• Analyze text
• General conversation

**Examples:**
• "What's my balance?"
• "Top up 0.5 HTR"
• "Explain blockchain technology"
• "Summarize this article: [paste text]"

Type any command or question to get started!
"""
    
    return commands.strip()
