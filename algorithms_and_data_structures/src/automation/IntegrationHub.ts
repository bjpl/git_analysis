import { EventEmitter } from 'events';
import axios, { AxiosRequestConfig } from 'axios';
import * as crypto from 'crypto';
import { promises as fs } from 'fs';
import { WorkflowEngine } from './WorkflowEngine';

export interface Integration {
  id: string;
  name: string;
  type: IntegrationType;
  config: Record<string, any>;
  enabled: boolean;
  createdAt: Date;
  updatedAt: Date;
  lastUsed?: Date;
  usageCount: number;
  rateLimits?: RateLimit;
  authentication?: AuthConfig;
}

export type IntegrationType = 
  | 'github_actions'
  | 'webhook'
  | 'api_gateway'
  | 'ci_cd'
  | 'slack'
  | 'discord'
  | 'email'
  | 'database'
  | 'cloud_storage'
  | 'monitoring';

export interface AuthConfig {
  type: 'none' | 'api_key' | 'bearer_token' | 'oauth2' | 'basic' | 'custom';
  credentials: Record<string, any>;
  refreshToken?: string;
  expiresAt?: Date;
}

export interface RateLimit {
  requests: number;
  window: number; // in milliseconds
  current: number;
  resetTime: Date;
}

export interface WebhookConfig {
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  secret?: string;
  retries?: number;
  timeout?: number;
}

export interface GitHubActionsConfig {
  repository: string;
  workflow: string;
  branch?: string;
  inputs?: Record<string, any>;
  token: string;
}

export interface APIGatewayConfig {
  baseURL: string;
  endpoints: APIEndpoint[];
  defaultHeaders?: Record<string, string>;
  rateLimitConfig?: RateLimit;
}

export interface APIEndpoint {
  path: string;
  method: string;
  description?: string;
  parameters?: APIParameter[];
  authentication?: AuthConfig;
}

export interface APIParameter {
  name: string;
  type: 'query' | 'path' | 'header' | 'body';
  required: boolean;
  description?: string;
}

export interface IntegrationEvent {
  id: string;
  integrationId: string;
  type: string;
  data: any;
  timestamp: Date;
  processed: boolean;
  error?: string;
}

export class IntegrationHub extends EventEmitter {
  private integrations = new Map<string, Integration>();
  private rateLimiters = new Map<string, RateLimit>();
  private eventQueue: IntegrationEvent[] = [];
  private isProcessingQueue = false;
  private webhookServer?: any; // Would be Express/Fastify server
  private encryptionKey: Buffer;

  constructor(private workflowEngine: WorkflowEngine, encryptionKey?: string) {
    super();
    this.encryptionKey = Buffer.from(
      encryptionKey || process.env.INTEGRATION_ENCRYPTION_KEY || 'default-key-change-in-production',
      'utf8'
    );
    this.startEventProcessor();
  }

  /**
   * Register a new integration
   */
  async registerIntegration(integration: Omit<Integration, 'id' | 'createdAt' | 'updatedAt' | 'usageCount'>): Promise<string> {
    const integrationId = this.generateId();
    
    const fullIntegration: Integration = {
      ...integration,
      id: integrationId,
      createdAt: new Date(),
      updatedAt: new Date(),
      usageCount: 0
    };

    // Encrypt sensitive credentials
    if (fullIntegration.authentication?.credentials) {
      fullIntegration.authentication.credentials = this.encryptCredentials(
        fullIntegration.authentication.credentials
      );
    }

    this.integrations.set(integrationId, fullIntegration);
    
    // Initialize rate limiter if specified
    if (fullIntegration.rateLimits) {
      this.rateLimiters.set(integrationId, { ...fullIntegration.rateLimits });
    }

    // Setup integration-specific configuration
    await this.setupIntegration(fullIntegration);

    this.emit('integration:registered', fullIntegration);
    return integrationId;
  }

