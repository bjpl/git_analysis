# SPARC METHODOLOGY - INTEGRATED LEARNING PLATFORM
## Phase 4: REFINEMENT

### 4.1 OPTIMIZATION OPPORTUNITIES

#### 4.1.1 Performance Optimization Strategy

**Database Query Optimization:**
```sql
-- Before: N+1 query problem
-- SELECT * FROM users WHERE id = ?
-- FOR each user: SELECT * FROM user_profiles WHERE user_id = ?

-- After: Single optimized query with joins
SELECT 
    u.id, u.email, u.first_name, u.last_name,
    up.learning_style, up.difficulty_preferences,
    lg.subject, lg.current_progress
FROM users u
LEFT JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN learning_goals lg ON u.id = lg.user_id
WHERE u.id = ANY($1::uuid[])
AND lg.status = 'active';

-- Index optimization for spaced repetition queries
CREATE INDEX CONCURRENTLY idx_next_review_optimized 
ON user_learning_progress(next_review, user_id) 
WHERE next_review <= CURRENT_TIMESTAMP;
```

**Caching Strategy Refinement:**
```javascript
// Multi-layer caching architecture
class CacheManager {
  constructor() {
    this.l1Cache = new Map(); // In-memory cache (100MB limit)
    this.l2Cache = new Redis(); // Redis cache (distributed)
    this.l3Cache = new PostgreSQL(); // Database cache tables
  }

  async get(key, fallback) {
    // L1: Memory cache (fastest)
    if (this.l1Cache.has(key)) {
      return this.l1Cache.get(key);
    }

    // L2: Redis cache (fast)
    const redisValue = await this.l2Cache.get(key);
    if (redisValue) {
      this.l1Cache.set(key, JSON.parse(redisValue));
      return JSON.parse(redisValue);
    }

    // L3: Database or computation (slowest)
    const value = await fallback();
    this.setMultiLayer(key, value);
    return value;
  }

  async setMultiLayer(key, value, ttl = 3600) {
    this.l1Cache.set(key, value);
    await this.l2Cache.setex(key, ttl, JSON.stringify(value));
  }
}
```

**Algorithm Optimization:**
```javascript
// Optimized spaced repetition with batch processing
class OptimizedSpacedRepetition {
  constructor() {
    this.batchSize = 100;
    this.processingQueue = new Map();
  }

  async batchUpdateIntervals(userResponses) {
    // Group responses by user for batch processing
    const userGroups = this.groupResponsesByUser(userResponses);
    
    const updates = [];
    for (const [userId, responses] of userGroups) {
      // Batch calculate all intervals for user
      const intervalUpdates = await this.calculateBatchIntervals(userId, responses);
      updates.push(...intervalUpdates);
    }

    // Single database transaction for all updates
    await this.batchUpdateDatabase(updates);
    
    // Update caches in parallel
    await this.batchUpdateCaches(updates);
  }

  calculateBatchIntervals(userId, responses) {
    // Vectorized calculation using user's historical performance
    const userPerformanceVector = this.getUserPerformanceVector(userId);
    
    return responses.map(response => {
      const baseInterval = this.calculateBaseInterval(response);
      const personalizedMultiplier = this.getPersonalizedMultiplier(
        userPerformanceVector, 
        response.subject
      );
      
      return {
        itemId: response.learningItemId,
        newInterval: baseInterval * personalizedMultiplier,
        nextReview: new Date(Date.now() + (baseInterval * personalizedMultiplier * 86400000))
      };
    });
  }
}
```

#### 4.1.2 Memory Usage Optimization

**Connection Pool Optimization:**
```javascript
// Intelligent connection pool management
class AdaptiveConnectionPool {
  constructor() {
    this.minConnections = 5;
    this.maxConnections = 100;
    this.currentConnections = this.minConnections;
    this.connectionMetrics = new Map();
  }

  async getConnection() {
    // Monitor connection usage patterns
    const currentLoad = this.getCurrentLoad();
    
    if (currentLoad > 0.8 && this.currentConnections < this.maxConnections) {
      // Scale up connections during high load
      await this.scaleUp();
    } else if (currentLoad < 0.3 && this.currentConnections > this.minConnections) {
      // Scale down during low load
      await this.scaleDown();
    }

    return await this.pool.getConnection();
  }

  async scaleUp() {
    const newConnections = Math.min(
      this.currentConnections * 1.5,
      this.maxConnections
    );
    
    await this.pool.resize(newConnections);
    this.currentConnections = newConnections;
    console.log(`Scaled up to ${newConnections} connections`);
  }
}
```

