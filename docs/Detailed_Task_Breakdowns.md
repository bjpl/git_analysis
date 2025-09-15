# SpanishMaster Platform - Detailed Task Breakdowns

## Task Matrix Overview

This document provides granular task breakdowns with specific deliverables, dependencies, resource requirements, success criteria, and risk mitigation strategies for each phase of the SpanishMaster platform development.

---

# WEEK 1-2: FOUNDATION PHASE

## Week 1 Tasks

### Task 1.1: Project Architecture Design
**Category**: Infrastructure  
**Effort**: 8 hours  
**Priority**: P0 (Critical)  
**Owner**: Senior Full-Stack Developer

#### Specific Deliverables
1. **Monorepo Structure**: Complete directory tree with all necessary folders
2. **Development Environment**: Docker Compose setup with hot reload
3. **CI/CD Pipeline**: GitHub Actions workflow file
4. **Package Configuration**: package.json files with all dependencies
5. **Environment Setup**: Development, staging, production environment configs

#### Dependencies
- **Prerequisites**: None
- **Blockers**: Technology stack approval required
- **Parallel Tasks**: None

#### Resource Requirements
- **Personnel**: 1 Senior Developer
- **Tools**: Docker, Node.js, Git, GitHub
- **Infrastructure**: GitHub repository, basic AWS account
- **Budget**: $0 (using free tiers)

#### Success Criteria
- [ ] All developers can run project with single command (`docker-compose up`)
- [ ] Hot reload works for both frontend and backend
- [ ] CI/CD pipeline runs successfully on pull requests
- [ ] Code quality gates pass (linting, TypeScript compilation)
- [ ] All environment variables are properly configured

#### Risk Mitigation

**Risk**: Docker complexity causing setup issues  
**Likelihood**: Medium | **Impact**: High  
**Mitigation**: 
- Provide alternative non-Docker setup instructions
- Create setup validation scripts
- Pre-built Docker images for common configurations

**Risk**: CI/CD pipeline failures  
**Likelihood**: Low | **Impact**: Medium  
**Mitigation**:
- Start with minimal pipeline, expand incrementally
- Use proven GitHub Actions templates
- Implement pipeline failure notifications

#### Acceptance Test Plan
```bash
# Test 1: Environment Setup
1. Clone repository
2. Run `npm run setup`
3. Verify all services start correctly
4. Confirm hot reload functionality

# Test 2: CI/CD Pipeline
1. Create feature branch
2. Make trivial change
3. Push to GitHub
4. Verify pipeline runs and passes

# Test 3: Quality Gates
1. Introduce linting error
2. Verify pipeline fails appropriately
3. Fix error, verify pipeline passes
```

---

### Task 1.2: Database Architecture Migration
**Category**: Data Layer  
**Effort**: 12 hours  
**Priority**: P0 (Critical)  
**Owner**: Senior Full-Stack Developer + DBA Consultant

#### Specific Deliverables
1. **Unified Schema Design**: PostgreSQL schema consolidating all existing SQLite databases
2. **Migration Scripts**: Automated scripts to transfer data from SQLite to PostgreSQL
3. **ORM Setup**: Prisma or TypeORM configuration with type generation
4. **Database Seeding**: Scripts to populate development database with test data
5. **Performance Indexes**: Optimized indexes for all expected query patterns

#### Dependencies
- **Prerequisites**: Task 1.1 (Project Architecture) must be complete
- **Blockers**: Access to all existing SQLite databases
- **Parallel Tasks**: Can start schema design while architecture is being finalized

#### Resource Requirements
- **Personnel**: 1 Senior Developer + 0.25 FTE DBA Consultant (3 hours)
- **Tools**: PostgreSQL, Prisma/TypeORM, pgAdmin, database migration tools
- **Infrastructure**: PostgreSQL instance (local + staging)
- **Budget**: $100/month for managed PostgreSQL (RDS/Supabase)

#### Success Criteria
- [ ] 100% data migration without loss from all source databases
- [ ] Query performance meets or exceeds SQLite performance
- [ ] All foreign key relationships properly established
- [ ] Database connection pooling configured and tested
- [ ] Backup and recovery procedures documented and tested

#### Detailed Schema Migration Strategy

**Phase 1: Schema Analysis** (2 hours)
```sql
-- Analyze existing schemas
-- MySpanishApp: sessions, vocab, grammar, challenges, comfort, teachers
-- Conjugation GUI: progress tracking, verb database, exercise results
-- Subjunctive Practice: trigger types, streak data, user progress
-- Image Manager: images, tags, collections, ratings
```