  /**
   * Setup integration-specific configuration
   */
  private async setupIntegration(integration: Integration): Promise<void> {
    switch (integration.type) {
      case 'webhook':
        await this.setupWebhook(integration);
        break;
      case 'github_actions':
        await this.setupGitHubActions(integration);
        break;
      case 'api_gateway':
        await this.setupAPIGateway(integration);
        break;
      case 'slack':
        await this.setupSlackIntegration(integration);
        break;
      case 'discord':
        await this.setupDiscordIntegration(integration);
        break;
      case 'email':
        await this.setupEmailIntegration(integration);
        break;
      default:
        console.log(`Setup for integration type ${integration.type} not implemented`);
    }
  }

  /**
   * Setup webhook integration
   */
  private async setupWebhook(integration: Integration): Promise<void> {
    const config = integration.config as WebhookConfig;
    
    this.emit('webhook:setup', {
      integrationId: integration.id,
      endpoint: config.endpoint,
      method: config.method,
      handler: async (req: any, res: any) => {
        try {
          // Verify webhook secret if provided
          if (config.secret && !this.verifyWebhookSignature(req, config.secret)) {
            res.status(401).json({ error: 'Invalid signature' });
            return;
          }

          // Create integration event
          const event: IntegrationEvent = {
            id: this.generateId(),
            integrationId: integration.id,
            type: 'webhook_received',
            data: {
              headers: req.headers,
              body: req.body,
              query: req.query,
              method: req.method,
              url: req.url
            },
            timestamp: new Date(),
            processed: false
          };

          this.queueEvent(event);
          res.status(200).json({ success: true, eventId: event.id });

        } catch (error) {
          console.error('Webhook handling error:', error);
          res.status(500).json({ error: 'Internal server error' });
        }
      }
    });
  }

  /**
   * Setup GitHub Actions integration
   */
  private async setupGitHubActions(integration: Integration): Promise<void> {
    const config = integration.config as GitHubActionsConfig;
    
    // Validate GitHub token and repository access
    try {
      const response = await axios.get(`https://api.github.com/repos/${config.repository}`, {
        headers: {
          'Authorization': `token ${config.token}`,
          'Accept': 'application/vnd.github.v3+json'
        }
      });

      this.emit('github:validated', {
        integrationId: integration.id,
        repository: config.repository,
        hasAccess: response.status === 200
      });

    } catch (error) {
      this.emit('github:validation_failed', {
        integrationId: integration.id,
        error: error.message
      });
    }
  }

  /**
   * Setup API Gateway integration
   */
  private async setupAPIGateway(integration: Integration): Promise<void> {
    const config = integration.config as APIGatewayConfig;
    
    // Test connectivity to base URL
    try {
      const response = await axios.get(config.baseURL, {
        timeout: 5000,
        headers: config.defaultHeaders
      });

      this.emit('api_gateway:connected', {
        integrationId: integration.id,
        baseURL: config.baseURL,
        status: response.status
      });

    } catch (error) {
      this.emit('api_gateway:connection_failed', {
        integrationId: integration.id,
        error: error.message
      });
    }
  }

  /**
   * Setup Slack integration
   */
  private async setupSlackIntegration(integration: Integration): Promise<void> {
    const credentials = this.decryptCredentials(integration.authentication?.credentials || {});
    
    if (credentials.webhook_url || credentials.bot_token) {
      this.emit('slack:ready', {
        integrationId: integration.id,
        hasWebhook: !!credentials.webhook_url,
        hasBot: !!credentials.bot_token
      });
    } else {
      this.emit('slack:setup_required', {
        integrationId: integration.id,
        message: 'Slack webhook URL or bot token required'
      });
    }
  }

  /**
   * Setup Discord integration
   */
  private async setupDiscordIntegration(integration: Integration): Promise<void> {
    const credentials = this.decryptCredentials(integration.authentication?.credentials || {});
    
    if (credentials.webhook_url || credentials.bot_token) {
      this.emit('discord:ready', {
        integrationId: integration.id,
        hasWebhook: !!credentials.webhook_url,
        hasBot: !!credentials.bot_token
      });
    } else {
      this.emit('discord:setup_required', {
        integrationId: integration.id,
        message: 'Discord webhook URL or bot token required'
      });
    }
  }

