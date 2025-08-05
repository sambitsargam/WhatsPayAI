# WhatsPayAI Deployment Guide

## Quick Deploy to Production

### 1. Environment Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/your-username/WhatsPayAI.git
   cd WhatsPayAI
   ```

2. **Set Up Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### 2. Platform-Specific Deployment

#### Heroku
```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set TWILIO_SID=your_sid
heroku config:set TWILIO_TOKEN=your_token
heroku config:set TWILIO_WHATSAPP_NUMBER=whatsapp:+your_number
heroku config:set OPENAI_API_KEY=your_openai_key
heroku config:set HATHOR_NETWORK=testnet
heroku config:set HATHOR_NODE_URL=https://node1.testnet.hathor.network
heroku config:set HATHOR_WALLET_SEED=your_wallet_seed

# Deploy
git push heroku main
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

#### Docker
```bash
# Build image
docker build -t whatspaiai .

# Run container
docker run -p 8000:8000 --env-file .env whatspaiai
```

#### Docker Compose
```bash
# Start services
docker-compose up -d
```

### 3. Webhook Configuration

1. **Get your public URL** from your deployment platform
2. **Configure Twilio Webhook**:
   - Go to Twilio Console > WhatsApp > Sandbox
   - Set webhook URL to: `https://your-domain.com/webhook`
   - Set HTTP method to: POST

### 4. Testing

1. **Health Check**:
   ```bash
   curl https://your-domain.com/
   ```

2. **Send Test Message**:
   - Send "help" to your WhatsApp Business number
   - Should receive welcome message

### 5. Monitoring

- **Application Stats**: `GET /stats`
- **Logs**: Check platform logs (Heroku logs, Railway logs, etc.)
- **State File**: Monitor `state.json` for balance/usage data

### 6. Scaling Considerations

- **State Persistence**: Consider Redis/Database for production
- **Load Balancing**: Use multiple instances behind load balancer  
- **Monitoring**: Add APM tools (New Relic, DataDog)
- **Security**: Use secrets management (AWS Secrets, Vault)

### 7. Required API Keys

- **Twilio**: Account SID, Auth Token, WhatsApp Number
- **OpenAI**: API Key with sufficient credits
- **Hathor**: Wallet seed phrase (generate new for production)

### 8. Production Security

- Use HTTPS only
- Validate webhook signatures
- Rate limit endpoints
- Monitor for abuse
- Regular security updates

### 9. Backup Strategy

- Backup `state.json` regularly
- Store wallet seed securely
- Monitor balance/usage logs

### 10. Support

- Monitor error logs
- Set up alerts for failures
- Have rollback plan ready

---

**Note**: This is a basic deployment guide. For production use, consider additional security measures, monitoring, and scalability improvements.