**Phase 2: Unified Schema Design** (4 hours)
```sql
-- Core Tables
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE teachers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  region VARCHAR(100),
  specialties TEXT[],
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Session Management (enhanced from MySpanishApp)
CREATE TABLE learning_sessions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  teacher_id INTEGER REFERENCES teachers(id),
  session_date DATE NOT NULL,
  start_time TIME,
  duration INTERVAL,
  status VARCHAR(20) DEFAULT 'planned' CHECK (status IN ('planned', 'active', 'completed', 'cancelled')),
  session_type VARCHAR(50) DEFAULT 'tutoring', -- tutoring, self-study, practice
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Vocabulary System (from MySpanishApp + Image Manager integration)
CREATE TABLE vocabulary (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  session_id INTEGER REFERENCES learning_sessions(id) ON DELETE SET NULL,
  word_phrase TEXT NOT NULL,
  translation TEXT,
  context_notes TEXT,
  image_id INTEGER REFERENCES images(id) ON DELETE SET NULL,
  difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 5),
  mastery_score FLOAT DEFAULT 0.0 CHECK (mastery_score BETWEEN 0.0 AND 1.0),
  next_review TIMESTAMP,
  review_count INTEGER DEFAULT 0,
  correct_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Image Management (from Image Manager)
CREATE TABLE images (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  filename VARCHAR(255) NOT NULL,
  original_path TEXT NOT NULL,
  thumbnail_path TEXT,
  file_size BIGINT,
  dimensions JSONB, -- {width: number, height: number}
  mime_type VARCHAR(100),
  tags TEXT[] DEFAULT '{}',
  rating INTEGER CHECK (rating BETWEEN 0 AND 5),
  is_favorite BOOLEAN DEFAULT false,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Grammar Tracking (enhanced from MySpanishApp)
CREATE TABLE grammar_rules (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  session_id INTEGER REFERENCES learning_sessions(id) ON DELETE SET NULL,
  rule_name VARCHAR(255),
  phrase_structure TEXT NOT NULL,
  explanation TEXT,
  examples TEXT[],
  resource_link TEXT,
  difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 5),
  mastery_score FLOAT DEFAULT 0.0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Conjugation Practice (from Conjugation GUI)
CREATE TABLE verb_conjugations (
  id SERIAL PRIMARY KEY,
  verb VARCHAR(100) NOT NULL,
  infinitive VARCHAR(100) NOT NULL,
  verb_type VARCHAR(20), -- regular, irregular, stem-changing
  conjugations JSONB NOT NULL, -- All tense/person combinations
  difficulty_level INTEGER DEFAULT 1,
  frequency_rank INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conjugation_practice (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  verb VARCHAR(100) NOT NULL,
  tense VARCHAR(50) NOT NULL,
  person VARCHAR(10) NOT NULL,
  attempts INTEGER DEFAULT 0,
  correct_attempts INTEGER DEFAULT 0,
  last_practiced TIMESTAMP,
  average_response_time FLOAT, -- in milliseconds
  difficulty_score FLOAT DEFAULT 0.5,
  streak_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Subjunctive Practice (from Subjunctive Practice)
CREATE TABLE subjunctive_triggers (
  id SERIAL PRIMARY KEY,
  trigger_category VARCHAR(50) NOT NULL, -- wish, emotion, doubt, etc.
  trigger_phrase VARCHAR(255) NOT NULL,
  english_translation TEXT,
  example_sentences TEXT[],
  difficulty_level INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE subjunctive_practice (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  trigger_id INTEGER REFERENCES subjunctive_triggers(id),
  tense VARCHAR(50) NOT NULL,
  exercise_type VARCHAR(50), -- traditional, tblt, mood-contrast
  attempts INTEGER DEFAULT 0,
  correct_attempts INTEGER DEFAULT 0,
  last_practiced TIMESTAMP,
  mastery_score FLOAT DEFAULT 0.0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- User Progress and Streaks
CREATE TABLE user_streaks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
  activity_type VARCHAR(50) NOT NULL, -- conjugation, subjunctive, vocabulary
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  last_activity DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, activity_type)
);

-- Performance Indexes
CREATE INDEX idx_vocabulary_user_review ON vocabulary(user_id, next_review);
CREATE INDEX idx_conjugation_practice_user_verb ON conjugation_practice(user_id, verb, last_practiced);
CREATE INDEX idx_images_user_tags ON images USING GIN(user_id, tags);
CREATE INDEX idx_sessions_user_date ON learning_sessions(user_id, session_date);
CREATE INDEX idx_user_streaks_user_type ON user_streaks(user_id, activity_type);
```

