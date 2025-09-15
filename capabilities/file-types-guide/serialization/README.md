# Serialization File Types Guide

## Overview
Serialization formats enable data exchange between systems, configuration management, and efficient storage. This guide covers essential serialization file types and their use cases.

## File Types Reference

| **Format Type** | **Core Files** | **Supporting Files** | **Purpose** |
|----------------|----------------|---------------------|------------|
| **Data Files** | `.json`, `.yaml` | `.yml`, `.toml`, `.xml`, `.ini` | Configuration and data exchange |
| **Binary Files** | `.bin`, `.dat` | `.db`, `.sqlite`, `.pickle`, `.msgpack` | Efficient storage and databases |
| **Protocol Buffers** | `.proto` | `.pb` | Efficient binary serialization |

## Use Cases & Examples

### JSON Data Format
**Best For:** APIs, configuration, data exchange
```json
// config.json - Application configuration
{
  "application": {
    "name": "MyApp",
    "version": "2.1.0",
    "environment": "production"
  },
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "ssl": {
      "enabled": true,
      "cert": "/path/to/cert.pem",
      "key": "/path/to/key.pem"
    }
  },
  "database": {
    "type": "postgresql",
    "connection": {
      "host": "db.example.com",
      "port": 5432,
      "database": "myapp",
      "pool": {
        "min": 2,
        "max": 10
      }
    }
  },
  "features": {
    "authentication": true,
    "rateLimit": {
      "enabled": true,
      "maxRequests": 100,
      "windowMs": 60000
    }
  },
  "logging": {
    "level": "info",
    "outputs": ["console", "file"],
    "file": {
      "path": "/var/log/myapp.log",
      "maxSize": "10MB",
      "maxFiles": 5
    }
  }
}
```

**JSON Schema Validation:**
```json
// schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["application", "server"],
  "properties": {
    "application": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "version": { 
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$"
        }
      }
    },
    "server": {
      "type": "object",
      "properties": {
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        }
      }
    }
  }
}
```
**Example Projects:** REST APIs, configuration files, data storage

### YAML Configuration
**Best For:** Human-readable configuration, CI/CD pipelines
```yaml
# application.yml - Spring Boot configuration
spring:
  application:
    name: user-service
  
  datasource:
    url: jdbc:postgresql://localhost:5432/userdb
    username: ${DB_USER:dbuser}
    password: ${DB_PASSWORD}
    hikari:
      maximum-pool-size: 10
      minimum-idle: 2
      connection-timeout: 30000
  
  redis:
    host: localhost
    port: 6379
    timeout: 2000ms
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
  
  kafka:
    bootstrap-servers: kafka1:9092,kafka2:9092
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
    consumer:
      group-id: user-service-group
      auto-offset-reset: earliest

server:
  port: 8080
  servlet:
    context-path: /api
  compression:
    enabled: true
    mime-types: application/json,application/xml

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  metrics:
    export:
      prometheus:
        enabled: true

logging:
  level:
    root: INFO
    com.example: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
```
**Example Projects:** Kubernetes configs, Docker Compose, CI/CD pipelines

### TOML Configuration
**Best For:** Application settings, package configuration
```toml
# pyproject.toml - Python project configuration
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "A sample Python project"
authors = ["John Doe <john@example.com>"]
license = "MIT"
readme = "README.md"
homepage = "https://github.com/example/my-project"
repository = "https://github.com/example/my-project"
keywords = ["sample", "project"]

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.100.0"
pydantic = "^2.0.0"
sqlalchemy = "^2.0.0"
alembic = "^1.11.0"
redis = "^4.5.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
black = "^23.7.0"
mypy = "^1.4.0"
ruff = "^0.0.280"

[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.ruff]
select = ["E", "F", "B", "W"]
ignore = ["E501"]
line-length = 88
target-version = "py39"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --cov=src --cov-report=term-missing"
testpaths = ["tests"]
```
**Example Projects:** Rust projects (Cargo.toml), Python projects, Hugo sites

