/**
 * UserAnalytics - Comprehensive user behavior analytics system
 * Features: Command tracking, navigation flow, error patterns, A/B testing
 */

export interface CommandUsage {
  command: string;
  count: number;
  totalTime: number;
  averageTime: number;
  successRate: number;
  lastUsed: number;
  parameters: Record<string, any>;
}

export interface NavigationFlow {
  fromPage: string;
  toPage: string;
  timestamp: number;
  duration: number;
  exitType: 'navigation' | 'back' | 'close' | 'error';
}

export interface ErrorPattern {
  errorType: string;
  errorMessage: string;
  stackTrace: string;
  context: Record<string, any>;
  timestamp: number;
  userId?: string;
  sessionId: string;
  recoveryAction?: string;
  recoverySuccess: boolean;
}

export interface SessionMetrics {
  sessionId: string;
  startTime: number;
  endTime?: number;
  duration: number;
  commandsExecuted: number;
  errorsEncountered: number;
  pagesVisited: string[];
  features: string[];
  userAgent: string;
  screenResolution: string;
  engagement: {
    clickCount: number;
    keyboardInteractions: number;
    scrollDistance: number;
    idleTime: number;
  };
}

export interface FeatureAdoption {
  featureName: string;
  firstUsed: number;
  totalUses: number;
  uniqueUsers: Set<string>;
  adoptionRate: number;
  retentionRate: number;
  timeToFirstUse: number;
}

export interface ABTestConfig {
  testName: string;
  variants: string[];
  trafficSplit: Record<string, number>;
  startDate: number;
  endDate: number;
  metrics: string[];
  isActive: boolean;
}

export interface ABTestResult {
  testName: string;
  variant: string;
  userId: string;
  sessionId: string;
  timestamp: number;
  metrics: Record<string, any>;
  conversionEvents: string[];
}

export interface UserPreference {
  userId: string;
  preferences: Record<string, any>;
  lastUpdated: number;
  source: 'explicit' | 'inferred' | 'default';
}

export class UserAnalytics {
  private commandUsage = new Map<string, CommandUsage>();
  private navigationHistory: NavigationFlow[] = [];
  private errorPatterns: ErrorPattern[] = [];
  private sessions = new Map<string, SessionMetrics>();
  private featureAdoption = new Map<string, FeatureAdoption>();
  private abTests = new Map<string, ABTestConfig>();
  private abTestResults: ABTestResult[] = [];
  private userPreferences = new Map<string, UserPreference>();
  private currentSession?: SessionMetrics;
  private observers: Array<(event: any) => void> = [];
  
  // Configuration
  private config = {
    sessionTimeoutMs: 30 * 60 * 1000, // 30 minutes
    maxNavigationHistory: 1000,
    maxErrorHistory: 500,
    enableHeartbeat: true,
    heartbeatIntervalMs: 60000, // 1 minute
    autoFlushIntervalMs: 5 * 60 * 1000, // 5 minutes
    enableLocalStorage: true,
    enableServerSync: false
  };

  private heartbeatInterval?: NodeJS.Timeout;
  private flushInterval?: NodeJS.Timeout;
  private startTime = Date.now();

  constructor() {
    this.initializeSession();
    this.setupEventListeners();
    this.startHeartbeat();
    this.loadFromStorage();
  }

  private initializeSession(): void {
    const sessionId = this.generateSessionId();
    this.currentSession = {
      sessionId,
      startTime: Date.now(),
      duration: 0,
      commandsExecuted: 0,
      errorsEncountered: 0,
      pagesVisited: [],
      features: [],
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'Unknown',
      screenResolution: typeof screen !== 'undefined' ? `${screen.width}x${screen.height}` : 'Unknown',
      engagement: {
        clickCount: 0,
        keyboardInteractions: 0,
        scrollDistance: 0,
        idleTime: 0
      }
    };
    
    this.sessions.set(sessionId, this.currentSession);
  }

