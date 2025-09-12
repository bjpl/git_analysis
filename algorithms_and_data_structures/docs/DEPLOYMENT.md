# Deployment Guide

## Production Deployment and Configuration

This guide covers deploying the Interactive Algorithms Learning Platform in various production environments, from single-server deployments to enterprise-scale distributed systems.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Single Server Deployment](#single-server-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Performance Tuning](#performance-tuning)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Configuration](#security-configuration)
- [Backup and Recovery](#backup-and-recovery)
- [Scaling Strategies](#scaling-strategies)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Node.js**: Version 18.0.0 or higher
- **Memory**: Minimum 512MB RAM, recommended 2GB+
- **Storage**: 100MB for application, 1GB+ for user data
- **CPU**: 1 core minimum, 2+ cores recommended
- **Network**: Stable internet connection for updates

### Operating System Support

- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+
- **Windows**: Windows Server 2019+, Windows 10+
- **macOS**: macOS 10.15+ (development/testing)

### Required Dependencies

```bash
# System packages
sudo apt-get update
sudo apt-get install -y nodejs npm git curl

# Optional: Process manager
npm install -g pm2

# Optional: Reverse proxy
sudo apt-get install -y nginx
```

## Environment Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Application Configuration
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# Data Configuration
DATA_DIR=/var/lib/algorithms-platform
LOG_DIR=/var/log/algorithms-platform
CACHE_SIZE=256
MAX_USERS=1000

# Performance Settings
WORKER_PROCESSES=4
MAX_MEMORY=1024
TIMEOUT=30000

# Monitoring
LOG_LEVEL=info
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Security
AUTH_TIMEOUT=3600
RATE_LIMIT=100
CORS_ORIGIN=*

# Feature Flags
AUTOMATION_ENABLED=true
COLLABORATION_ENABLED=true
ADVANCED_METRICS=true
```

### Configuration Files

#### Production Config (`config/production.json`)
```json
{
  "server": {
    "port": 3000,
    "host": "0.0.0.0",
    "workers": 4,
    "timeout": 30000
  },
  "database": {
    "path": "/var/lib/algorithms-platform/db",
    "backup_interval": 3600,
    "compression": true
  },
  "logging": {
    "level": "info",
    "file": "/var/log/algorithms-platform/app.log",
    "max_size": "100MB",
    "rotate": true
  },
  "monitoring": {
    "metrics_port": 9090,
    "health_endpoint": "/health",
    "stats_endpoint": "/stats"
  }
}
```

## Single Server Deployment

### Manual Deployment

```bash
# Create application user
sudo useradd -r -m -d /opt/algorithms-platform algorithms
sudo usermod -s /bin/bash algorithms

# Create directories
sudo mkdir -p /var/lib/algorithms-platform
sudo mkdir -p /var/log/algorithms-platform
sudo chown -R algorithms:algorithms /var/lib/algorithms-platform
sudo chown -R algorithms:algorithms /var/log/algorithms-platform

# Switch to application user
sudo su - algorithms

# Clone and setup application
git clone <repository-url> /opt/algorithms-platform
cd /opt/algorithms-platform
npm ci --production
npm run build

# Copy configuration
cp config/.env.production .env

# Test the application
node index.js --test
```

### Systemd Service

Create `/etc/systemd/system/algorithms-platform.service`:

```ini
[Unit]
Description=Interactive Algorithms Learning Platform
After=network.target
Wants=network.target

[Service]
Type=simple
User=algorithms
Group=algorithms
WorkingDirectory=/opt/algorithms-platform
Environment=NODE_ENV=production
ExecStart=/usr/bin/node index.js
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=algorithms-platform
KillMode=mixed
TimeoutStopSec=30

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable algorithms-platform
sudo systemctl start algorithms-platform
sudo systemctl status algorithms-platform
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM node:18-alpine AS builder

# Install build dependencies
RUN apk add --no-cache git python3 make g++

WORKDIR /app
COPY package*.json ./
RUN npm ci --production && npm cache clean --force

# Production stage
FROM node:18-alpine AS production

# Create app user
RUN addgroup -g 1001 -S algorithms && \
    adduser -S algorithms -u 1001

# Install runtime dependencies
RUN apk add --no-cache dumb-init curl

WORKDIR /app

# Copy application code
COPY --chown=algorithms:algorithms . .
COPY --from=builder --chown=algorithms:algorithms /app/node_modules ./node_modules

# Create data directories
RUN mkdir -p /data/algorithms-platform && \
    chown -R algorithms:algorithms /data/algorithms-platform

USER algorithms

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node health-check.js

EXPOSE 3000

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "index.js"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  algorithms-platform:
    build: .
    restart: unless-stopped
    ports:
      - "3000:3000"
      - "9090:9090"
    environment:
      - NODE_ENV=production
      - DATA_DIR=/data
      - LOG_LEVEL=info
    volumes:
      - app-data:/data/algorithms-platform
      - app-logs:/var/log/algorithms-platform
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - algorithms-platform

volumes:
  app-data:
  app-logs:

networks:
  default:
    name: algorithms-platform
```

### Build and Deploy

```bash
# Build the Docker image
docker build -t algorithms-platform:latest .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f algorithms-platform

# Scale the service
docker-compose up -d --scale algorithms-platform=3
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance Setup

```bash
# Launch EC2 instance (t3.medium or larger)
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy application
git clone <repository-url>
cd algorithms-learning
docker-compose -f docker-compose.prod.yml up -d
```

#### ECS Deployment

```json
{
  "family": "algorithms-platform",
  "taskRoleArn": "arn:aws:iam::123456789012:role/AlgorithmsTaskRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/AlgorithmsExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "algorithms-platform",
      "image": "your-account.dkr.ecr.region.amazonaws.com/algorithms-platform:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "NODE_ENV", "value": "production"},
        {"name": "PORT", "value": "3000"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/algorithms-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Cloud Run Deployment

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/algorithms-platform

# Deploy to Cloud Run
gcloud run deploy algorithms-platform \
  --image gcr.io/PROJECT-ID/algorithms-platform \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10
```

#### GKE Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: algorithms-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: algorithms-platform
  template:
    metadata:
      labels:
        app: algorithms-platform
    spec:
      containers:
      - name: algorithms-platform
        image: gcr.io/PROJECT-ID/algorithms-platform:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        env:
        - name: NODE_ENV
          value: "production"
        - name: PORT
          value: "3000"
---
apiVersion: v1
kind: Service
metadata:
  name: algorithms-platform-service
spec:
  selector:
    app: algorithms-platform
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

## Performance Tuning

### Node.js Optimization

```bash
# Production startup options
node --max-old-space-size=1024 \
     --optimize-for-size \
     --gc-interval=100 \
     index.js
```

### Environment Variables for Performance

```bash
# V8 Engine optimization
NODE_OPTIONS="--max-old-space-size=1024 --optimize-for-size"

# UV Thread Pool (for file operations)
UV_THREADPOOL_SIZE=8

# Application-specific
WORKER_PROCESSES=4
MAX_CONCURRENT_USERS=100
CACHE_SIZE=256
REQUEST_TIMEOUT=30000
```

### System-Level Optimizations

```bash
# Increase file descriptor limits
echo "algorithms soft nofile 65536" >> /etc/security/limits.conf
echo "algorithms hard nofile 65536" >> /etc/security/limits.conf

# TCP/IP optimizations
echo "net.ipv4.tcp_fin_timeout = 30" >> /etc/sysctl.conf
echo "net.ipv4.tcp_tw_reuse = 1" >> /etc/sysctl.conf
echo "net.core.somaxconn = 65536" >> /etc/sysctl.conf
sysctl -p
```

## Monitoring and Logging

### Application Metrics

```javascript
// Custom metrics endpoint
app.get('/metrics', (req, res) => {
  const metrics = {
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    cpu: process.cpuUsage(),
    activeUsers: getUserCount(),
    requestsPerMinute: getRequestRate(),
    errorRate: getErrorRate()
  };
  res.json(metrics);
});
```

### Log Configuration

```json
{
  "logging": {
    "level": "info",
    "format": "json",
    "outputs": [
      {
        "type": "file",
        "path": "/var/log/algorithms-platform/app.log",
        "maxSize": "100MB",
        "maxFiles": 5
      },
      {
        "type": "syslog",
        "facility": "local0"
      }
    ]
  }
}
```

### Monitoring Stack

```yaml
# monitoring/docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
  
  node-exporter:
    image: prom/node-exporter
    ports:
      - "9100:9100"

volumes:
  grafana-data:
```

## Security Configuration

### HTTPS Configuration

```nginx
# /etc/nginx/sites-available/algorithms-platform
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Firewall Rules

```bash
# UFW configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### Application Security

```javascript
// Security middleware
app.use(helmet());
app.use(cors({ origin: process.env.CORS_ORIGIN || false }));
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: process.env.RATE_LIMIT || 100
}));
```

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/var/backups/algorithms-platform"
DATA_DIR="/var/lib/algorithms-platform"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Create backup
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $DATA_DIR .

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

# Upload to S3 (optional)
if [ -n "$AWS_S3_BUCKET" ]; then
    aws s3 cp $BACKUP_DIR/backup_$DATE.tar.gz s3://$AWS_S3_BUCKET/backups/
fi
```

### Cron Job Setup

```bash
# Add to crontab
crontab -e

# Backup every 6 hours
0 */6 * * * /opt/algorithms-platform/scripts/backup.sh

# Health check every 5 minutes
*/5 * * * * curl -f http://localhost:3000/health || systemctl restart algorithms-platform
```

### Recovery Procedures

```bash
# Restore from backup
sudo systemctl stop algorithms-platform
cd /var/lib/algorithms-platform
sudo tar -xzf /var/backups/algorithms-platform/backup_20240912_120000.tar.gz
sudo chown -R algorithms:algorithms .
sudo systemctl start algorithms-platform
```

## Scaling Strategies

### Horizontal Scaling

```bash
# Load balancer configuration
upstream algorithms_backend {
    least_conn;
    server 10.0.1.10:3000 weight=1 max_fails=2 fail_timeout=30s;
    server 10.0.1.11:3000 weight=1 max_fails=2 fail_timeout=30s;
    server 10.0.1.12:3000 weight=1 max_fails=2 fail_timeout=30s;
}

server {
    listen 80;
    location / {
        proxy_pass http://algorithms_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Auto-scaling with Docker Swarm

```yaml
version: '3.8'
services:
  algorithms-platform:
    image: algorithms-platform:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    networks:
      - algorithms-network

networks:
  algorithms-network:
    driver: overlay
```

## Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check memory usage
htop
ps aux | grep node

# Node.js memory debugging
node --inspect index.js

# Heap dump analysis
node --heapsnapshot-signal=SIGUSR2 index.js
kill -USR2 <pid>
```

#### Performance Issues
```bash
# CPU profiling
node --prof index.js
node --prof-process isolate-0x*.log > processed.txt

# Application metrics
curl http://localhost:3000/metrics
curl http://localhost:3000/health
```

#### Service Won't Start
```bash
# Check logs
journalctl -u algorithms-platform -f
sudo systemctl status algorithms-platform

# Check configuration
node -c index.js
npm run test:config
```

### Health Checks

```javascript
// health-check.js
const http = require('http');

const options = {
  hostname: 'localhost',
  port: 3000,
  path: '/health',
  timeout: 3000
};

const req = http.request(options, (res) => {
  if (res.statusCode === 200) {
    process.exit(0);
  } else {
    process.exit(1);
  }
});

req.on('error', () => process.exit(1));
req.on('timeout', () => process.exit(1));
req.end();
```

### Monitoring Dashboards

```bash
# Key metrics to monitor
- CPU usage < 80%
- Memory usage < 85%
- Response time < 200ms
- Error rate < 1%
- Disk space > 20% free
- Active connections
- Queue depth
```

## Support and Maintenance

### Regular Maintenance Tasks

```bash
# Weekly maintenance script
#!/bin/bash
# Update dependencies
npm audit fix

# Clean temporary files
find /tmp -name "algorithms-*" -mtime +7 -delete

# Rotate logs
logrotate /etc/logrotate.d/algorithms-platform

# Check disk space
df -h | grep -E "/(var|opt)" | awk '$5 > 80 {print "WARNING: " $0}'

# Test application health
curl -f http://localhost:3000/health || echo "Health check failed"
```

### Update Procedures

```bash
# Zero-downtime updates
# 1. Deploy to staging
# 2. Run integration tests
# 3. Blue-green deployment
# 4. Health checks
# 5. Switch traffic
# 6. Monitor for issues
```

This deployment guide provides comprehensive coverage of production deployment scenarios. Adapt the configurations based on your specific requirements, infrastructure, and scaling needs.