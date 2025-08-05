#!/bin/bash

# WhatsPayAI Setup Script
# Sets up the development environment

set -e

echo "🚀 Setting up WhatsPayAI development environment..."

# Check if Python 3.9+ is available
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+' || echo "0.0")
if [[ $(echo "$python_version >= 3.9" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Try to install Hathor dependencies from source (optional)
echo "🔗 Attempting to install Hathor dependencies..."
echo "Note: Hathor packages may not be available on PyPI"
echo "For production use, install from source:"
echo "  pip install git+https://github.com/hathornetwork/hathor-wallet-lib@master"
echo "  pip install git+https://github.com/hathornetwork/hathor-api-client@master"

# Copy environment template
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys and configuration"
fi

# Create state file if it doesn't exist
if [ ! -f "state.json" ]; then
    echo "💾 Creating initial state file..."
    echo '{"balances": {}, "usage_logs": {}, "deposit_queue": {}}' > state.json
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - TWILIO_SID, TWILIO_TOKEN, TWILIO_WHATSAPP_NUMBER (from Twilio)"
echo "   - OPENAI_API_KEY (from OpenAI)"
echo "   - HATHOR_WALLET_SEED (generate a new seed phrase)"
echo ""
echo "2. Run the application:"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "3. Run tests:"
echo "   pytest"
echo ""
echo "4. Format code:"
echo "   black ."
echo "   isort ."
echo ""
echo "📖 See README.md for detailed setup instructions."
