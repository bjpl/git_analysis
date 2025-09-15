# Documentation File Types Guide

## Overview
Comprehensive documentation is essential for project maintainability, user adoption, and team collaboration. This guide covers file types for creating various forms of technical documentation.

## File Types Reference

| **Documentation Type** | **Core Files** | **Supporting Files** | **Purpose** |
|-----------------------|----------------|---------------------|------------|
| **API Documentation** | `.md`, `.yaml` (OpenAPI) | `.json`, `.html`, `.adoc` | API reference and integration guides |
| **Knowledge Bases** | `.md`, `.mdx`, `.rst` | `.adoc`, `.html`, `.wiki` | Team wikis and documentation sites |
| **Technical Tutorials** | `.md`, `.ipynb` | `.html`, `.jsx`, `.mdx` | Learning materials and guides |
| **Markdown Processors** | `.md`, `.mdx` | `.html`, `.pdf`, `.docx` | Content transformation and publishing |

## Use Cases & Examples

### API Documentation
**Best For:** Developer references, API contracts, integration guides
```yaml
# openapi.yaml - OpenAPI/Swagger specification
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: API for managing user accounts
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      summary: List all users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
        name:
          type: string
```
**Example Projects:** REST API docs, SDK references, webhook documentation

### Knowledge Bases
**Best For:** Internal wikis, product documentation, FAQ systems
```markdown
# System Architecture

## Overview
Our system follows a microservices architecture with the following components:

### Services
- **Auth Service**: Handles authentication and authorization
- **User Service**: Manages user profiles and preferences
- **Payment Service**: Processes transactions and billing

## Getting Started

### Prerequisites
- Node.js 18+
- Docker
- PostgreSQL 14+

### Installation
1. Clone the repository
   ```bash
   git clone https://github.com/example/project
   ```
2. Install dependencies
   ```bash
   npm install
   ```
3. Set up environment variables
   ```bash
   cp .env.example .env
   ```

### Configuration
See [Configuration Guide](./configuration.md) for detailed setup instructions.
```
**Example Projects:** Developer portals, team handbooks, troubleshooting guides

### Technical Tutorials
**Best For:** Educational content, onboarding materials, how-to guides
```mdx
# Building a REST API with Node.js

import { CodeBlock } from './components/CodeBlock'
import { Alert } from './components/Alert'

## Introduction
In this tutorial, we'll build a RESTful API using Node.js and Express.

<Alert type="info">
  This tutorial assumes basic knowledge of JavaScript and Node.js
</Alert>

## Step 1: Project Setup

First, create a new directory and initialize npm:

<CodeBlock language="bash">
mkdir my-api
cd my-api
npm init -y
</CodeBlock>

## Step 2: Install Dependencies

<CodeBlock language="bash">
npm install express body-parser cors
npm install -D nodemon
</CodeBlock>

## Interactive Exercise

Try modifying the code below to add a new endpoint:

<CodeBlock live>
const express = require('express');
const app = express();

app.get('/hello', (req, res) => {
  res.json({ message: 'Hello World!' });
});

// Add your endpoint here

app.listen(3000);
</CodeBlock>
```
**Example Projects:** Interactive tutorials, coding bootcamps, technical courses

### Markdown Processors
**Best For:** Static site generation, document conversion, publishing workflows
```javascript
// markdown-processor.js
const markdown = require('markdown-it')({
  html: true,
  linkify: true,
  typographer: true
});
const hljs = require('highlight.js');

// Add syntax highlighting
markdown.use(require('markdown-it-highlightjs'), { hljs });

// Add custom plugins
markdown.use(require('markdown-it-anchor'));
markdown.use(require('markdown-it-toc-done-right'));

// Process markdown
const html = markdown.render(`
# My Document

## Table of Contents
[[toc]]

## Code Example
\`\`\`javascript
console.log('Hello World');
\`\`\`
`);
```
**Example Projects:** Blog generators, documentation sites, note converters

## Best Practices

1. **Structure:** Use clear hierarchical organization with consistent navigation
2. **Examples:** Include code examples and practical use cases
3. **Versioning:** Maintain documentation versions aligned with software releases
4. **Search:** Implement full-text search for large documentation sets
5. **Feedback:** Include feedback mechanisms and update based on user input
6. **Accessibility:** Ensure documentation is accessible (proper headings, alt text)

## File Organization Pattern
```
docs/
├── api/
│   ├── reference/
│   │   └── endpoints.md
│   └── guides/
│       └── authentication.md
├── tutorials/
│   ├── getting-started.md
│   └── advanced/
├── concepts/
│   └── architecture.md
├── changelog/
│   └── v1.0.0.md
└── _sidebar.md
```

## Documentation Patterns

### Frontmatter Metadata
```markdown
---
title: API Authentication Guide
description: Learn how to authenticate with our API
author: John Doe
date: 2024-01-15
tags: [api, authentication, security]
---

# API Authentication Guide
```

### Interactive Documentation
```html
<!-- Embedded API console -->
<div id="api-console">
  <select id="method">
    <option>GET</option>
    <option>POST</option>
  </select>
  <input type="text" id="endpoint" placeholder="/api/users">
  <button onclick="executeRequest()">Try it</button>
  <pre id="response"></pre>
</div>
```

## Documentation Generators

### Static Site Generators
- **Docusaurus:** React-based documentation sites
- **VuePress:** Vue-powered static sites
- **MkDocs:** Python-based documentation
- **Hugo:** Fast static site generator
- **Jekyll:** GitHub Pages compatible

### API Documentation Tools
- **Swagger UI:** Interactive API documentation
- **Redoc:** OpenAPI documentation
- **Postman:** API documentation and testing
- **Slate:** Beautiful API docs

## Performance Considerations
- Static generation for faster loading
- Search indexing for quick lookups
- Image optimization and lazy loading
- Code splitting for large documentation sets
- CDN deployment for global access