**Memory Leak Prevention:**
```javascript
// Automatic memory cleanup system
class MemoryManager {
  constructor() {
    this.memoryThreshold = 500 * 1024 * 1024; // 500MB
    this.cleanupInterval = setInterval(() => {
      this.performCleanup();
    }, 60000); // Every minute
  }

  performCleanup() {
    const memUsage = process.memoryUsage();
    
    if (memUsage.heapUsed > this.memoryThreshold) {
      // Clean expired cache entries
      this.cleanExpiredCache();
      
      // Clean orphaned objects
      this.cleanOrphanedObjects();
      
      // Force garbage collection if needed
      if (global.gc) {
        global.gc();
      }
    }
  }

  cleanExpiredCache() {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (value.expiresAt < now) {
        this.cache.delete(key);
      }
    }
  }
}
```

### 4.2 TESTING STRATEGIES

#### 4.2.1 Test-Driven Development (TDD) Implementation

**Unit Testing Framework:**
```javascript
// Jest configuration for comprehensive testing
module.exports = {
  testEnvironment: 'node',
  coverageThreshold: {
    global: {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.test.js',
    '<rootDir>/tests/**/*.test.js'
  ],
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.config.js',
    '!src/**/index.js'
  ]
};
```

**Core Algorithm Tests:**
```javascript
describe('SpacedRepetitionAlgorithm', () => {
  beforeEach(() => {
    this.algorithm = new SpacedRepetitionAlgorithm();
    this.mockUser = createMockUser();
    this.mockLearningItem = createMockLearningItem();
  });

  describe('calculateNextReview', () => {
    it('should increase interval for correct responses', async () => {
      // Arrange
      const response = { quality: 4, isCorrect: true };
      const currentInterval = 1;

      // Act
      const result = await this.algorithm.calculateNextReview(
        this.mockLearningItem,
        response,
        currentInterval
      );

      // Assert
      expect(result.interval).toBeGreaterThan(currentInterval);
      expect(result.nextReview).toBeInstanceOf(Date);
      expect(result.easiness).toBeGreaterThanOrEqual(1.3);
    });

    it('should reset interval for poor responses', async () => {
      // Arrange
      const response = { quality: 1, isCorrect: false };
      const currentInterval = 10;

      // Act
      const result = await this.algorithm.calculateNextReview(
        this.mockLearningItem,
        response,
        currentInterval
      );

      // Assert
      expect(result.interval).toBe(1);
      expect(result.confidence).toBeLessThan(0.5);
    });

    it('should handle edge cases gracefully', async () => {
      // Test with null/undefined inputs
      await expect(
        this.algorithm.calculateNextReview(null, {}, 1)
      ).rejects.toThrow('Invalid learning item');

      // Test with extreme values
      const extremeResponse = { quality: 10, isCorrect: true };
      const result = await this.algorithm.calculateNextReview(
        this.mockLearningItem,
        extremeResponse,
        1000
      );
      
      expect(result.interval).toBeLessThan(10000); // Sanity check
    });
  });
});
```

**Integration Testing:**
```javascript
describe('Learning Service Integration', () => {
  let testDb, testRedis, learningService;

  beforeAll(async () => {
    testDb = await setupTestDatabase();
    testRedis = await setupTestRedis();
    learningService = new LearningService(testDb, testRedis);
  });

  afterAll(async () => {
    await teardownTestDatabase(testDb);
    await teardownTestRedis(testRedis);
  });

  describe('complete learning session workflow', () => {
    it('should handle full learning session lifecycle', async () => {
      // Start session
      const session = await learningService.startSession({
        userId: testUserId,
        subject: 'spanish',
        targetItems: 10
      });

      expect(session.id).toBeDefined();
      expect(session.status).toBe('active');

      // Submit responses
      const responses = await Promise.all([
        learningService.submitResponse(session.id, correctResponse1),
        learningService.submitResponse(session.id, incorrectResponse1),
        learningService.submitResponse(session.id, partialResponse1)
      ]);

      // Verify response processing
      responses.forEach(response => {
        expect(response.feedback).toBeDefined();
        expect(response.nextInterval).toBeGreaterThan(0);
      });

      // End session
      const completedSession = await learningService.endSession(session.id);
      
      expect(completedSession.status).toBe('completed');
      expect(completedSession.performance).toBeDefined();
      expect(completedSession.itemsStudied).toBe(3);
    });
  });
});
```