**Phase 3: Data Migration Scripts** (4 hours)
```typescript
// Migration script structure
interface MigrationScript {
  migrateMySpanishApp(): Promise<void>;
  migrateConjugationGUI(): Promise<void>; 
  migrateSubjunctivePractice(): Promise<void>;
  migrateImageManager(): Promise<void>;
  validateMigration(): Promise<ValidationReport>;
}

// Sample migration function
async function migrateMySpanishApp() {
  const sqliteDb = new Database('MySpanishApp/my_spanish_app.db');
  const pgClient = new PrismaClient();

  // Migrate sessions
  const sessions = sqliteDb.prepare('SELECT * FROM sessions').all();
  for (const session of sessions) {
    await pgClient.learning_sessions.create({
      data: {
        // Map SQLite fields to PostgreSQL schema
        session_date: new Date(session.session_date),
        // ... other fields
      }
    });
  }

  // Migrate vocabulary with progress tracking
  const vocab = sqliteDb.prepare('SELECT * FROM vocab').all();
  for (const item of vocab) {
    await pgClient.vocabulary.create({
      data: {
        word_phrase: item.word_phrase,
        translation: item.translation,
        // Initialize spaced repetition fields
        next_review: new Date(Date.now() + 24 * 60 * 60 * 1000), // 1 day
        mastery_score: 0.0,
        // ... other fields
      }
    });
  }
}
```

#### Risk Mitigation

**Risk**: Data loss during migration  
**Likelihood**: Low | **Impact**: Critical  
**Mitigation**:
- Create full backups of all source databases
- Implement rollback procedures
- Test migration on copies first
- Validate data integrity at each step

**Risk**: Performance degradation vs SQLite  
**Likelihood**: Medium | **Impact**: High  
**Mitigation**:
- Benchmark critical queries before/after
- Implement connection pooling from day 1
- Add proper indexes for all query patterns
- Use EXPLAIN ANALYZE to optimize slow queries

---

### Task 1.3: Authentication & Authorization System
**Category**: Security  
**Effort**: 10 hours  
**Priority**: P0 (Critical)  
**Owner**: Senior Full-Stack Developer

#### Specific Deliverables
1. **JWT Authentication Service**: Complete auth service with token generation/validation
2. **User Registration/Login**: Secure endpoints with validation and rate limiting
3. **Password Reset Flow**: Email-based password reset with secure tokens
4. **Role-Based Access Control**: User roles (student, teacher, admin) with permissions
5. **OAuth Integration**: Google and Facebook social login
6. **Security Middleware**: Rate limiting, input validation, CORS configuration

#### Dependencies
- **Prerequisites**: Task 1.2 (Database with users table)
- **Blockers**: Email service provider decision (SendGrid, AWS SES)
- **Parallel Tasks**: Can develop while database migration is in progress

#### Resource Requirements
- **Personnel**: 1 Senior Developer
- **Tools**: bcrypt, jsonwebtoken, express-rate-limit, joi/zod
- **Services**: Email provider (SendGrid/AWS SES), OAuth app registrations
- **Budget**: $25/month for email service

#### Success Criteria
- [ ] Password security meets OWASP guidelines (bcrypt, complexity requirements)
- [ ] JWT tokens expire appropriately and can be refreshed
- [ ] Rate limiting prevents brute force attacks (max 5 failed attempts per IP/15min)
- [ ] OAuth flows work seamlessly without security vulnerabilities
- [ ] All endpoints properly validate user permissions
- [ ] Password reset flow is secure and user-friendly

#### Implementation Details

**JWT Service Implementation**
```typescript
interface AuthService {
  register(userData: RegisterRequest): Promise<AuthResponse>;
  login(credentials: LoginRequest): Promise<AuthResponse>;
  refreshToken(refreshToken: string): Promise<AuthResponse>;
  resetPassword(email: string): Promise<void>;
  confirmResetPassword(token: string, newPassword: string): Promise<void>;
  validateToken(token: string): Promise<User>;
}

interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

// Security Configuration
const SECURITY_CONFIG = {
  bcrypt: {
    saltRounds: 12, // High security, slower but safer
  },
  jwt: {
    accessTokenExpiry: '15m', // Short-lived for security
    refreshTokenExpiry: '7d', // Longer-lived for UX
    algorithm: 'HS256',
  },
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    maxAttempts: 5,
    skipSuccessfulRequests: true,
  },
  password: {
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true,
  }
};
```

