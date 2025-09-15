# Database Files Guide

## Overview
Database files define data structures, manage schema evolution, and populate initial data. This guide covers essential file types for database management and migrations.

## File Types Reference

| **File Type** | **Core Files** | **Supporting Files** | **Purpose** |
|--------------|----------------|---------------------|------------|
| **Schema Files** | `.sql`, `.prisma` | `.graphql`, `.dbml` | Database structure definition |
| **Migration Files** | `.sql`, `.js`, `.ts` | `.py`, `.rb` | Schema versioning and updates |
| **Seed Files** | `.sql`, `.json` | `.csv`, `.js`, `.py` | Test and initial data |

## Use Cases & Examples

### Schema Definition
**Best For:** Database design, table relationships, constraints
```sql
-- schema.sql - PostgreSQL schema
CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE app.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE app.posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app.users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    published BOOLEAN DEFAULT false,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_posts_user_id ON app.posts(user_id);
CREATE INDEX idx_posts_published ON app.posts(published) WHERE published = true;
CREATE INDEX idx_users_email ON app.users(email);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION app.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON app.users
    FOR EACH ROW
    EXECUTE FUNCTION app.update_updated_at();
```

**Prisma Schema:**
```prisma
// schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        String   @id @default(uuid())
  email     String   @unique
  username  String   @unique @db.VarChar(50)
  password  String
  posts     Post[]
  profile   Profile?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  
  @@index([email])
}

model Post {
  id          String    @id @default(uuid())
  title       String    @db.VarChar(200)
  content     String?
  published   Boolean   @default(false)
  publishedAt DateTime?
  author      User      @relation(fields: [authorId], references: [id])
  authorId    String
  tags        Tag[]
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt
  
  @@index([authorId])
  @@index([published])
}

model Tag {
  id    String @id @default(uuid())
  name  String @unique
  posts Post[]
}
```
**Example Projects:** User management systems, content platforms, e-commerce databases

### Database Migrations
**Best For:** Schema versioning, incremental updates, rollback capability
```javascript
// migrations/20240115_add_user_roles.js - Knex migration
exports.up = function(knex) {
  return knex.schema
    .createTable('roles', table => {
      table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
      table.string('name', 50).notNullable().unique();
      table.text('description');
      table.timestamps(true, true);
    })
    .createTable('user_roles', table => {
      table.uuid('user_id').references('id').inTable('users').onDelete('CASCADE');
      table.uuid('role_id').references('id').inTable('roles').onDelete('CASCADE');
      table.primary(['user_id', 'role_id']);
      table.timestamp('assigned_at').defaultTo(knex.fn.now());
    })
    .table('users', table => {
      table.boolean('is_active').defaultTo(true);
      table.timestamp('last_login_at');
    });
};

exports.down = function(knex) {
  return knex.schema
    .table('users', table => {
      table.dropColumn('is_active');
      table.dropColumn('last_login_at');
    })
    .dropTableIfExists('user_roles')
    .dropTableIfExists('roles');
};
```

**SQL Migration:**
```sql
-- migrations/V1__initial_schema.sql - Flyway migration
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);

-- migrations/V2__add_products.sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0
);

ALTER TABLE orders ADD COLUMN shipping_address TEXT;
```
**Example Projects:** Schema evolution, database versioning, deployment automation

### Seed Data
**Best For:** Development data, testing fixtures, demo content
```javascript
// seeds/01_users.js - Knex seed
exports.seed = async function(knex) {
  // Deletes ALL existing entries
  await knex('user_roles').del();
  await knex('posts').del();
  await knex('users').del();
  await knex('roles').del();
  
  // Insert roles
  const roles = await knex('roles').insert([
    { name: 'admin', description: 'System administrator' },
    { name: 'editor', description: 'Content editor' },
    { name: 'user', description: 'Regular user' }
  ]).returning('*');
  
  // Insert users
  const users = await knex('users').insert([
    {
      email: 'admin@example.com',
      username: 'admin',
      password_hash: '$2b$10$...' // bcrypt hash
    },
    {
      email: 'editor@example.com',
      username: 'editor',
      password_hash: '$2b$10$...'
    },
    {
      email: 'user@example.com',
      username: 'testuser',
      password_hash: '$2b$10$...'
    }
  ]).returning('*');
  
  // Assign roles
  await knex('user_roles').insert([
    { user_id: users[0].id, role_id: roles[0].id },
    { user_id: users[1].id, role_id: roles[1].id },
    { user_id: users[2].id, role_id: roles[2].id }
  ]);
  
  // Insert sample posts
  await knex('posts').insert([
    {
      author_id: users[1].id,
      title: 'Getting Started with Node.js',
      content: 'This is a sample post about Node.js...',
      published: true,
      published_at: new Date()
    },
    {
      author_id: users[1].id,
      title: 'Database Best Practices',
      content: 'Learn about database optimization...',
      published: false
    }
  ]);
};
```

**JSON Seed Data:**
```json
// seeds/products.json
[
  {
    "name": "Laptop",
    "category": "Electronics",
    "price": 999.99,
    "stock": 50,
    "specifications": {
      "cpu": "Intel i7",
      "ram": "16GB",
      "storage": "512GB SSD"
    }
  },
  {
    "name": "Wireless Mouse",
    "category": "Accessories",
    "price": 29.99,
    "stock": 200,
    "specifications": {
      "connectivity": "Bluetooth 5.0",
      "battery": "AA x2"
    }
  }
]
```
**Example Projects:** Test data generation, demo environments, development fixtures

## Best Practices

1. **Version Control:** Track all schema changes in version control
2. **Rollback Strategy:** Ensure migrations can be rolled back safely
3. **Idempotency:** Make migrations idempotent when possible
4. **Testing:** Test migrations on a copy of production data
5. **Documentation:** Document complex schema relationships
6. **Performance:** Consider index impact during migrations

## File Organization Pattern
```
database/
├── schema/
│   ├── tables/
│   │   ├── users.sql
│   │   └── posts.sql
│   ├── indexes/
│   └── triggers/
├── migrations/
│   ├── 001_initial_schema.sql
│   ├── 002_add_user_roles.sql
│   └── 003_add_audit_tables.sql
├── seeds/
│   ├── development/
│   │   └── sample_data.sql
│   └── test/
│       └── test_fixtures.sql
└── backups/
```

## Migration Strategies

### Timestamp-based Migrations
```bash
# Migration file naming
20240115143022_create_users_table.sql
20240116091545_add_email_verification.sql
20240117120000_create_posts_table.sql
```

### Version-based Migrations
```bash
# Flyway style
V1__Initial_schema.sql
V2__Add_user_roles.sql
V2.1__Fix_user_constraints.sql
```

## Database Tools

### Migration Tools
- **Flyway:** Java-based database migration tool
- **Liquibase:** Database schema change management
- **Knex.js:** SQL query builder with migrations
- **Prisma Migrate:** Type-safe database migrations
- **Alembic:** Python database migration tool

### Schema Design Tools
- **dbdiagram.io:** Database diagram design
- **DrawSQL:** Visual database design
- **DBeaver:** Universal database tool
- **TablePlus:** Modern database management

## Performance Considerations
- Add indexes after data import for faster initial load
- Use batch inserts for seed data
- Consider partition strategies for large tables
- Monitor migration execution time
- Plan maintenance windows for large migrations