  private setupEventListeners(): void {
    if (typeof window !== 'undefined') {
      // Track user interactions
      window.addEventListener('click', () => {
        if (this.currentSession) {
          this.currentSession.engagement.clickCount++;
        }
      });

      window.addEventListener('keydown', () => {
        if (this.currentSession) {
          this.currentSession.engagement.keyboardInteractions++;
        }
      });

      window.addEventListener('scroll', () => {
        if (this.currentSession) {
          this.currentSession.engagement.scrollDistance += Math.abs(window.scrollY);
        }
      });

      // Track page visibility changes
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          this.trackIdleStart();
        } else {
          this.trackIdleEnd();
        }
      });

      // Track before unload
      window.addEventListener('beforeunload', () => {
        this.endSession();
      });
    }
  }

  private startHeartbeat(): void {
    if (!this.config.enableHeartbeat) return;
    
    this.heartbeatInterval = setInterval(() => {
      this.updateSessionDuration();
      this.flushToStorage();
    }, this.config.heartbeatIntervalMs);

    this.flushInterval = setInterval(() => {
      this.flushToStorage();
    }, this.config.autoFlushIntervalMs);
  }

  private generateSessionId(): string {
    return `session-${Date.now()}-${Math.random().toString(36).substring(2)}`;
  }

  // Command tracking
  public trackCommand(command: string, parameters: Record<string, any> = {}, success: boolean = true, duration: number = 0): void {
    const existing = this.commandUsage.get(command);
    
    if (existing) {
      existing.count++;
      existing.totalTime += duration;
      existing.averageTime = existing.totalTime / existing.count;
      existing.successRate = (existing.successRate * (existing.count - 1) + (success ? 1 : 0)) / existing.count;
      existing.lastUsed = Date.now();
      existing.parameters = { ...existing.parameters, ...parameters };
    } else {
      this.commandUsage.set(command, {
        command,
        count: 1,
        totalTime: duration,
        averageTime: duration,
        successRate: success ? 1 : 0,
        lastUsed: Date.now(),
        parameters
      });
    }

    if (this.currentSession) {
      this.currentSession.commandsExecuted++;
    }

    this.notifyObservers({
      type: 'command',
      command,
      parameters,
      success,
      duration,
      timestamp: Date.now()
    });
  }

  // Navigation tracking
  public trackNavigation(fromPage: string, toPage: string, exitType: NavigationFlow['exitType'] = 'navigation'): void {
    const navigation: NavigationFlow = {
      fromPage,
      toPage,
      timestamp: Date.now(),
      duration: 0, // Will be updated when leaving the page
      exitType
    };

    this.navigationHistory.push(navigation);
    
    // Trim history if it gets too long
    if (this.navigationHistory.length > this.config.maxNavigationHistory) {
      this.navigationHistory = this.navigationHistory.slice(-this.config.maxNavigationHistory);
    }

    if (this.currentSession && !this.currentSession.pagesVisited.includes(toPage)) {
      this.currentSession.pagesVisited.push(toPage);
    }

    this.notifyObservers({
      type: 'navigation',
      navigation,
      timestamp: Date.now()
    });
  }

  // Error tracking
  public trackError(error: Error, context: Record<string, any> = {}, recoveryAction?: string, recoverySuccess: boolean = false): void {
    const errorPattern: ErrorPattern = {
      errorType: error.name,
      errorMessage: error.message,
      stackTrace: error.stack || 'No stack trace available',
      context,
      timestamp: Date.now(),
      sessionId: this.currentSession?.sessionId || 'unknown',
      recoveryAction,
      recoverySuccess
    };

    this.errorPatterns.push(errorPattern);
    
    // Trim error history if it gets too long
    if (this.errorPatterns.length > this.config.maxErrorHistory) {
      this.errorPatterns = this.errorPatterns.slice(-this.config.maxErrorHistory);
    }

    if (this.currentSession) {
      this.currentSession.errorsEncountered++;
    }

    this.notifyObservers({
      type: 'error',
      error: errorPattern,
      timestamp: Date.now()
    });
  }

  // Feature adoption tracking
  public trackFeatureUsage(featureName: string, userId?: string): void {
    const existing = this.featureAdoption.get(featureName);
    const now = Date.now();

    if (existing) {
      existing.totalUses++;
      if (userId) {
        existing.uniqueUsers.add(userId);
      }
      existing.adoptionRate = existing.uniqueUsers.size / this.sessions.size;
    } else {
      const users = new Set<string>();
      if (userId) users.add(userId);
      
      this.featureAdoption.set(featureName, {
        featureName,
        firstUsed: now,
        totalUses: 1,
        uniqueUsers: users,
        adoptionRate: users.size / this.sessions.size,
        retentionRate: 0, // Will be calculated over time
        timeToFirstUse: now - this.startTime
      });
    }

    if (this.currentSession && !this.currentSession.features.includes(featureName)) {
      this.currentSession.features.push(featureName);
    }

    this.notifyObservers({
      type: 'feature',
      featureName,
      userId,
      timestamp: now
    });
  }

  // A/B Testing
  public createABTest(config: ABTestConfig): void {
    this.abTests.set(config.testName, config);
  }

  public assignUserToVariant(testName: string, userId: string): string | null {
    const test = this.abTests.get(testName);
    if (!test || !test.isActive || Date.now() > test.endDate) {
      return null;
    }

    // Simple hash-based assignment for consistency
    const hash = this.hashString(userId + testName);
    const variants = Object.keys(test.trafficSplit);
    let cumulative = 0;
    const random = hash % 100;

    for (const variant of variants) {
      cumulative += test.trafficSplit[variant];
      if (random < cumulative) {
        return variant;
      }
    }

    return variants[0]; // Fallback
  }

  public trackABTestResult(testName: string, variant: string, userId: string, metrics: Record<string, any>, conversionEvents: string[] = []): void {
    const result: ABTestResult = {
      testName,
      variant,
      userId,
      sessionId: this.currentSession?.sessionId || 'unknown',
      timestamp: Date.now(),
      metrics,
      conversionEvents
    };

    this.abTestResults.push(result);

    this.notifyObservers({
      type: 'abtest',
      result,
      timestamp: Date.now()
    });
  }

  // User preferences
  public updateUserPreference(userId: string, key: string, value: any, source: UserPreference['source'] = 'explicit'): void {
    const existing = this.userPreferences.get(userId);
    
    if (existing) {
      existing.preferences[key] = value;
      existing.lastUpdated = Date.now();
      existing.source = source;
    } else {
      this.userPreferences.set(userId, {
        userId,
        preferences: { [key]: value },
        lastUpdated: Date.now(),
        source
      });
    }

    this.notifyObservers({
      type: 'preference',
      userId,
      key,
      value,
      source,
      timestamp: Date.now()
    });
  }

  public getUserPreference(userId: string, key: string): any {
    const preferences = this.userPreferences.get(userId);
    return preferences?.preferences[key];
  }

  // Session management
  private updateSessionDuration(): void {
    if (this.currentSession) {
      this.currentSession.duration = Date.now() - this.currentSession.startTime;
    }
  }

  public endSession(): void {
    if (this.currentSession) {
      this.currentSession.endTime = Date.now();
      this.currentSession.duration = this.currentSession.endTime - this.currentSession.startTime;
      
      this.notifyObservers({
        type: 'sessionEnd',
        session: this.currentSession,
        timestamp: Date.now()
      });
    }
  }

  private trackIdleStart(): void {
    if (this.currentSession) {
      this.currentSession.engagement.idleTime = Date.now();
    }
  }

  private trackIdleEnd(): void {
    if (this.currentSession && this.currentSession.engagement.idleTime > 0) {
      const idleDuration = Date.now() - this.currentSession.engagement.idleTime;
      this.currentSession.engagement.idleTime += idleDuration;
    }
  }

  // Analytics queries
  public getCommandStats(): CommandUsage[] {
    return Array.from(this.commandUsage.values())
      .sort((a, b) => b.count - a.count);
  }

  public getNavigationFlow(): NavigationFlow[] {
    return [...this.navigationHistory];
  }

  public getErrorPatterns(): ErrorPattern[] {
    return [...this.errorPatterns];
  }

  public getFeatureAdoptionStats(): FeatureAdoption[] {
    return Array.from(this.featureAdoption.values())
      .sort((a, b) => b.adoptionRate - a.adoptionRate);
  }

  public getSessionMetrics(): SessionMetrics[] {
    return Array.from(this.sessions.values());
  }

  public getABTestResults(testName?: string): ABTestResult[] {
    if (testName) {
      return this.abTestResults.filter(r => r.testName === testName);
    }
    return [...this.abTestResults];
  }

  // Data persistence
  private flushToStorage(): void {
    if (!this.config.enableLocalStorage || typeof localStorage === 'undefined') {
      return;
    }

    try {
      const data = {
        commandUsage: Array.from(this.commandUsage.entries()),
        navigationHistory: this.navigationHistory,
        errorPatterns: this.errorPatterns,
        sessions: Array.from(this.sessions.entries()),
        featureAdoption: Array.from(this.featureAdoption.entries()).map(([name, feature]) => [
          name, 
          { ...feature, uniqueUsers: Array.from(feature.uniqueUsers) }
        ]),
        abTestResults: this.abTestResults,
        userPreferences: Array.from(this.userPreferences.entries())
      };

      localStorage.setItem('userAnalytics', JSON.stringify(data));
    } catch (error) {
      console.warn('Failed to save analytics data:', error);
    }
  }

  private loadFromStorage(): void {
    if (!this.config.enableLocalStorage || typeof localStorage === 'undefined') {
      return;
    }

    try {
      const data = localStorage.getItem('userAnalytics');
      if (!data) return;

      const parsed = JSON.parse(data);
      
      this.commandUsage = new Map(parsed.commandUsage);
      this.navigationHistory = parsed.navigationHistory || [];
      this.errorPatterns = parsed.errorPatterns || [];
      this.sessions = new Map(parsed.sessions);
      
      // Reconstruct feature adoption with Sets
      if (parsed.featureAdoption) {
        this.featureAdoption = new Map(
          parsed.featureAdoption.map(([name, feature]) => [
            name,
            { ...feature, uniqueUsers: new Set(feature.uniqueUsers) }
          ])
        );
      }
      
      this.abTestResults = parsed.abTestResults || [];
      this.userPreferences = new Map(parsed.userPreferences);
    } catch (error) {
      console.warn('Failed to load analytics data:', error);
    }
  }

  // Export functionality
  public exportData(): any {
    return {
      commandUsage: Array.from(this.commandUsage.entries()),
      navigationHistory: this.navigationHistory,
      errorPatterns: this.errorPatterns,
      sessions: Array.from(this.sessions.entries()),
      featureAdoption: Array.from(this.featureAdoption.entries()),
      abTestResults: this.abTestResults,
      userPreferences: Array.from(this.userPreferences.entries())
    };
  }

  public exportToCSV(): string {
    const csvData = [];
    
    // Command usage CSV
    csvData.push('Command Usage');
    csvData.push('Command,Count,Total Time,Average Time,Success Rate,Last Used');
    Array.from(this.commandUsage.values()).forEach(cmd => {
      csvData.push(`${cmd.command},${cmd.count},${cmd.totalTime},${cmd.averageTime.toFixed(2)},${(cmd.successRate * 100).toFixed(1)}%,${new Date(cmd.lastUsed).toISOString()}`);
    });
    
    return csvData.join('\n');
  }

  // Observer pattern
  public subscribe(callback: (event: any) => void): () => void {
    this.observers.push(callback);
    return () => {
      const index = this.observers.indexOf(callback);
      if (index > -1) {
        this.observers.splice(index, 1);
      }
    };
  }

  private notifyObservers(event: any): void {
    this.observers.forEach(callback => callback(event));
  }

  // Utility functions
  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  public dispose(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
    }
    this.endSession();
    this.flushToStorage();
  }
}

// Singleton instance
export const userAnalytics = new UserAnalytics();