**Security Middleware Stack**
```typescript
// Rate limiting
app.use('/api/auth', rateLimit({
  windowMs: SECURITY_CONFIG.rateLimit.windowMs,
  max: SECURITY_CONFIG.rateLimit.maxAttempts,
  message: 'Too many authentication attempts, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
}));

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  optionsSuccessStatus: 200,
}));

// Input validation
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

// Authentication middleware
function authenticate(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload;
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}

// Authorization middleware
function authorize(roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}
```

#### Risk Mitigation

**Risk**: Security vulnerabilities in auth implementation  
**Likelihood**: Medium | **Impact**: Critical  
**Mitigation**:
- Follow OWASP security guidelines strictly
- Use established libraries (passport.js, bcrypt) instead of custom crypto
- Implement comprehensive security testing
- Regular security audits and dependency updates

**Risk**: OAuth integration complexity  
**Likelihood**: Medium | **Impact**: Medium  
**Mitigation**:
- Start with manual registration/login, add OAuth as enhancement
- Use proven OAuth libraries (passport-google-oauth20)
- Implement graceful fallbacks for OAuth failures

---

## Week 2 Tasks

### Task 2.1: API Gateway and Routing
**Category**: Backend Infrastructure  
**Effort**: 16 hours  
**Priority**: P0 (Critical)  
**Owner**: Senior Full-Stack Developer

#### Specific Deliverables
1. **OpenAPI Specification**: Complete API documentation with all endpoints defined
2. **RESTful API Implementation**: All CRUD endpoints for every entity
3. **Input Validation Layer**: Comprehensive request validation using Joi/Zod
4. **Error Handling System**: Consistent error responses with proper HTTP codes
5. **API Versioning Strategy**: v1 namespace with migration path for future versions
6. **Rate Limiting & Security**: Per-endpoint rate limits and security headers

#### Dependencies
- **Prerequisites**: Task 1.2 (Database), Task 1.3 (Authentication)
- **Blockers**: None
- **Parallel Tasks**: Can start API design while auth is being implemented

#### Resource Requirements
- **Personnel**: 1 Senior Developer
- **Tools**: Express.js/Fastify, OpenAPI Generator, Postman/Insomnia
- **Infrastructure**: API Gateway service (optional), load balancer (staging)
- **Budget**: $50/month for API Gateway service (AWS API Gateway or similar)

#### Success Criteria
- [ ] All endpoints return consistent JSON structure
- [ ] Input validation catches all edge cases with helpful error messages
- [ ] API documentation is auto-generated and always up-to-date
- [ ] Response times < 100ms for simple queries, < 500ms for complex ones
- [ ] Proper HTTP status codes used throughout
- [ ] All endpoints have appropriate rate limiting

#### API Architecture Design