  /**
   * Setup email integration
   */
  private async setupEmailIntegration(integration: Integration): Promise<void> {
    const credentials = this.decryptCredentials(integration.authentication?.credentials || {});
    
    // Validate SMTP configuration
    const requiredFields = ['host', 'port', 'user', 'password'];
    const hasAllFields = requiredFields.every(field => credentials[field]);

    if (hasAllFields) {
      this.emit('email:ready', {
        integrationId: integration.id,
        host: credentials.host,
        port: credentials.port
      });
    } else {
      this.emit('email:setup_required', {
        integrationId: integration.id,
        message: 'SMTP configuration incomplete',
        missing: requiredFields.filter(field => !credentials[field])
      });
    }
  }

  /**
   * Execute integration action
   */
  async executeIntegration(
    integrationId: string, 
    action: string, 
    data: any,
    context?: any
  ): Promise<any> {
    const integration = this.integrations.get(integrationId);
    if (!integration || !integration.enabled) {
      throw new Error(`Integration not found or disabled: ${integrationId}`);
    }

    // Check rate limits
    if (!this.checkRateLimit(integrationId)) {
      throw new Error('Rate limit exceeded');
    }

    integration.usageCount++;
    integration.lastUsed = new Date();
    integration.updatedAt = new Date();

    try {
      const result = await this.executeIntegrationAction(integration, action, data, context);
      this.emit('integration:executed', { integrationId, action, success: true, result });
      return result;

    } catch (error) {
      this.emit('integration:failed', { integrationId, action, error: error.message });
      throw error;
    }
  }

  /**
   * Execute specific integration action
   */
  private async executeIntegrationAction(
    integration: Integration, 
    action: string, 
    data: any, 
    context?: any
  ): Promise<any> {
    switch (integration.type) {
      case 'webhook':
        return this.executeWebhookAction(integration, action, data);
      
      case 'github_actions':
        return this.executeGitHubAction(integration, action, data);
      
      case 'api_gateway':
        return this.executeAPIGatewayAction(integration, action, data);
      
      case 'slack':
        return this.executeSlackAction(integration, action, data);
      
      case 'discord':
        return this.executeDiscordAction(integration, action, data);
      
      case 'email':
        return this.executeEmailAction(integration, action, data);
      
      default:
        throw new Error(`Action execution not implemented for type: ${integration.type}`);
    }
  }

  /**
   * Execute webhook action
   */
  private async executeWebhookAction(integration: Integration, action: string, data: any): Promise<any> {
    const config = integration.config as WebhookConfig;
    const credentials = this.decryptCredentials(integration.authentication?.credentials || {});

    const requestConfig: AxiosRequestConfig = {
      url: config.endpoint,
      method: config.method,
      data: action === 'send' ? data : undefined,
      headers: {
        ...config.headers,
        ...this.getAuthHeaders(integration.authentication, credentials)
      },
      timeout: config.timeout || 30000
    };

    const response = await axios(requestConfig);
    return {
      status: response.status,
      headers: response.headers,
      data: response.data
    };
  }

  /**
   * Execute GitHub Actions
   */
  private async executeGitHubAction(integration: Integration, action: string, data: any): Promise<any> {
    const config = integration.config as GitHubActionsConfig;
    
    if (action === 'trigger_workflow') {
      const response = await axios.post(
        `https://api.github.com/repos/${config.repository}/actions/workflows/${config.workflow}/dispatches`,
        {
          ref: config.branch || 'main',
          inputs: { ...config.inputs, ...data.inputs }
        },
        {
          headers: {
            'Authorization': `token ${config.token}`,
            'Accept': 'application/vnd.github.v3+json'
          }
        }
      );

      return { success: true, status: response.status };
    }

    throw new Error(`Unknown GitHub action: ${action}`);
  }

