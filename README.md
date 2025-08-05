# WhatsPayAI 🤖💳

A WhatsApp-based AI assistant that uses feeless Hathor Network micro-payments for billing and JSON file-backed state persistence. No external databases or SQL required!

## Features ✨

- 🤖 **AI-Powered Assistance**: Integration with OpenAI GPT-3.5 for natural language processing
- ⚡ **Hathor Network Payments**: Fast, feeless micro-payments for usage billing
- 📱 **WhatsApp Integration**: Easy communication via Twilio WhatsApp API
- 💾 **Simple State Management**: JSON file-backed persistence with in-memory caching
- 🔄 **Real-time Processing**: Automatic deposit detection and balance management
- 📊 **Usage Tracking**: Detailed logs of all AI interactions and costs
- 🛡️ **Secure**: No personal data storage beyond phone numbers

## Tech Stack 🛠️

- **Backend**: Python 3.9+, FastAPI, APScheduler
- **AI**: OpenAI API (GPT-3.5 Turbo)
- **Messaging**: Twilio WhatsApp API
- **Blockchain**: Hathor Network (hathor-wallet-lib, hathor-api-client)
- **Storage**: JSON files for state persistence
- **Testing**: pytest, unittest.mock
- **CI/CD**: GitHub Actions with flake8, black, coverage

## Quick Start 🚀

### 1. Clone and Setup

```bash
git clone https://github.com/your-username/WhatsPayAI.git
cd WhatsPayAI
./setup.sh
```

### 2. Configure Environment

Edit `.env` file with your API keys:

```env
# Twilio (WhatsApp)
TWILIO_SID=your_twilio_account_sid
TWILIO_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Hathor Network
HATHOR_NETWORK=testnet
HATHOR_NODE_URL=https://node1.testnet.hathor.network
HATHOR_WALLET_SEED=your_wallet_seed_phrase

# Application
DEBUG=True
PORT=8000
COST_PER_100_TOKENS=0.01
```

### 3. Run the Application

```bash
source venv/bin/activate
python run.py
```

The server will start on `http://localhost:8000`

### 4. Setup Twilio Webhook

Configure your Twilio WhatsApp webhook URL to:
```
https://your-domain.com/webhook
```

## Usage Examples 💬

Users can interact with WhatsPayAI via WhatsApp messages:

### Payment Commands
```
"Top up 1 HTR"          → Get deposit instructions
"What's my balance?"    → Check account balance
"Usage history"         → View recent activity
```

### AI Queries
```
"What's the capital of France?"
"Summarize this article: [paste text]"
"Explain quantum computing"
"Translate 'Hello' to Spanish"
```

### Help Commands
```
"Help"                  → Show usage instructions
"Commands"              → List available commands
"Pricing"               → Show pricing information
```

## API Endpoints 🔌

- `POST /webhook` - Twilio WhatsApp webhook endpoint
- `GET /` - Health check
- `GET /stats` - Application statistics

## Pricing Model 💰

- **Cost**: 0.01 HTR per 100 tokens (~$0.005 USD)
- **Typical Query**: 0.01-0.05 HTR
- **No Monthly Fees**: Pay only for what you use
- **Automatic Billing**: Deducted from your balance instantly

## Development 👩‍💻

### Install Development Dependencies

```bash
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_intent.py
```

### Code Formatting

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint code
flake8 .
```

### Project Structure

```
WhatsPayAI/
├── src/                    # Source code
│   ├── app.py             # FastAPI application
│   ├── intent.py          # Intent classification
│   ├── twilio_client.py   # WhatsApp messaging
│   ├── hathor_client.py   # Blockchain integration
│   ├── scheduler.py       # Background jobs
│   └── handlers/          # Message handlers
│       ├── ai_query.py    # AI query processing
│       ├── balance.py     # Balance queries
│       ├── help.py        # Help messages
│       └── payment.py     # Payment processing
├── tests/                 # Test suite
├── .github/workflows/     # CI/CD pipelines
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Deployment 🚀

### Using Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

### Using Heroku

```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set TWILIO_SID=your_sid
heroku config:set TWILIO_TOKEN=your_token
# ... set other environment variables
git push heroku main
```

### Using Railway/Render

1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy automatically on push

## Security Considerations 🔒

- **Environment Variables**: Never commit `.env` files to version control
- **API Keys**: Use secure key management in production
- **HTTPS**: Always use HTTPS for webhook endpoints
- **Rate Limiting**: Consider implementing rate limiting for production
- **Input Validation**: All user inputs are validated and sanitized

## Monitoring & Observability 📊

### Application Statistics

Access `/stats` endpoint for:
- Total users
- Total HTR balance
- Pending deposits
- Query volume

### Logging

The application logs:
- All incoming messages
- Payment transactions
- AI query costs
- Error conditions

### Health Checks

Use the root endpoint `/` for health monitoring.

## Troubleshooting 🔧

### Common Issues

**1. Twilio Webhook Not Working**
- Check webhook URL is accessible publicly
- Verify HTTPS is enabled
- Check Twilio credentials in `.env`

**2. OpenAI API Errors**
- Verify API key is valid
- Check OpenAI account has sufficient credits
- Review rate limits

**3. Hathor Network Issues**
- Ensure testnet node URL is accessible
- Check wallet seed phrase is valid
- Verify network connectivity

**4. State File Corruption**
- Backup `state.json` regularly
- The file will be recreated if deleted

### Debug Mode

Set `DEBUG=True` in `.env` for verbose logging.

### Test Environment

Run tests to verify all components:
```bash
pytest -v
```

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings for all functions
- Maintain test coverage above 90%

## Resources 📚

- [Hathor Network Documentation](https://docs.hathor.network)
- [Hathor GitHub Repository](https://github.com/hathornetwork)
- [Twilio WhatsApp API Docs](https://www.twilio.com/docs/whatsapp)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

- GitHub Issues: Report bugs and feature requests
- Documentation: Check this README and inline code comments  
- Community: Join the Hathor Network Discord

---

**Made with ❤️ for the Hathor Network ecosystem**