**Endpoint Structure**
```typescript
// Authentication Endpoints
POST   /api/v1/auth/register          // User registration
POST   /api/v1/auth/login             // User login
POST   /api/v1/auth/refresh           // Token refresh
POST   /api/v1/auth/logout            // User logout
POST   /api/v1/auth/reset-password    // Request password reset
PUT    /api/v1/auth/reset-password    // Confirm password reset

// User Management
GET    /api/v1/users/profile          // Get user profile
PUT    /api/v1/users/profile          // Update user profile
DELETE /api/v1/users/account          // Delete user account
GET    /api/v1/users/preferences      // Get user preferences
PUT    /api/v1/users/preferences      // Update user preferences

// Learning Sessions
GET    /api/v1/sessions               // List user sessions (paginated)
POST   /api/v1/sessions               // Create new session
GET    /api/v1/sessions/:id           // Get specific session
PUT    /api/v1/sessions/:id           // Update session
DELETE /api/v1/sessions/:id           // Delete session
PUT    /api/v1/sessions/:id/status    // Update session status

// Vocabulary Management
GET    /api/v1/vocabulary             // List vocabulary (paginated, filtered)
POST   /api/v1/vocabulary             // Add vocabulary item
GET    /api/v1/vocabulary/:id         // Get specific vocabulary item
PUT    /api/v1/vocabulary/:id         // Update vocabulary item
DELETE /api/v1/vocabulary/:id         // Delete vocabulary item
GET    /api/v1/vocabulary/due-review  // Get items due for review
POST   /api/v1/vocabulary/:id/review  // Submit review result

// Grammar Tracking
GET    /api/v1/grammar                // List grammar rules
POST   /api/v1/grammar                // Add grammar rule
GET    /api/v1/grammar/:id            // Get specific grammar rule
PUT    /api/v1/grammar/:id            // Update grammar rule
DELETE /api/v1/grammar/:id            // Delete grammar rule

// Conjugation Practice
GET    /api/v1/conjugation/verbs      // List available verbs
GET    /api/v1/conjugation/exercises  // Generate practice exercises
POST   /api/v1/conjugation/submit     // Submit conjugation answer
GET    /api/v1/conjugation/progress   // Get conjugation progress
GET    /api/v1/conjugation/stats      // Get detailed statistics

// Subjunctive Practice
GET    /api/v1/subjunctive/triggers   // List trigger types
GET    /api/v1/subjunctive/exercises  // Generate subjunctive exercises
POST   /api/v1/subjunctive/submit     // Submit subjunctive answer
GET    /api/v1/subjunctive/progress   // Get subjunctive progress
GET    /api/v1/subjunctive/scenarios  // Get TBLT scenarios

// Image Management
POST   /api/v1/images/upload          // Upload image
GET    /api/v1/images                 // List user images
GET    /api/v1/images/:id             // Get specific image
PUT    /api/v1/images/:id             // Update image metadata
DELETE /api/v1/images/:id             // Delete image
GET    /api/v1/images/:id/thumbnail   // Get image thumbnail

// Analytics & Progress
GET    /api/v1/analytics/overview     // Overall progress summary
GET    /api/v1/analytics/streaks      // Streak information
GET    /api/v1/analytics/weak-areas   // Identified weak areas
GET    /api/v1/analytics/time-series  // Progress over time
GET    /api/v1/analytics/export       // Export analytics data

// Teachers (for tutoring sessions)
GET    /api/v1/teachers               // List available teachers
POST   /api/v1/teachers               // Add teacher (admin only)
GET    /api/v1/teachers/:id           // Get teacher details
PUT    /api/v1/teachers/:id           // Update teacher info
```

**Response Structure Standardization**
```typescript
// Success Response
interface APIResponse<T> {
  success: true;
  data: T;
  meta?: {
    pagination?: {
      page: number;
      limit: number;
      total: number;
      totalPages: number;
    };
    timestamp: string;
    version: string;
  };
}

// Error Response
interface APIErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
    timestamp: string;
    path: string;
  };
}

// Example implementations
async function getVocabulary(req: Request, res: Response) {
  try {
    const { page = 1, limit = 20, search, difficulty } = req.query;
    const offset = (Number(page) - 1) * Number(limit);

    const whereClause = {
      user_id: req.user!.id,
      ...(search && {
        OR: [
          { word_phrase: { contains: search as string, mode: 'insensitive' } },
          { translation: { contains: search as string, mode: 'insensitive' } }
        ]
      }),
      ...(difficulty && { difficulty_level: Number(difficulty) })
    };

    const [vocabulary, total] = await Promise.all([
      prisma.vocabulary.findMany({
        where: whereClause,
        skip: offset,
        take: Number(limit),
        orderBy: { created_at: 'desc' },
        include: { image: true }
      }),
      prisma.vocabulary.count({ where: whereClause })
    ]);

    res.json({
      success: true,
      data: vocabulary,
      meta: {
        pagination: {
          page: Number(page),
          limit: Number(limit),
          total,
          totalPages: Math.ceil(total / Number(limit))
        },
        timestamp: new Date().toISOString(),
        version: 'v1'
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: {
        code: 'VOCABULARY_FETCH_ERROR',
        message: 'Failed to fetch vocabulary',
        details: process.env.NODE_ENV === 'development' ? error.message : undefined,
        timestamp: new Date().toISOString(),
        path: req.path
      }
    });
  }
}
```

