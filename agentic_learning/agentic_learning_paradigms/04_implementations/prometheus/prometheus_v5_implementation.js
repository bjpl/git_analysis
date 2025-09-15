/**
 * Prometheus v5 - Next Generation Monitoring with Integrated Voice & Text Agents
 * 
 * This implementation extends Prometheus v4 with native AI agent capabilities
 * for voice and text-based monitoring interactions.
 * 
 * @version 5.0.0
 * @author AI-Enhanced Monitoring Team
 */

// ============================================================================
// Core Dependencies
// ============================================================================

const express = require('express');
const WebSocket = require('ws');
const { Server } = require('socket.io');
const Redis = require('ioredis');
const { EventEmitter } = require('events');
const crypto = require('crypto');

// AI/ML Dependencies
const { OpenAI } = require('openai');
const { LangChain } = require('langchain');
const { PromQLParser } = require('./lib/promql-parser');
const { WhisperAPI } = require('./lib/whisper-api');
const { ElevenLabsAPI } = require('./lib/elevenlabs-api');

// Prometheus Core
const { PrometheusClient } = require('prom-client');
const { AlertManager } = require('./lib/alertmanager');
const { RemoteWriteReceiver } = require('./lib/remote-write');

// ============================================================================
// Prometheus v5 Core Architecture
// ============================================================================

class PrometheusV5 extends EventEmitter {
    constructor(config = {}) {
        super();
        
        this.config = {
            port: config.port || 9090,
            voiceEnabled: config.voiceEnabled !== false,
            textEnabled: config.textEnabled !== false,
            aiModel: config.aiModel || 'gpt-4-turbo',
            security: {
                authEnabled: config.security?.authEnabled !== false,
                encryption: config.security?.encryption || 'TLS1.3',
                rbac: config.security?.rbac || true
            },
            agents: {
                maxConcurrent: config.agents?.maxConcurrent || 10,
                timeout: config.agents?.timeout || 30000,
                memory: config.agents?.memory || true
            },
            ...config
        };
        
        this.initialize();
    }
    
    async initialize() {
        // Core components
        this.metricsStore = new MetricsStore();
        this.alertManager = new AlertManager();
        this.queryEngine = new QueryEngine();
        
        // AI Agent components
        this.voiceAgent = new VoiceAgent(this.config);
        this.textAgent = new TextAgent(this.config);
        this.nlpProcessor = new NLPProcessor(this.config);
        
        // Communication layer
        this.wsServer = new WebSocketServer(this.config);
        this.apiServer = new APIServer(this.config);
        
        // Security layer
        this.authManager = new AuthenticationManager(this.config.security);
        
        console.log('🚀 Prometheus v5 initialized with AI agents');
    }
    
    async start() {
        await this.apiServer.start();
        await this.wsServer.start();
        await this.voiceAgent.initialize();
        await this.textAgent.initialize();
        
        this.emit('ready');
        console.log(`✅ Prometheus v5 running on port ${this.config.port}`);
    }
}

// ============================================================================
// Voice Agent Implementation
// ============================================================================

class VoiceAgent {
    constructor(config) {
        this.config = config;
        this.whisper = new WhisperAPI(config.whisperApiKey);
        this.elevenLabs = new ElevenLabsAPI(config.elevenLabsApiKey);
        this.recognitionActive = false;
        this.sessions = new Map();
    }
    
    async initialize() {
        // Initialize voice models
        await this.whisper.initialize();
        await this.elevenLabs.initialize();
        
        // Set up wake word detection
        this.wakeWordDetector = new WakeWordDetector(['prometheus', 'hey metrics']);
        
        console.log('🎤 Voice agent initialized');
    }
    
