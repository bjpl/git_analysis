# APIs & Backend File Types Guide

## Overview
Backend services and APIs power modern applications with data processing, business logic, and integrations. This guide covers essential file types for building scalable backend systems and APIs.

## File Types Reference

| **API Type** | **Core Files** | **Supporting Files** | **Purpose** |
|-------------|----------------|---------------------|------------|
| **RESTful Services** | `.py`, `.js`, `.go`, `.java` | `.json`, `.yml`, `.env` | CRUD operations, microservices |
| **GraphQL Endpoints** | `.graphql`, `.gql` | `schema.graphql`, `.js`, `.ts` | Flexible data fetching |
| **Webhook Handlers** | `.js`, `.py`, `.go` | `.json`, `.env`, `.yml` | Event-driven automation |
| **Serverless Functions** | `.js`, `.py`, `.go` | `serverless.yml`, `function.json` | Scalable event processing |

## Use Cases & Examples

### RESTful Services
**Best For:** CRUD operations, microservices, standard API patterns
```javascript
// api/users.js - Express.js REST API
const express = require('express');
const router = express.Router();

// GET /api/users
router.get('/', async (req, res) => {
  const users = await User.findAll();
  res.json(users);
});

// POST /api/users
router.post('/', async (req, res) => {
  const user = await User.create(req.body);
  res.status(201).json(user);
});

// PUT /api/users/:id
router.put('/:id', async (req, res) => {
  const user = await User.findByIdAndUpdate(req.params.id, req.body);
  res.json(user);
});

module.exports = router;
```
**Example Projects:** User management APIs, e-commerce backends, inventory systems

### GraphQL Endpoints
**Best For:** Complex data relationships, mobile backends, flexible queries
```graphql
# schema.graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
}

type Query {
  users(limit: Int = 10): [User!]!
  user(id: ID!): User
  posts(authorId: ID): [Post!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
}
```
**Example Projects:** Social media APIs, content management systems, real-time dashboards

### Webhook Handlers
**Best For:** Third-party integrations, payment processing, event notifications
```python
# webhook_handler.py - Flask webhook
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/github', methods=['POST'])
def github_webhook():
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process webhook event
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    if event_type == 'push':
        handle_push_event(payload)
    elif event_type == 'pull_request':
        handle_pr_event(payload)
    
    return jsonify({'status': 'processed'}), 200
```
**Example Projects:** CI/CD triggers, payment confirmations, chat bot integrations

### Serverless Functions
**Best For:** Event processing, scheduled tasks, auto-scaling workloads
```javascript
// lambda/imageProcessor.js - AWS Lambda
exports.handler = async (event) => {
  const { Records } = event;
  
  for (const record of Records) {
    const bucket = record.s3.bucket.name;
    const key = record.s3.object.key;
    
    // Process uploaded image
    const image = await getImageFromS3(bucket, key);
    const resized = await resizeImage(image);
    await saveToS3(bucket, `resized/${key}`, resized);
  }
  
  return {
    statusCode: 200,
    body: JSON.stringify({ processed: Records.length })
  };
};
```
**Example Projects:** Image processors, data pipelines, notification services

## Best Practices

1. **API Versioning:** Use URL or header-based versioning (`/api/v1/`)
2. **Authentication:** Implement JWT, OAuth, or API keys
3. **Rate Limiting:** Protect against abuse with rate limits
4. **Error Handling:** Consistent error responses with proper HTTP codes
5. **Documentation:** Use OpenAPI/Swagger for API documentation
6. **Validation:** Input validation and sanitization
7. **Monitoring:** Implement logging and metrics collection

## File Organization Pattern
```
backend/
├── src/
│   ├── controllers/
│   │   ├── userController.js
│   │   └── authController.js
│   ├── models/
│   │   └── User.js
│   ├── routes/
│   │   ├── api.js
│   │   └── auth.js
│   ├── middleware/
│   │   ├── auth.js
│   │   └── validation.js
│   └── services/
│       └── emailService.js
├── config/
│   └── database.js
├── tests/
│   └── api.test.js
└── server.js
```

## API Patterns

### Authentication Middleware
```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');

module.exports = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

### OpenAPI Documentation
```yaml
# openapi.yml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

## Performance Considerations
- Database connection pooling
- Response caching with Redis
- Query optimization and indexing
- Async/await for non-blocking operations
- Load balancing across instances
- CDN for static assets

## Tools & Frameworks
- **Frameworks:** Express, FastAPI, Gin, Spring Boot
- **GraphQL:** Apollo Server, GraphQL Yoga, Hasura
- **Serverless:** AWS Lambda, Vercel Functions, Netlify Functions
- **Testing:** Postman, Insomnia, Jest, pytest
- **Documentation:** Swagger/OpenAPI, GraphQL Playground