  /**
   * Execute API Gateway action
   */
  private async executeAPIGatewayAction(integration: Integration, action: string, data: any): Promise<any> {
    const config = integration.config as APIGatewayConfig;
    const endpoint = config.endpoints.find(ep => ep.path === data.endpoint);
    
    if (!endpoint) {
      throw new Error(`Endpoint not found: ${data.endpoint}`);
    }

    const url = `${config.baseURL}${endpoint.path}`;
    const credentials = this.decryptCredentials(endpoint.authentication?.credentials || {});

    const requestConfig: AxiosRequestConfig = {
      url,
      method: endpoint.method as any,
      data: data.body,
      params: data.query,
      headers: {
        ...config.defaultHeaders,
        ...data.headers,
        ...this.getAuthHeaders(endpoint.authentication, credentials)
      }
    };

    const response = await axios(requestConfig);
    return {
      status: response.status,
      headers: response.headers,
      data: response.data
    };
  }

  /**
   * Execute Slack action
   */
  private async executeSlackAction(integration: Integration, action: string, data: any): Promise<any> {
    const credentials = this.decryptCredentials(integration.authentication?.credentials || {});

    if (action === 'send_message') {
      if (credentials.webhook_url) {
        // Use webhook
        const response = await axios.post(credentials.webhook_url, {
          text: data.text,
          channel: data.channel,
          username: data.username,
          icon_emoji: data.icon_emoji,
          attachments: data.attachments
        });

        return { success: response.status === 200 };
      
      } else if (credentials.bot_token) {
        // Use Web API
        const response = await axios.post('https://slack.com/api/chat.postMessage', {
          channel: data.channel,
          text: data.text,
          attachments: data.attachments
        }, {
          headers: {
            'Authorization': `Bearer ${credentials.bot_token}`,
            'Content-Type': 'application/json'
          }
        });

        return response.data;
      }
    }

    throw new Error(`Unknown Slack action: ${action}`);
  }

  /**
   * Execute Discord action
   */
  private async executeDiscordAction(integration: Integration, action: string, data: any): Promise<any> {
    const credentials = this.decryptCredentials(integration.authentication?.credentials || {});

    if (action === 'send_message' && credentials.webhook_url) {
      const response = await axios.post(credentials.webhook_url, {
        content: data.content,
        username: data.username,
        avatar_url: data.avatar_url,
        embeds: data.embeds
      });

      return { success: response.status === 204 };
    }

    throw new Error(`Unknown Discord action: ${action}`);
  }

  /**
   * Execute email action
   */
  private async executeEmailAction(integration: Integration, action: string, data: any): Promise<any> {
    const credentials = this.decryptCredentials(integration.authentication?.credentials || {});

    if (action === 'send_email') {
      // This would integrate with nodemailer or similar
      this.emit('email:send', {
        integrationId: integration.id,
        to: data.to,
        subject: data.subject,
        body: data.body,
        html: data.html,
        attachments: data.attachments,
        smtp: {
          host: credentials.host,
          port: credentials.port,
          user: credentials.user
          // password would be decrypted here
        }
      });

      return { success: true, messageId: this.generateId() };
    }

    throw new Error(`Unknown email action: ${action}`);
  }

  /**
   * Get authentication headers
   */
  private getAuthHeaders(auth?: AuthConfig, credentials: any = {}): Record<string, string> {
    if (!auth || auth.type === 'none') return {};

    switch (auth.type) {
      case 'api_key':
        return {
          [credentials.header_name || 'X-API-Key']: credentials.api_key
        };
      
      case 'bearer_token':
        return {
          'Authorization': `Bearer ${credentials.token}`
        };
      
      case 'basic':
        const basicAuth = Buffer.from(`${credentials.username}:${credentials.password}`).toString('base64');
        return {
          'Authorization': `Basic ${basicAuth}`
        };
      
      default:
        return {};
    }
  }

  /**
   * Check rate limits
   */
  private checkRateLimit(integrationId: string): boolean {
    const limit = this.rateLimiters.get(integrationId);
    if (!limit) return true;

    const now = new Date();
    
    // Reset if window has passed
    if (now > limit.resetTime) {
      limit.current = 0;
      limit.resetTime = new Date(now.getTime() + limit.window);
    }

    if (limit.current >= limit.requests) {
      return false;
    }

    limit.current++;
    return true;
  }