**Input Validation System**
```typescript
import { z } from 'zod';

// Validation schemas
const VocabularySchema = z.object({
  word_phrase: z.string().min(1).max(255),
  translation: z.string().optional(),
  context_notes: z.string().optional(),
  difficulty_level: z.number().int().min(1).max(5).default(1),
  image_id: z.number().int().optional(),
});

const ConjugationExerciseSchema = z.object({
  tenses: z.array(z.string()).min(1),
  persons: z.array(z.string()).min(1),
  verb_types: z.array(z.string()).optional(),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']).default('intermediate'),
  count: z.number().int().min(1).max(50).default(10),
});

// Validation middleware
function validate(schema: z.ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          success: false,
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Invalid request data',
            details: error.errors,
            timestamp: new Date().toISOString(),
            path: req.path
          }
        });
      }
      throw error;
    }
  };
}

// Usage
app.post('/api/v1/vocabulary', 
  authenticate, 
  validate(VocabularySchema), 
  createVocabulary
);
```

#### Risk Mitigation

**Risk**: API design changes requiring frontend updates  
**Likelihood**: High | **Impact**: Medium  
**Mitigation**:
- Create comprehensive API specification before implementation
- Use contract-first development with OpenAPI
- Implement API versioning from day 1
- Regular API review sessions with frontend team

**Risk**: Performance issues with complex queries  
**Likelihood**: Medium | **Impact**: High  
**Mitigation**:
- Implement database query optimization from the start
- Add response caching for read-heavy endpoints
- Use database indexes for all query patterns
- Monitor API performance with APM tools

---

### Task 2.2: Base UI Component System
**Category**: Frontend Infrastructure  
**Effort**: 20 hours  
**Priority**: P0 (Critical)  
**Owner**: UI/UX Developer + Senior Developer

#### Specific Deliverables
1. **Design System Documentation**: Complete color palette, typography, spacing system
2. **Component Library**: 20+ reusable React components with TypeScript
3. **Storybook Setup**: Interactive component documentation and testing
4. **Theme Provider**: Dark/light mode support with CSS custom properties
5. **Responsive Grid System**: Mobile-first responsive layout components
6. **Accessibility Implementation**: WCAG 2.1 AA compliance for all components

#### Dependencies
- **Prerequisites**: Task 1.1 (Project Architecture)
- **Blockers**: Design system approval from stakeholders
- **Parallel Tasks**: Can develop alongside API implementation

#### Resource Requirements
- **Personnel**: 1 UI/UX Developer + 0.5 FTE Senior Developer
- **Tools**: React, TypeScript, Storybook, Tailwind CSS, Headless UI
- **Design**: Figma/Adobe XD for design system, icon library (Heroicons/Lucide)
- **Budget**: $20/month for Figma Pro, icon library license if needed

#### Success Criteria
- [ ] All components are fully responsive (mobile, tablet, desktop)
- [ ] Lighthouse accessibility score > 95 for all component stories
- [ ] Components work in both light and dark themes
- [ ] Storybook documentation covers all component variants
- [ ] TypeScript provides full type safety for props
- [ ] Components follow consistent naming and API patterns

#### Component Architecture Design

**Design System Foundation**
```css
/* CSS Custom Properties for Theme System */
:root {
  /* Colors */
  --color-primary-50: #f0f9ff;
  --color-primary-100: #e0f2fe;
  --color-primary-500: #0ea5e9;
  --color-primary-600: #0284c7;
  --color-primary-700: #0369a1;
  --color-primary-900: #0c4a6e;

  /* Typography */
  --font-family-sans: 'Inter', system-ui, sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Courier New', monospace;
  
  /* Font Sizes (Mobile First) */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  
  /* Spacing */
  --space-1: 0.25rem;    /* 4px */
  --space-2: 0.5rem;     /* 8px */
  --space-3: 0.75rem;    /* 12px */
  --space-4: 1rem;       /* 16px */
  --space-6: 1.5rem;     /* 24px */
  --space-8: 2rem;       /* 32px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */

  /* Breakpoints */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
}

/* Dark Theme */
[data-theme='dark'] {
  --color-background: #0f172a;
  --color-surface: #1e293b;
  --color-text-primary: #f1f5f9;
  --color-text-secondary: #cbd5e1;
  --color-border: #334155;
}

/* Light Theme */
[data-theme='light'] {
  --color-background: #ffffff;
  --color-surface: #f8fafc;
  --color-text-primary: #1e293b;
  --color-text-secondary: #64748b;
  --color-border: #e2e8f0;
}
```