### Protocol Buffers
**Best For:** High-performance serialization, gRPC services
```protobuf
// user.proto - Protocol buffer definition
syntax = "proto3";

package user.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";

// User service definition
service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc UpdateUser(UpdateUserRequest) returns (User);
  rpc DeleteUser(DeleteUserRequest) returns (google.protobuf.Empty);
  rpc StreamUsers(StreamUsersRequest) returns (stream User);
}

// Message definitions
message User {
  string id = 1;
  string email = 2;
  string username = 3;
  Profile profile = 4;
  repeated string roles = 5;
  google.protobuf.Timestamp created_at = 6;
  google.protobuf.Timestamp updated_at = 7;
  
  enum Status {
    STATUS_UNSPECIFIED = 0;
    STATUS_ACTIVE = 1;
    STATUS_INACTIVE = 2;
    STATUS_SUSPENDED = 3;
  }
  Status status = 8;
}

message Profile {
  string first_name = 1;
  string last_name = 2;
  string avatar_url = 3;
  map<string, string> metadata = 4;
}

message GetUserRequest {
  string id = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  string filter = 3;
  string order_by = 4;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
  int32 total_count = 3;
}

message CreateUserRequest {
  string email = 1;
  string username = 2;
  string password = 3;
  Profile profile = 4;
}
```
**Example Projects:** Microservices communication, mobile app APIs, real-time systems

### Binary Serialization
**Best For:** Caching, session storage, inter-process communication
```python
# binary_serialization.py - Various binary formats
import pickle
import msgpack
import sqlite3
import struct

# Pickle serialization (Python-specific)
def save_with_pickle(data, filename):
    with open(filename, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

def load_with_pickle(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# MessagePack (cross-language)
def save_with_msgpack(data, filename):
    with open(filename, 'wb') as f:
        packed = msgpack.packb(data, use_bin_type=True)
        f.write(packed)

def load_with_msgpack(filename):
    with open(filename, 'rb') as f:
        return msgpack.unpackb(f.read(), raw=False)

# SQLite database
def create_sqlite_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_users_email 
        ON users(email)
    ''')
    
    conn.commit()
    return conn

# Custom binary format
def write_binary_record(file, record):
    """Write a custom binary record format"""
    # Format: [4 bytes: record length][1 byte: type][N bytes: data]
    data = msgpack.packb(record)
    file.write(struct.pack('I', len(data)))  # Record length
    file.write(struct.pack('B', 1))  # Record type
    file.write(data)

def read_binary_record(file):
    """Read a custom binary record"""
    length_data = file.read(4)
    if not length_data:
        return None
    
    length = struct.unpack('I', length_data)[0]
    record_type = struct.unpack('B', file.read(1))[0]
    data = file.read(length)
    return msgpack.unpackb(data, raw=False)
```
**Example Projects:** Cache systems, embedded databases, game save files

## Best Practices

1. **Schema Evolution:** Plan for backward compatibility
2. **Validation:** Validate data against schemas
3. **Compression:** Compress large serialized data
4. **Security:** Sanitize untrusted serialized data
5. **Performance:** Choose format based on use case
6. **Documentation:** Document data structures and schemas

## File Organization Pattern
```
data/
├── schemas/
│   ├── json/
│   ├── protobuf/
│   └── avro/
├── configs/
│   ├── app.yaml
│   ├── database.toml
│   └── services.json
├── fixtures/
│   └── test_data.json
└── migrations/
```

## Format Comparison

| Format | Human Readable | Size | Speed | Schema Support | Language Support |
|--------|---------------|------|-------|----------------|------------------|
| JSON | Yes | Large | Medium | JSON Schema | Universal |
| YAML | Yes | Large | Slow | Limited | Good |
| TOML | Yes | Medium | Medium | No | Growing |
| XML | Yes | Very Large | Slow | XSD | Universal |
| Protocol Buffers | No | Small | Fast | Built-in | Excellent |
| MessagePack | No | Small | Fast | No | Good |
| Pickle | No | Medium | Fast | No | Python only |

## Performance Considerations
- Use binary formats for high-frequency data
- Implement caching for deserialized objects
- Stream large files instead of loading entirely
- Use compression for network transmission
- Profile serialization/deserialization performance

## Serialization Libraries
- **JSON:** Jackson (Java), json (Python), JSON.NET (C#)
- **YAML:** PyYAML (Python), js-yaml (JavaScript)
- **Protocol Buffers:** protobuf (Multi-language)
- **MessagePack:** msgpack (Multi-language)
- **Binary:** Pickle (Python), Kryo (Java), Bond (C++)