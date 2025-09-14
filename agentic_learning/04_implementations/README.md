# Prometheus AI-Enhanced Implementations

This directory contains next-generation implementations of Prometheus monitoring system with integrated AI capabilities.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Redis (for session management)
- OpenAI API key
- Optional: Whisper API key (for voice)
- Optional: ElevenLabs API key (for TTS)

### Installation

```bash
# Clone the repository
git clone <repository>
cd agentic_learning

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start Prometheus v5
npm start
```

## 📁 Directory Structure

```
implementations/
├── INDEX.md                          # Version history and changelog
├── README.md                          # This file
├── prometheus_v5_implementation.js    # Main v5 implementation
└── lib/                              # Supporting libraries (future)
    ├── promql-parser.js
    ├── whisper-api.js
    ├── elevenlabs-api.js
    └── alertmanager.js
```

## 🎯 Current Implementation: Prometheus v5

### Key Features

#### 🎤 Voice Agent
- Natural voice commands for monitoring
- Wake word activation ("Hey Prometheus")
- Voice alerts and notifications
- Hands-free incident response

#### 💬 Text Agent  
- Conversational monitoring interface
- Natural language to PromQL conversion
- Interactive troubleshooting
- Automated report generation

#### 🔌 Real-Time Communication
- WebSocket streaming for live metrics
- Server-sent events for alerts
- Bidirectional agent communication
- Low-latency voice processing

#### 🔒 Enhanced Security
- OAuth2/OIDC authentication
- Role-based access control (RBAC)
- Audit logging for all queries
- Encrypted agent communications

## 🛠️ Development

### Running in Development Mode

```bash
# Start with nodemon for auto-reload
npm run dev

# Run tests
npm test

# Lint code
npm run lint
```

### Docker Deployment

```bash
# Build Docker image
npm run docker:build

# Run container
npm run docker:run
```

## 📊 API Endpoints

### Core Metrics API
- `GET /api/v5/query` - Execute PromQL query
- `GET /api/v5/query_range` - Range query
- `POST /api/v5/query/natural` - Natural language query

### Agent API
- `POST /api/v5/agent/text` - Text agent interaction
- `POST /api/v5/agent/voice` - Voice agent processing

### WebSocket Events
- `authenticate` - Authenticate connection
- `subscribe_metrics` - Subscribe to metric updates
- `subscribe_alerts` - Subscribe to alerts
- `text_message` - Send text to agent
- `voice_stream_start` - Start voice streaming

## 🧪 Testing the Agents

### Text Agent Example

```javascript
// Send natural language query
POST /api/v5/agent/text
{
  "message": "Show me CPU usage for the web servers",
  "conversationId": "conv-123"
}

// Response
{
  "text": "Here's the CPU usage for web servers...",
  "data": {...},
  "promql": "avg(rate(cpu_usage{job='web'}[5m]))"
}
```

### Voice Agent Example

```javascript
// Process voice command
POST /api/v5/agent/voice
{
  "audio": "<base64_audio>",
  "sessionId": "session-456"
}

// Response
{
  "transcript": "What's the current error rate?",
  "intent": "QUERY_METRICS",
  "response": {...},
  "audio": "<base64_tts_response>"
}
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

- `AI_MODEL` - OpenAI model to use (gpt-4-turbo)
- `ENABLE_VOICE_AGENT` - Enable/disable voice
- `ENABLE_TEXT_AGENT` - Enable/disable text
- `MAX_CONCURRENT_AGENTS` - Agent concurrency limit
- `AGENT_TIMEOUT_MS` - Agent response timeout

### Feature Flags

Toggle features without code changes:

- `ENABLE_AUTOMATION` - Automated remediation
- `ENABLE_PREDICTIVE_ALERTS` - ML-based predictions
- `SELF_MONITORING` - Monitor Prometheus itself

## 📈 Performance Considerations

### Optimization Tips

1. **Caching**: Redis caches frequent queries
2. **Rate Limiting**: Prevents agent abuse
3. **Connection Pooling**: Reuse WebSocket connections
4. **Query Optimization**: PromQL query caching
5. **Voice Streaming**: Chunked audio processing

### Benchmarks

- Text query response: <500ms average
- Voice recognition: <2s end-to-end
- WebSocket latency: <50ms
- Concurrent agents: 10-100 depending on resources

## 🐛 Troubleshooting

### Common Issues

1. **Voice not working**: Check Whisper API key
2. **Text agent timeout**: Increase AGENT_TIMEOUT_MS
3. **WebSocket disconnects**: Check firewall/proxy
4. **Authentication fails**: Verify TOKEN_SECRET
5. **High latency**: Enable Redis caching

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=debug npm start

# Check agent logs
tail -f prometheus-v5.log | grep agent
```

## 🤝 Contributing

1. Check INDEX.md for version guidelines
2. Add tests for new features
3. Update documentation
4. Follow semantic versioning
5. Create PR with description

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [LangChain Docs](https://docs.langchain.com/)
- [WebSocket Guide](https://socket.io/docs/)

## 📝 License

Apache License 2.0 - See LICENSE file

---

**Need Help?** Open an issue or check the [INDEX.md](INDEX.md) for detailed version information.