#### 4.2.2 Load Testing Strategy

**Artillery Load Testing Configuration:**
```yaml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 120
      arrivalRate: 50
      name: "Ramp up load"
    - duration: 300
      arrivalRate: 100
      name: "Sustained load"
  payload:
    path: "test-users.csv"
    fields:
      - "email"
      - "password"

scenarios:
  - name: "Complete learning session"
    weight: 70
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.token"
              as: "authToken"
      
      - post:
          url: "/learning/sessions/start"
          headers:
            Authorization: "Bearer {{ authToken }}"
          json:
            subject: "spanish"
            targetItems: 10
          capture:
            - json: "$.sessionId"
              as: "sessionId"
      
      - loop:
          - post:
              url: "/learning/responses"
              headers:
                Authorization: "Bearer {{ authToken }}"
              json:
                sessionId: "{{ sessionId }}"
                response: "{{ $randomString() }}"
                responseTime: "{{ $randomInt(1000, 5000) }}"
        count: 10

      - put:
          url: "/learning/sessions/{{ sessionId }}/end"
          headers:
            Authorization: "Bearer {{ authToken }}"

  - name: "Analytics dashboard"
    weight: 20
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.token"
              as: "authToken"
      
      - get:
          url: "/analytics/dashboard"
          headers:
            Authorization: "Bearer {{ authToken }}"
      
      - get:
          url: "/analytics/progress/week"
          headers:
            Authorization: "Bearer {{ authToken }}"

  - name: "Content generation"
    weight: 10
    flow:
      - post:
          url: "/auth/login"
          json:
            email: "{{ email }}"
            password: "{{ password }}"
          capture:
            - json: "$.token"
              as: "authToken"
      
      - post:
          url: "/content/generate"
          headers:
            Authorization: "Bearer {{ authToken }}"
          json:
            subject: "spanish"
            contentType: "conjugation"
            difficulty: 0.7
```

**Performance Benchmarking:**
```javascript
// Automated performance benchmarking
class PerformanceBenchmark {
  constructor() {
    this.metrics = new Map();
    this.thresholds = {
      responseTime: 200, // ms
      throughput: 1000,  // requests/second
      errorRate: 0.01    // 1%
    };
  }

  async benchmarkSpacedRepetition() {
    const testCases = [
      { users: 100, items: 10 },
      { users: 1000, items: 10 },
      { users: 10000, items: 10 }
    ];

    for (const testCase of testCases) {
      const startTime = Date.now();
      
      // Generate test data
      const users = await this.generateTestUsers(testCase.users);
      const responses = await this.generateTestResponses(users, testCase.items);
      
      // Benchmark algorithm
      const results = await this.measureAlgorithmPerformance(responses);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      this.metrics.set(`spacedRepetition_${testCase.users}_users`, {
        duration,
        throughput: (testCase.users * testCase.items) / (duration / 1000),
        avgResponseTime: results.avgResponseTime,
        errorRate: results.errorRate
      });
    }
  }

  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      benchmarks: {},
      thresholdViolations: []
    };

    for (const [testName, metrics] of this.metrics) {
      report.benchmarks[testName] = metrics;
      
      // Check threshold violations
      if (metrics.avgResponseTime > this.thresholds.responseTime) {
        report.thresholdViolations.push({
          test: testName,
          metric: 'responseTime',
          actual: metrics.avgResponseTime,
          threshold: this.thresholds.responseTime
        });
      }
    }

    return report;
  }
}
```

### 4.3 CI/CD PIPELINE