  /**
   * Queue integration event for processing
   */
  private queueEvent(event: IntegrationEvent): void {
    this.eventQueue.push(event);
    this.emit('event:queued', event);
  }

  /**
   * Start event processor
   */
  private startEventProcessor(): void {
    setInterval(async () => {
      if (this.isProcessingQueue || this.eventQueue.length === 0) {
        return;
      }

      this.isProcessingQueue = true;

      try {
        const event = this.eventQueue.shift()!;
        await this.processEvent(event);
      } catch (error) {
        console.error('Event processing error:', error);
      } finally {
        this.isProcessingQueue = false;
      }
    }, 1000);
  }

  /**
   * Process integration event
   */
  private async processEvent(event: IntegrationEvent): Promise<void> {
    try {
      const integration = this.integrations.get(event.integrationId);
      if (!integration) {
        throw new Error(`Integration not found: ${event.integrationId}`);
      }

      // Trigger workflows based on integration events
      const triggers = integration.config.triggers || [];
      
      for (const trigger of triggers) {
        if (this.matchesEventTrigger(event, trigger)) {
          await this.workflowEngine.executeWorkflow(
            trigger.workflowId,
            { event: event.data, integration: integration.name },
            `integration:${integration.id}`
          );
        }
      }

      event.processed = true;
      this.emit('event:processed', event);

    } catch (error) {
      event.error = error.message;
      this.emit('event:failed', { event, error });
    }
  }

  /**
   * Check if event matches trigger conditions
   */
  private matchesEventTrigger(event: IntegrationEvent, trigger: any): boolean {
    if (trigger.eventType && trigger.eventType !== event.type) {
      return false;
    }

    if (trigger.conditions) {
      return this.evaluateEventConditions(event.data, trigger.conditions);
    }

    return true;
  }

  /**
   * Evaluate event conditions
   */
  private evaluateEventConditions(eventData: any, conditions: any[]): boolean {
    return conditions.every(condition => {
      try {
        const func = new Function('event', `return ${condition.expression}`);
        return func(eventData);
      } catch (error) {
        console.warn('Event condition evaluation failed:', condition, error);
        return false;
      }
    });
  }