**Core Component Library**
```typescript
// Button Component with all variants
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  children,
  onClick,
  type = 'button',
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        fullWidth && 'w-full',
        (disabled || loading) && 'opacity-50 cursor-not-allowed',
      )}
      {...props}
    >
      {loading && <Spinner className="mr-2 h-4 w-4" />}
      {children}
    </button>
  );
};

// Input Component with validation states
interface InputProps {
  label?: string;
  placeholder?: string;
  error?: string;
  helpText?: string;
  required?: boolean;
  disabled?: boolean;
  type?: 'text' | 'email' | 'password' | 'number' | 'search';
  value?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Input: React.FC<InputProps> = ({
  label,
  placeholder,
  error,
  helpText,
  required = false,
  disabled = false,
  type = 'text',
  value,
  onChange,
  onBlur,
  icon,
  fullWidth = true,
  ...props
}) => {
  const id = useId();
  
  return (
    <div className={cn('space-y-1', fullWidth && 'w-full')}>
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {icon}
          </div>
        )}
        
        <input
          id={id}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          onBlur={onBlur}
          disabled={disabled}
          className={cn(
            'block w-full rounded-md border shadow-sm',
            'focus:border-blue-500 focus:ring-blue-500',
            icon && 'pl-10',
            error 
              ? 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500'
              : 'border-gray-300',
            disabled && 'bg-gray-50 text-gray-500 cursor-not-allowed'
          )}
          {...props}
        />
      </div>
      
      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
      
      {helpText && !error && (
        <p className="text-sm text-gray-500">
          {helpText}
        </p>
      )}
    </div>
  );
};

// Card Component for content sections
interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  variant?: 'default' | 'highlighted' | 'outlined';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  actions,
  variant = 'default',
  padding = 'md',
  className,
}) => {
  const variantClasses = {
    default: 'bg-white shadow-sm border border-gray-200',
    highlighted: 'bg-blue-50 shadow-sm border border-blue-200',
    outlined: 'bg-transparent border-2 border-dashed border-gray-300',
  };
  
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  return (
    <div className={cn(
      'rounded-lg',
      variantClasses[variant],
      paddingClasses[padding],
      className
    )}>
      {(title || subtitle || actions) && (
        <div className="flex items-start justify-between mb-4">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-gray-900">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-gray-600">
                {subtitle}
              </p>
            )}
          </div>
          {actions && (
            <div className="flex space-x-2">
              {actions}
            </div>
          )}
        </div>
      )}
      {children}
    </div>
  );
};
```

**Storybook Configuration**
```typescript
// .storybook/main.ts
export default {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
    '@storybook/addon-viewport',
    '@storybook/addon-docs',
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
};

// Button.stories.tsx
export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    docs: {
      description: {
        component: 'A versatile button component with multiple variants and states.',
      },
    },
  },
  argTypes: {
    variant: {
      control: { type: 'radio' },
      options: ['primary', 'secondary', 'danger', 'ghost'],
    },
    size: {
      control: { type: 'radio' },
      options: ['sm', 'md', 'lg'],
    },
    loading: { control: 'boolean' },
    disabled: { control: 'boolean' },
    fullWidth: { control: 'boolean' },
  },
} as Meta<typeof Button>;

export const Primary: Story<ButtonProps> = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
};

export const AllVariants: Story = () => (
  <div className="space-y-4">
    <div className="flex space-x-4">
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="danger">Danger</Button>
      <Button variant="ghost">Ghost</Button>
    </div>
    <div className="flex space-x-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
    <div className="flex space-x-4">
      <Button loading>Loading</Button>
      <Button disabled>Disabled</Button>
      <Button fullWidth>Full Width</Button>
    </div>
  </div>
);
```

#### Risk Mitigation

**Risk**: Design system inconsistencies across components  
**Likelihood**: High | **Impact**: Medium  
**Mitigation**:
- Create design tokens and CSS custom properties first
- Use consistent prop naming conventions
- Regular design system reviews with UI/UX team
- Automated visual regression testing with Chromatic

**Risk**: Accessibility compliance issues  
**Likelihood**: Medium | **Impact**: High  
**Mitigation**:
- Use proven accessible components (Headless UI, Radix UI)
- Implement automated accessibility testing (axe-core)
- Regular accessibility audits with screen readers
- ARIA attributes and semantic HTML by default

---

This detailed breakdown continues for all remaining tasks. Each task includes the same level of detail with specific deliverables, dependencies, resource requirements, success criteria, technical implementation details, and risk mitigation strategies.

Would you like me to continue with the remaining tasks in similar detail?