#### 4.3.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '18.x'
  POSTGRES_VERSION: '14'

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linting
        run: npm run lint

      - name: Run type checking
        run: npm run typecheck

      - name: Run unit tests
        run: npm run test:unit
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379

      - name: Run integration tests
        run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379

      - name: Run load tests
        run: npm run test:load
        env:
          TEST_TARGET: http://localhost:3000

      - name: Generate coverage report
        run: npm run coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run security audit
        run: npm audit --audit-level high

      - name: Run SAST scan
        uses: github/super-linter@v4
        env:
          DEFAULT_BRANCH: main
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Run dependency check
        uses: dependency-check/Dependency-Check_Action@main
        with:
          project: 'learning-platform'
          path: '.'
          format: 'JSON'

  build-and-deploy:
    runs-on: ubuntu-latest
    needs: [test, security-scan]
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-west-2

      - name: Build Docker images
        run: |
          docker build -t learning-platform-api:${{ github.sha }} .
          docker build -t learning-platform-worker:${{ github.sha }} -f Dockerfile.worker .

      - name: Push to ECR
        run: |
          aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker tag learning-platform-api:${{ github.sha }} $ECR_REGISTRY/learning-platform-api:${{ github.sha }}
          docker tag learning-platform-worker:${{ github.sha }} $ECR_REGISTRY/learning-platform-worker:${{ github.sha }}
          docker push $ECR_REGISTRY/learning-platform-api:${{ github.sha }}
          docker push $ECR_REGISTRY/learning-platform-worker:${{ github.sha }}
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}

      - name: Deploy to staging
        run: |
          kubectl set image deployment/api-deployment api=$ECR_REGISTRY/learning-platform-api:${{ github.sha }}
          kubectl set image deployment/worker-deployment worker=$ECR_REGISTRY/learning-platform-worker:${{ github.sha }}
          kubectl rollout status deployment/api-deployment
          kubectl rollout status deployment/worker-deployment

      - name: Run smoke tests
        run: npm run test:smoke
        env:
          TEST_TARGET: https://staging.learningplatform.com

      - name: Deploy to production
        if: success()
        run: |
          kubectl config use-context production
          kubectl set image deployment/api-deployment api=$ECR_REGISTRY/learning-platform-api:${{ github.sha }}
          kubectl set image deployment/worker-deployment worker=$ECR_REGISTRY/learning-platform-worker:${{ github.sha }}
          kubectl rollout status deployment/api-deployment
          kubectl rollout status deployment/worker-deployment
```

#### 4.3.2 Quality Gates

```javascript
// Quality gate configuration
const qualityGates = {
  codeQuality: {
    sonarQube: {
      coverage: 90,
      maintainabilityRating: 'A',
      reliabilityRating: 'A',
      securityRating: 'A',
      duplicatedLines: 3
    }
  },
  
  performance: {
    loadTesting: {
      avgResponseTime: 200,
      p95ResponseTime: 500,
      errorRate: 0.01,
      throughput: 1000
    },
    
    resourceUsage: {
      cpuUsage: 70,
      memoryUsage: 80,
      diskIO: 80
    }
  },
  
  security: {
    vulnerabilities: {
      critical: 0,
      high: 0,
      medium: 5
    },
    
    dependencies: {
      outdated: 10,
      vulnerable: 0
    }
  }
};

// Quality gate checker
class QualityGateChecker {
  async checkAllGates() {
    const results = {
      codeQuality: await this.checkCodeQuality(),
      performance: await this.checkPerformance(),
      security: await this.checkSecurity()
    };

    const passed = Object.values(results).every(result => result.passed);
    
    if (!passed) {
      throw new Error(`Quality gates failed: ${JSON.stringify(results, null, 2)}`);
    }

    return results;
  }

  async checkCodeQuality() {
    const sonarResults = await this.getSonarQubeResults();
    
    return {
      passed: sonarResults.coverage >= qualityGates.codeQuality.sonarQube.coverage,
      details: sonarResults
    };
  }
}
```

### 4.4 MONITORING & OBSERVABILITY

#### 4.4.1 Application Performance Monitoring

```javascript
// Custom APM implementation
class LearningPlatformAPM {
  constructor() {
    this.metrics = new Map();
    this.traces = new Map();
    this.alerts = new Map();
  }

  // Track key business metrics
  trackLearningMetrics(userId, sessionId, metrics) {
    const timestamp = Date.now();
    
    this.recordMetric('learning.session.accuracy', metrics.accuracy, {
      userId,
      sessionId,
      subject: metrics.subject,
      timestamp
    });
    
    this.recordMetric('learning.session.completion_time', metrics.completionTime, {
      userId,
      sessionId,
      timestamp
    });

    this.recordMetric('learning.retention.rate', metrics.retentionRate, {
      userId,
      subject: metrics.subject,
      timestamp
    });
  }

  // Distributed tracing
  startTrace(operationName, parentSpanId = null) {
    const traceId = this.generateTraceId();
    const spanId = this.generateSpanId();
    
    const trace = {
      traceId,
      spanId,
      parentSpanId,
      operationName,
      startTime: Date.now(),
      tags: new Map(),
      logs: []
    };
    
    this.traces.set(spanId, trace);
    return spanId;
  }