  /**
   * Verify webhook signature
   */
  private verifyWebhookSignature(req: any, secret: string): boolean {
    const signature = req.headers['x-hub-signature'] || req.headers['x-signature'];
    if (!signature) return false;

    const payload = JSON.stringify(req.body);
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');

    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(`sha256=${expectedSignature}`)
    );
  }

  /**
   * Encrypt sensitive credentials
   */
  private encryptCredentials(credentials: Record<string, any>): Record<string, any> {
    const encrypted: Record<string, any> = {};
    
    for (const [key, value] of Object.entries(credentials)) {
      if (typeof value === 'string' && this.isSensitiveField(key)) {
        const cipher = crypto.createCipher('aes-256-cbc', this.encryptionKey);
        let encryptedValue = cipher.update(value, 'utf8', 'hex');
        encryptedValue += cipher.final('hex');
        encrypted[key] = `encrypted:${encryptedValue}`;
      } else {
        encrypted[key] = value;
      }
    }
    
    return encrypted;
  }

  /**
   * Decrypt sensitive credentials
   */
  private decryptCredentials(credentials: Record<string, any>): Record<string, any> {
    const decrypted: Record<string, any> = {};
    
    for (const [key, value] of Object.entries(credentials)) {
      if (typeof value === 'string' && value.startsWith('encrypted:')) {
        try {
          const encryptedValue = value.substring(10);
          const decipher = crypto.createDecipher('aes-256-cbc', this.encryptionKey);
          let decryptedValue = decipher.update(encryptedValue, 'hex', 'utf8');
          decryptedValue += decipher.final('utf8');
          decrypted[key] = decryptedValue;
        } catch (error) {
          console.error(`Failed to decrypt field ${key}:`, error);
          decrypted[key] = value;
        }
      } else {
        decrypted[key] = value;
      }
    }
    
    return decrypted;
  }

  /**
   * Check if field contains sensitive data
   */
  private isSensitiveField(fieldName: string): boolean {
    const sensitiveFields = [
      'password', 'token', 'secret', 'key', 'api_key', 
      'bot_token', 'webhook_url', 'client_secret'
    ];
    
    return sensitiveFields.some(field => 
      fieldName.toLowerCase().includes(field)
    );
  }

  /**
   * Generate unique ID
   */
  private generateId(): string {
    return crypto.randomBytes(16).toString('hex');
  }

  // Public API methods

  getIntegration(integrationId: string): Integration | undefined {
    return this.integrations.get(integrationId);
  }

  listIntegrations(type?: IntegrationType): Integration[] {
    const integrations = Array.from(this.integrations.values());
    return type ? integrations.filter(i => i.type === type) : integrations;
  }

  async updateIntegration(integrationId: string, updates: Partial<Integration>): Promise<boolean> {
    const integration = this.integrations.get(integrationId);
    if (!integration) return false;

    // Encrypt credentials if updated
    if (updates.authentication?.credentials) {
      updates.authentication.credentials = this.encryptCredentials(
        updates.authentication.credentials
      );
    }

    Object.assign(integration, updates, { updatedAt: new Date() });
    
    // Re-setup if configuration changed
    if (updates.config || updates.authentication) {
      await this.setupIntegration(integration);
    }

    this.emit('integration:updated', integration);
    return true;
  }

  async removeIntegration(integrationId: string): Promise<boolean> {
    const integration = this.integrations.get(integrationId);
    if (!integration) return false;

    this.integrations.delete(integrationId);
    this.rateLimiters.delete(integrationId);

    this.emit('integration:removed', integration);
    return true;
  }

  testIntegration(integrationId: string): Promise<boolean> {
    return this.executeIntegration(integrationId, 'test', {});
  }

  getIntegrationStats(integrationId: string): any {
    const integration = this.integrations.get(integrationId);
    if (!integration) return null;

    const rateLimit = this.rateLimiters.get(integrationId);
    
    return {
      id: integration.id,
      name: integration.name,
      type: integration.type,
      enabled: integration.enabled,
      usageCount: integration.usageCount,
      lastUsed: integration.lastUsed,
      rateLimit: rateLimit ? {
        current: rateLimit.current,
        limit: rateLimit.requests,
        resetTime: rateLimit.resetTime
      } : null
    };
  }

  getAllStats(): any {
    const stats = {
      totalIntegrations: this.integrations.size,
      enabledIntegrations: 0,
      byType: {} as Record<string, number>,
      totalUsage: 0,
      queueSize: this.eventQueue.length
    };

    for (const integration of this.integrations.values()) {
      if (integration.enabled) stats.enabledIntegrations++;
      stats.byType[integration.type] = (stats.byType[integration.type] || 0) + 1;
      stats.totalUsage += integration.usageCount;
    }

    return stats;
  }

  getEventHistory(integrationId?: string, limit: number = 100): IntegrationEvent[] {
    // In a real implementation, this would query a persistent store
    // For now, return recent events from queue
    const events = this.eventQueue.slice(-limit);
    return integrationId 
      ? events.filter(e => e.integrationId === integrationId)
      : events;
  }

  async exportIntegrations(): Promise<string> {
    const data = Array.from(this.integrations.values()).map(integration => ({
      ...integration,
      // Don't export encrypted credentials for security
      authentication: integration.authentication ? {
        ...integration.authentication,
        credentials: {}
      } : undefined
    }));

    return JSON.stringify(data, null, 2);
  }

  async importIntegrations(data: string): Promise<number> {
    const integrations = JSON.parse(data);
    let importCount = 0;

    for (const integration of integrations) {
      try {
        await this.registerIntegration(integration);
        importCount++;
      } catch (error) {
        console.error(`Failed to import integration ${integration.name}:`, error);
      }
    }

    return importCount;
  }

  shutdown(): void {
    this.integrations.clear();
    this.rateLimiters.clear();
    this.eventQueue = [];
    this.removeAllListeners();
  }
}