    async processVoiceInput(audioStream, sessionId) {
        try {
            // Speech to text
            const transcript = await this.whisper.transcribe(audioStream);
            console.log(`Voice input: "${transcript}"`);
            
            // Process intent
            const intent = await this.detectIntent(transcript);
            
            // Execute action
            const response = await this.executeVoiceCommand(intent, sessionId);
            
            // Text to speech
            const audioResponse = await this.elevenLabs.synthesize(response.text);
            
            return {
                transcript,
                intent,
                response: response.data,
                audio: audioResponse,
                text: response.text
            };
        } catch (error) {
            console.error('Voice processing error:', error);
            return this.handleVoiceError(error);
        }
    }
    
    async detectIntent(transcript) {
        const intents = {
            QUERY_METRICS: /(?:show|get|display|what|tell).*(?:metrics?|values?|data)/i,
            CHECK_ALERTS: /(?:any|show|what|check).*(?:alerts?|warnings?|issues?)/i,
            SYSTEM_STATUS: /(?:status|health|how|check).*(?:system|cluster|nodes?)/i,
            CREATE_ALERT: /(?:create|add|set).*(?:alert|notification|warning)/i,
            SILENCE_ALERT: /(?:silence|mute|disable|stop).*(?:alert|notification)/i,
            EXPLAIN_METRIC: /(?:explain|what is|describe|tell me about)/i,
            TREND_ANALYSIS: /(?:trend|forecast|predict|analyze)/i,
            HELP: /(?:help|what can|commands?|options?)/i
        };
        
        for (const [intent, pattern] of Object.entries(intents)) {
            if (pattern.test(transcript)) {
                return {
                    type: intent,
                    transcript,
                    confidence: 0.85,
                    entities: this.extractEntities(transcript)
                };
            }
        }
        
        // Fallback to AI intent detection
        return await this.nlpProcessor.detectIntent(transcript);
    }
    
    async executeVoiceCommand(intent, sessionId) {
        const session = this.getOrCreateSession(sessionId);
        
        switch (intent.type) {
            case 'QUERY_METRICS':
                return await this.queryMetricsVoice(intent.entities, session);
                
            case 'CHECK_ALERTS':
                return await this.checkAlertsVoice(session);
                
            case 'SYSTEM_STATUS':
                return await this.getSystemStatusVoice(session);
                
            case 'CREATE_ALERT':
                return await this.createAlertVoice(intent.entities, session);
                
            case 'SILENCE_ALERT':
                return await this.silenceAlertVoice(intent.entities, session);
                
            case 'EXPLAIN_METRIC':
                return await this.explainMetricVoice(intent.entities, session);
                
            case 'TREND_ANALYSIS':
                return await this.analyzeTrendVoice(intent.entities, session);
                
            case 'HELP':
                return this.getVoiceHelp();
                
            default:
                return await this.handleNaturalLanguageQuery(intent.transcript, session);
        }
    }
    
    async queryMetricsVoice(entities, session) {
        const promql = await this.nlpProcessor.toPromQL(entities);
        const results = await this.queryEngine.execute(promql);
        
        const summary = this.summarizeMetrics(results);
        return {
            text: summary,
            data: results,
            promql
        };
    }
    
    summarizeMetrics(results) {
        if (!results || results.length === 0) {
            return "No metrics found for your query.";
        }
        
        const count = results.length;
        const latest = results[0];
        
        let summary = `Found ${count} metric${count > 1 ? 's' : ''}. `;
        summary += `The latest value is ${latest.value} ${latest.unit || ''}. `;
        
        if (count > 1) {
            const avg = results.reduce((a, b) => a + b.value, 0) / count;
            summary += `Average is ${avg.toFixed(2)}. `;
        }
        
        return summary;
    }
    
    getOrCreateSession(sessionId) {
        if (!this.sessions.has(sessionId)) {
            this.sessions.set(sessionId, {
                id: sessionId,
                context: [],
                startTime: Date.now(),
                lastActivity: Date.now()
            });
        }
        return this.sessions.get(sessionId);
    }
}

// ============================================================================
// Text Agent Implementation
// ============================================================================

class TextAgent {
    constructor(config) {
        this.config = config;
        this.langchain = new LangChain({
            model: config.aiModel,
            temperature: 0.3
        });
        this.conversations = new Map();
    }
    