  finishTrace(spanId, error = null) {
    const trace = this.traces.get(spanId);
    if (!trace) return;

    trace.endTime = Date.now();
    trace.duration = trace.endTime - trace.startTime;
    
    if (error) {
      trace.error = true;
      trace.errorMessage = error.message;
    }

    // Send to APM service
    this.sendTraceToAPM(trace);
    
    // Check for performance issues
    this.checkPerformanceThresholds(trace);
  }

  checkPerformanceThresholds(trace) {
    const thresholds = {
      'spaced_repetition_calculation': 50,
      'content_generation': 2000,
      'user_analytics': 500,
      'database_query': 100
    };

    const threshold = thresholds[trace.operationName];
    if (threshold && trace.duration > threshold) {
      this.triggerAlert('performance_degradation', {
        operation: trace.operationName,
        duration: trace.duration,
        threshold,
        traceId: trace.traceId
      });
    }
  }
}
```

#### 4.4.2 Custom Metrics Dashboard

```javascript
// Real-time metrics collection
class MetricsCollector {
  constructor() {
    this.prometheus = require('prom-client');
    this.setupMetrics();
  }

  setupMetrics() {
    // Learning-specific metrics
    this.learningSessionDuration = new this.prometheus.Histogram({
      name: 'learning_session_duration_seconds',
      help: 'Duration of learning sessions',
      labelNames: ['subject', 'difficulty_level'],
      buckets: [10, 30, 60, 120, 300, 600]
    });

    this.spacedRepetitionAccuracy = new this.prometheus.Gauge({
      name: 'spaced_repetition_accuracy_ratio',
      help: 'Accuracy of spaced repetition predictions',
      labelNames: ['algorithm_version', 'subject']
    });

    this.contentGenerationLatency = new this.prometheus.Histogram({
      name: 'content_generation_duration_seconds',
      help: 'Time taken to generate content',
      labelNames: ['content_type', 'ai_model'],
      buckets: [0.1, 0.5, 1, 2, 5, 10]
    });

    this.activeUsers = new this.prometheus.Gauge({
      name: 'active_users_total',
      help: 'Number of currently active users',
      labelNames: ['timeframe']
    });
  }

  recordLearningSession(duration, subject, difficulty) {
    this.learningSessionDuration
      .labels(subject, difficulty.toString())
      .observe(duration);
  }

  recordSpacedRepetitionAccuracy(accuracy, algorithm, subject) {
    this.spacedRepetitionAccuracy
      .labels(algorithm, subject)
      .set(accuracy);
  }
}
```

### 4.5 ERROR HANDLING & RESILIENCE

#### 4.5.1 Circuit Breaker Pattern

```javascript
// Circuit breaker for external AI services
class AIServiceCircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.failureThreshold = threshold;
    this.timeout = timeout;
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
  }

  async call(operation) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.timeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }

  onFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
    }
  }
}
```

#### 4.5.2 Graceful Degradation Strategy

```javascript
// Service degradation handler
class ServiceDegradationHandler {
  constructor() {
    this.serviceStatus = new Map();
    this.fallbackStrategies = new Map();
    this.setupFallbacks();
  }

  setupFallbacks() {
    // AI content generation fallback
    this.fallbackStrategies.set('ai_content_generation', {
      primary: this.generateWithOpenAI.bind(this),
      fallback: this.generateWithLocalModel.bind(this),
      lastResort: this.usePreGeneratedContent.bind(this)
    });

    // User analytics fallback
    this.fallbackStrategies.set('analytics', {
      primary: this.realTimeAnalytics.bind(this),
      fallback: this.cachedAnalytics.bind(this),
      lastResort: this.basicAnalytics.bind(this)
    });
  }

  async executeWithFallback(serviceName, ...args) {
    const strategies = this.fallbackStrategies.get(serviceName);
    if (!strategies) {
      throw new Error(`No fallback strategy for service: ${serviceName}`);
    }

    const methods = [strategies.primary, strategies.fallback, strategies.lastResort];
    
    for (const method of methods) {
      try {
        const result = await method(...args);
        this.recordServiceSuccess(serviceName, method.name);
        return result;
      } catch (error) {
        this.recordServiceFailure(serviceName, method.name, error);
        console.warn(`Service ${serviceName} method ${method.name} failed:`, error.message);
      }
    }

    throw new Error(`All fallback strategies failed for service: ${serviceName}`);
  }
}
```

This comprehensive SPARC Refinement phase covers all critical optimization areas, testing strategies, CI/CD pipeline implementation, monitoring systems, and error handling mechanisms needed for a production-ready learning platform.