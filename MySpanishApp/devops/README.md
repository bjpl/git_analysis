# SpanishMaster DevOps Infrastructure

## 🚀 Overview

This directory contains the complete DevOps infrastructure for SpanishMaster, a production-ready Spanish learning application. The infrastructure is designed with high availability, security, and scalability in mind.

## 📁 Directory Structure

```
devops/
├── docker/                 # Docker configurations
│   ├── nginx.conf          # Nginx reverse proxy configuration
│   └── redis.conf          # Redis configuration
├── kubernetes/             # Kubernetes manifests
│   ├── namespace.yml       # Namespace definitions
│   ├── configmap.yml      # Configuration management
│   ├── secrets.yml        # Secret management
│   ├── deployment.yml     # Application deployments
│   ├── service.yml        # Service definitions
│   ├── ingress.yml        # Ingress controllers
│   ├── pvc.yml           # Persistent volume claims
│   └── hpa.yml           # Horizontal Pod Autoscaler
├── terraform/             # Infrastructure as Code
│   ├── main.tf           # Main Terraform configuration
│   ├── variables.tf      # Variable definitions
│   └── outputs.tf        # Output values
├── monitoring/           # Monitoring and observability
│   ├── prometheus.yml    # Prometheus configuration
│   ├── alert-rules.yml   # Alerting rules
│   ├── grafana-dashboard.json # Grafana dashboard
│   └── elk-stack.yml     # ELK stack for logging
├── security/            # Security configurations
│   ├── vault-config.hcl  # HashiCorp Vault config
│   ├── vault-policies.hcl # Vault policies
│   └── security-policies.yml # K8s security policies
└── backup-restore.yml   # Backup and disaster recovery
```

## 🛠 Core Components

### 1. **Containerization**
- **Multi-stage Dockerfile** optimized for Python Qt applications
- **Docker Compose** for local development with full stack
- **Production-ready** container images with security scanning

### 2. **Kubernetes Orchestration**
- **Production-grade** Kubernetes manifests
- **Auto-scaling** with HPA and VPA
- **High availability** with pod anti-affinity rules
- **Rolling updates** with zero downtime

### 3. **Infrastructure as Code**
- **Terraform** for AWS infrastructure provisioning
- **EKS cluster** with managed node groups
- **RDS PostgreSQL** with automated backups
- **ElastiCache Redis** for caching layer

### 4. **CI/CD Pipeline**
- **GitHub Actions** with comprehensive testing
- **Multi-environment** deployments (dev, staging, prod)
- **Security scanning** with Trivy and CodeQL
- **Performance regression** detection

### 5. **Monitoring & Observability**
- **Prometheus** for metrics collection
- **Grafana** for visualization and dashboards
- **ELK Stack** for centralized logging
- **Custom alerts** for business and technical metrics

### 6. **Security**
- **HashiCorp Vault** for secrets management
- **Network policies** for micro-segmentation
- **Pod Security Policies** and RBAC
- **TLS encryption** for all communications

### 7. **Backup & Disaster Recovery**
- **Automated daily backups** for database and application data
- **Cross-region replication** to S3
- **Point-in-time recovery** procedures
- **Disaster recovery** runbooks

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- kubectl and Helm
- Terraform >= 1.0
- AWS CLI configured
- GitHub repository secrets configured

### Local Development

1. **Start the full stack locally:**
   ```bash
   docker-compose up -d
   ```

2. **Access services:**
   - Application: http://localhost:8080
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

### Production Deployment

1. **Provision infrastructure:**
   ```bash
   cd terraform/
   terraform init
   terraform plan
   terraform apply
   ```

2. **Deploy to Kubernetes:**
   ```bash
   # Apply manifests in order
   kubectl apply -f kubernetes/namespace.yml
   kubectl apply -f kubernetes/secrets.yml
   kubectl apply -f kubernetes/configmap.yml
   kubectl apply -f kubernetes/pvc.yml
   kubectl apply -f kubernetes/deployment.yml
   kubectl apply -f kubernetes/service.yml
   kubectl apply -f kubernetes/ingress.yml
   kubectl apply -f kubernetes/hpa.yml
   ```

3. **Setup monitoring:**
   ```bash
   kubectl apply -f monitoring/elk-stack.yml
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `production` |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `LOG_LEVEL` | Application log level | `INFO` |

### Secrets Management

Secrets are managed through HashiCorp Vault with the following paths:
- `kv/data/app/spanishmaster/*` - Application secrets
- `database/creds/spanishmaster-app` - Database credentials
- `kv/data/redis/spanishmaster` - Redis credentials

## 📊 Monitoring

### Key Metrics
- **Application Performance**: Response times, error rates, throughput
- **Infrastructure**: CPU, memory, disk usage
- **Business Metrics**: User sessions, feature usage
- **Security**: Failed login attempts, suspicious activities

### Alerts
- Critical: Application down, database unavailable
- Warning: High resource usage, performance degradation
- Info: Deployment events, backup status

## 🔒 Security Features

### Network Security
- **Network policies** restrict pod-to-pod communication
- **TLS encryption** for all internal and external communication
- **WAF protection** against common web attacks

### Access Control
- **RBAC** with least privilege access
- **Service accounts** for workload identity
- **Admission controllers** for policy enforcement

### Data Protection
- **Encryption at rest** for databases and storage
- **Secrets rotation** automated through Vault
- **Backup encryption** for disaster recovery

## 📋 Operational Procedures

### Deployment
1. Code changes trigger CI/CD pipeline
2. Automated testing and security scanning
3. Image building and vulnerability scanning
4. Staged deployment (dev → staging → prod)
5. Health checks and rollback capabilities

### Backup & Recovery
- **Daily backups** at 2 AM UTC
- **30-day retention** for production data
- **Cross-region replication** for disaster recovery
- **Automated backup monitoring** and alerting

### Scaling
- **Horizontal Pod Autoscaler** scales based on CPU/memory
- **Vertical Pod Autoscaler** optimizes resource requests
- **Cluster Autoscaler** manages node capacity

## 🔍 Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   kubectl logs -f deployment/spanishmaster-app
   kubectl describe pod <pod-name>
   ```

2. **Database connection issues**
   ```bash
   kubectl exec -it <app-pod> -- pg_isready -h postgres-service
   ```

3. **High resource usage**
   - Check Grafana dashboards for resource metrics
   - Review HPA status: `kubectl get hpa`
   - Analyze logs for memory leaks or performance issues

### Health Checks
- Application: `https://spanishmaster.app/health`
- Prometheus: `https://monitoring.spanishmaster.app/prometheus/targets`
- Grafana: `https://monitoring.spanishmaster.app/grafana/`

## 📚 Documentation Links

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [HashiCorp Vault](https://www.vaultproject.io/docs)

## 🤝 Contributing

1. Follow infrastructure as code principles
2. All changes must go through pull requests
3. Include appropriate tests and documentation
4. Security review required for security-related changes

## 📞 Support

For infrastructure issues:
- Create an issue in the repository
- Contact the DevOps team
- Check monitoring dashboards for real-time status

---

**Infrastructure Version**: v2.0.0  
**Last Updated**: 2025-01-23  
**Maintained by**: DevOps Team