    async initialize() {
        // Initialize LangChain with Prometheus tools
        await this.langchain.addTools([
            new PromQLTool(),
            new AlertManagerTool(),
            new MetricsExplainerTool(),
            new TrendAnalysisTool(),
            new AutomationTool()
        ]);
        
        console.log('💬 Text agent initialized');
    }
    
    async processTextInput(message, conversationId, user) {
        try {
            const conversation = this.getOrCreateConversation(conversationId);
            
            // Add user message to context
            conversation.messages.push({
                role: 'user',
                content: message,
                timestamp: Date.now()
            });
            
            // Process with LangChain
            const response = await this.langchain.process({
                message,
                context: conversation.messages,
                user,
                tools: ['promql', 'alerts', 'explain', 'automate']
            });
            
            // Add assistant response to context
            conversation.messages.push({
                role: 'assistant',
                content: response.text,
                data: response.data,
                timestamp: Date.now()
            });
            
            return {
                text: response.text,
                data: response.data,
                suggestions: response.suggestions,
                visualizations: response.visualizations
            };
        } catch (error) {
            console.error('Text processing error:', error);
            return this.handleTextError(error);
        }
    }
    
    getOrCreateConversation(conversationId) {
        if (!this.conversations.has(conversationId)) {
            this.conversations.set(conversationId, {
                id: conversationId,
                messages: [],
                startTime: Date.now(),
                metadata: {}
            });
        }
        return this.conversations.get(conversationId);
    }
}

// ============================================================================
// Natural Language Processing
// ============================================================================

class NLPProcessor {
    constructor(config) {
        this.config = config;
        this.openai = new OpenAI({ apiKey: config.openaiApiKey });
        this.promqlParser = new PromQLParser();
    }
    
    async toPromQL(naturalLanguage) {
        const prompt = `
            Convert this natural language query to PromQL:
            "${naturalLanguage}"
            
            Context: Prometheus monitoring system
            Available metrics: cpu_usage, memory_usage, disk_io, network_traffic, http_requests
            
            Return only the PromQL query, no explanation.
        `;
        
        const response = await this.openai.chat.completions.create({
            model: this.config.aiModel,
            messages: [{ role: 'user', content: prompt }],
            temperature: 0.2
        });
        
        const promql = response.choices[0].message.content.trim();
        
        // Validate PromQL syntax
        try {
            this.promqlParser.parse(promql);
            return promql;
        } catch (error) {
            console.error('Invalid PromQL generated:', promql, error);
            throw new Error('Failed to generate valid PromQL query');
        }
    }
    
    async detectIntent(text) {
        const response = await this.openai.chat.completions.create({
            model: this.config.aiModel,
            messages: [{
                role: 'system',
                content: 'Detect the intent of monitoring-related queries. Return JSON with type, entities, and confidence.'
            }, {
                role: 'user',
                content: text
            }],
            response_format: { type: 'json_object' }
        });
        
        return JSON.parse(response.choices[0].message.content);
    }
}

// ============================================================================
// WebSocket Real-Time Communication
// ============================================================================

class WebSocketServer {
    constructor(config) {
        this.config = config;
        this.connections = new Map();
    }
    
    async start() {
        this.io = new Server({
            cors: {
                origin: this.config.corsOrigin || '*',
                methods: ['GET', 'POST']
            }
        });
        
        this.io.on('connection', (socket) => {
            console.log(`Client connected: ${socket.id}`);
            
            this.connections.set(socket.id, {
                socket,
                subscriptions: new Set(),
                authenticated: false
            });
            
            // Handle authentication
            socket.on('authenticate', async (token) => {
                const isValid = await this.authManager.validateToken(token);
                if (isValid) {
                    this.connections.get(socket.id).authenticated = true;
                    socket.emit('authenticated');
                } else {
                    socket.emit('auth_error', 'Invalid token');
                    socket.disconnect();
                }
            });
            
            // Handle metric subscriptions
            socket.on('subscribe_metrics', (query) => {
                if (!this.isAuthenticated(socket.id)) return;
                
                const subscription = this.metricsStore.subscribe(query, (data) => {
                    socket.emit('metrics_update', data);
                });
                
                this.connections.get(socket.id).subscriptions.add(subscription);
            });
            
            // Handle alert subscriptions
            socket.on('subscribe_alerts', (filter) => {
                if (!this.isAuthenticated(socket.id)) return;
                
                const subscription = this.alertManager.subscribe(filter, (alert) => {
                    socket.emit('alert', alert);
                });
                
                this.connections.get(socket.id).subscriptions.add(subscription);
            });
            
            // Handle voice streams
            socket.on('voice_stream_start', () => {
                if (!this.isAuthenticated(socket.id)) return;
                this.handleVoiceStream(socket);
            });
            
            // Handle text messages
            socket.on('text_message', async (message) => {
                if (!this.isAuthenticated(socket.id)) return;
                
                const response = await this.textAgent.processTextInput(
                    message.text,
                    socket.id,
                    message.user
                );
                
                socket.emit('text_response', response);
            });
            
            // Handle disconnection
            socket.on('disconnect', () => {
                const connection = this.connections.get(socket.id);
                if (connection) {
                    // Clean up subscriptions
                    connection.subscriptions.forEach(sub => sub.unsubscribe());
                    this.connections.delete(socket.id);
                }
                console.log(`Client disconnected: ${socket.id}`);
            });
        });
        
        const port = this.config.wsPort || 3001;
        this.io.listen(port);
        console.log(`WebSocket server listening on port ${port}`);
    }
    
    isAuthenticated(socketId) {
        return this.connections.get(socketId)?.authenticated || false;
    }
    
    handleVoiceStream(socket) {
        const audioChunks = [];
        
        socket.on('voice_data', (chunk) => {
            audioChunks.push(chunk);
        });
        
        socket.on('voice_stream_end', async () => {
            const audioBuffer = Buffer.concat(audioChunks);
            const response = await this.voiceAgent.processVoiceInput(
                audioBuffer,
                socket.id
            );
            
            socket.emit('voice_response', response);
        });
    }
}

// ============================================================================
// REST API Server
// ============================================================================

class APIServer {
    constructor(config) {
        this.config = config;
        this.app = express();
        this.setupMiddleware();
        this.setupRoutes();
    }
    
    setupMiddleware() {
        this.app.use(express.json());
        this.app.use(express.urlencoded({ extended: true }));
        
        // Security middleware
        this.app.use(helmet());
        this.app.use(cors(this.config.cors));
        
        // Rate limiting
        this.app.use(rateLimit({
            windowMs: 60 * 1000,
            max: 100
        }));
        
        // Authentication middleware
        this.app.use('/api/v5/*', this.authMiddleware.bind(this));
    }
    
    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({ status: 'healthy', version: '5.0.0' });
        });
        
        // Metrics API
        this.app.get('/api/v5/query', this.handleQuery.bind(this));
        this.app.get('/api/v5/query_range', this.handleQueryRange.bind(this));
        this.app.post('/api/v5/query/natural', this.handleNaturalQuery.bind(this));
        
        // Alerts API
        this.app.get('/api/v5/alerts', this.handleGetAlerts.bind(this));
        this.app.post('/api/v5/alerts', this.handleCreateAlert.bind(this));
        this.app.post('/api/v5/alerts/:id/silence', this.handleSilenceAlert.bind(this));
        
        // Agent API
        this.app.post('/api/v5/agent/text', this.handleTextAgent.bind(this));
        this.app.post('/api/v5/agent/voice', this.handleVoiceAgent.bind(this));
        
        // Automation API
        this.app.post('/api/v5/automation/runbook', this.handleRunbook.bind(this));
        this.app.get('/api/v5/automation/workflows', this.handleGetWorkflows.bind(this));
    }
    
    async authMiddleware(req, res, next) {
        const token = req.headers.authorization?.split(' ')[1];
        
        if (!token) {
            return res.status(401).json({ error: 'No token provided' });
        }
        
        const isValid = await this.authManager.validateToken(token);
        if (!isValid) {
            return res.status(401).json({ error: 'Invalid token' });
        }
        
        req.user = await this.authManager.getUserFromToken(token);
        next();
    }
    
    async handleNaturalQuery(req, res) {
        try {
            const { query } = req.body;
            const promql = await this.nlpProcessor.toPromQL(query);
            const results = await this.queryEngine.execute(promql);
            
            res.json({
                natural_query: query,
                promql,
                results,
                explanation: await this.explainQuery(promql)
            });
        } catch (error) {
            res.status(400).json({ error: error.message });
        }
    }
    
    async handleTextAgent(req, res) {
        try {
            const { message, conversationId } = req.body;
            const response = await this.textAgent.processTextInput(
                message,
                conversationId || crypto.randomUUID(),
                req.user
            );
            
            res.json(response);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async handleVoiceAgent(req, res) {
        try {
            const audioBuffer = req.body.audio;
            const sessionId = req.body.sessionId || crypto.randomUUID();
            
            const response = await this.voiceAgent.processVoiceInput(
                Buffer.from(audioBuffer, 'base64'),
                sessionId
            );
            
            res.json({
                ...response,
                audio: response.audio.toString('base64')
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async start() {
        return new Promise((resolve) => {
            this.server = this.app.listen(this.config.port, () => {
                console.log(`API server listening on port ${this.config.port}`);
                resolve();
            });
        });
    }
}

// ============================================================================
// Security & Authentication
// ============================================================================

class AuthenticationManager {
    constructor(config) {
        this.config = config;
        this.sessions = new Map();
        this.tokenSecret = config.tokenSecret || crypto.randomBytes(32).toString('hex');
    }
    
    async validateToken(token) {
        try {
            const decoded = jwt.verify(token, this.tokenSecret);
            return this.sessions.has(decoded.sessionId);
        } catch {
            return false;
        }
    }
    
    async getUserFromToken(token) {
        const decoded = jwt.verify(token, this.tokenSecret);
        return this.sessions.get(decoded.sessionId)?.user;
    }
    
    async createSession(user) {
        const sessionId = crypto.randomUUID();
        const token = jwt.sign(
            { sessionId, userId: user.id },
            this.tokenSecret,
            { expiresIn: '24h' }
        );
        
        this.sessions.set(sessionId, {
            user,
            createdAt: Date.now(),
            lastActivity: Date.now()
        });
        
        return { token, sessionId };
    }
}

// ============================================================================
// Export and Initialization
// ============================================================================

module.exports = {
    PrometheusV5,
    VoiceAgent,
    TextAgent,
    NLPProcessor,
    WebSocketServer,
    APIServer,
    AuthenticationManager
};

// Auto-start if run directly
if (require.main === module) {
    const prometheus = new PrometheusV5({
        port: process.env.PORT || 9090,
        wsPort: process.env.WS_PORT || 3001,
        voiceEnabled: true,
        textEnabled: true,
        aiModel: process.env.AI_MODEL || 'gpt-4-turbo',
        whisperApiKey: process.env.WHISPER_API_KEY,
        elevenLabsApiKey: process.env.ELEVENLABS_API_KEY,
        openaiApiKey: process.env.OPENAI_API_KEY,
        security: {
            authEnabled: true,
            tokenSecret: process.env.TOKEN_SECRET
        }
    });
    
    prometheus.start().then(() => {
        console.log('🎯 Prometheus v5 with AI Agents is running!');
        console.log('📊 Metrics API: http://localhost:9090');
        console.log('🔌 WebSocket: ws://localhost:3001');
        console.log('🎤 Voice Agent: Enabled');
        console.log('💬 Text Agent: Enabled');
    }).catch(error => {
        console.error('Failed to start Prometheus v5:', error);
        process.exit(1);
    });
}