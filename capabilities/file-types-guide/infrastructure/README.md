# Infrastructure File Types Guide

## Overview
Infrastructure as Code (IaC) enables reproducible, version-controlled infrastructure management. This guide covers essential file types for cloud infrastructure and configuration management.

## File Types Reference

| **Tool Type** | **Core Files** | **Supporting Files** | **Purpose** |
|--------------|----------------|---------------------|------------|
| **Terraform** | `.tf`, `.tfvars` | `.tfstate`, `.hcl` | Cloud resource provisioning |
| **Kubernetes** | `.yaml`, `.yml` | `.json` | Container orchestration |
| **Ansible** | `.yml`, `.yaml` | `.j2`, `.ini` | Configuration management |

## Use Cases & Examples

### Terraform Infrastructure
**Best For:** Cloud resource provisioning, multi-cloud management
```hcl
# main.tf - AWS infrastructure
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state-bucket"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

# variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# vpc.tf - Network configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.environment}-public-${count.index + 1}"
    Type = "public"
  }
}

# ec2.tf - Compute resources
resource "aws_instance" "app" {
  count                  = 2
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public[count.index].id
  vpc_security_group_ids = [aws_security_group.app.id]
  
  user_data = templatefile("${path.module}/user_data.sh", {
    environment = var.environment
  })

  tags = {
    Name        = "${var.environment}-app-${count.index + 1}"
    Environment = var.environment
  }
}

# outputs.tf
output "instance_ips" {
  description = "Public IP addresses of EC2 instances"
  value       = aws_instance.app[*].public_ip
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}
```
**Example Projects:** Multi-tier applications, microservices infrastructure, data pipelines

### Kubernetes Manifests
**Best For:** Container orchestration, microservices deployment
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: app
        image: myapp:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app-service
  namespace: production
spec:
  selector:
    app: web-app
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: app-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-service
            port:
              number: 80

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  app.properties: |
    server.port=8080
    logging.level=info
    cache.ttl=3600

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: production
type: Opaque
data:
  url: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0BkYi5leGFtcGxlLmNvbS9kYm5hbWU=
```
**Example Projects:** Microservices platforms, CI/CD pipelines, cloud-native applications

### Ansible Playbooks
**Best For:** Server configuration, application deployment, orchestration
```yaml
# site.yml - Main playbook
---
- name: Configure web servers
  hosts: webservers
  become: yes
  vars_files:
    - vars/main.yml
    - vars/{{ environment }}.yml
  
  roles:
    - common
    - nginx
    - app

---
# inventory/production.ini
[webservers]
web1 ansible_host=10.0.1.10
web2 ansible_host=10.0.1.11

[dbservers]
db1 ansible_host=10.0.2.10

[all:vars]
ansible_user=ubuntu
ansible_ssh_private_key_file=~/.ssh/prod-key.pem

---
# roles/nginx/tasks/main.yml
---
- name: Install Nginx
  apt:
    name: nginx
    state: present
    update_cache: yes

- name: Copy Nginx configuration
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    backup: yes
  notify: restart nginx

- name: Create site configuration
  template:
    src: site.conf.j2
    dest: /etc/nginx/sites-available/{{ app_name }}
  notify: reload nginx

- name: Enable site
  file:
    src: /etc/nginx/sites-available/{{ app_name }}
    dest: /etc/nginx/sites-enabled/{{ app_name }}
    state: link
  notify: reload nginx

- name: Ensure Nginx is running
  systemd:
    name: nginx
    state: started
    enabled: yes

---
# roles/nginx/templates/site.conf.j2
server {
    listen 80;
    server_name {{ server_name }};

    location / {
        proxy_pass http://localhost:{{ app_port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias {{ app_static_path }};
        expires 30d;
    }
}

---
# roles/app/tasks/main.yml
---
- name: Create app user
  user:
    name: {{ app_user }}
    shell: /bin/bash
    home: /home/{{ app_user }}

- name: Clone application repository
  git:
    repo: {{ app_repo }}
    dest: {{ app_path }}
    version: {{ app_version }}
  become_user: {{ app_user }}

- name: Install dependencies
  pip:
    requirements: {{ app_path }}/requirements.txt
    virtualenv: {{ app_path }}/venv
  become_user: {{ app_user }}

- name: Copy environment file
  template:
    src: env.j2
    dest: {{ app_path }}/.env
    owner: {{ app_user }}
    mode: '0600'

- name: Run database migrations
  command: {{ app_path }}/venv/bin/python manage.py migrate
  args:
    chdir: {{ app_path }}
  become_user: {{ app_user }}

- name: Create systemd service
  template:
    src: app.service.j2
    dest: /etc/systemd/system/{{ app_name }}.service
  notify: restart app
```
**Example Projects:** Server provisioning, application deployment, configuration management

## Best Practices

1. **State Management:** Use remote state backends for Terraform
2. **Secrets Management:** Never commit secrets, use vault solutions
3. **Modularity:** Create reusable modules and roles
4. **Testing:** Test infrastructure changes in staging first
5. **Documentation:** Document infrastructure architecture
6. **Version Pinning:** Pin provider and module versions

## File Organization Pattern
```
infrastructure/
├── terraform/
│   ├── modules/
│   │   ├── vpc/
│   │   └── eks/
│   ├── environments/
│   │   ├── dev/
│   │   └── prod/
│   └── global/
├── kubernetes/
│   ├── base/
│   ├── overlays/
│   │   ├── dev/
│   │   └── prod/
│   └── helm/
└── ansible/
    ├── playbooks/
    ├── roles/
    ├── inventory/
    └── group_vars/
```

## Infrastructure Patterns

### Blue-Green Deployment
```hcl
# Terraform blue-green deployment
resource "aws_lb_target_group" "blue" {
  name     = "app-blue"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_target_group" "green" {
  name     = "app-green"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_listener_rule" "main" {
  listener_arn = aws_lb_listener.main.arn
  
  action {
    type             = "forward"
    target_group_arn = var.active_environment == "blue" ? 
                       aws_lb_target_group.blue.arn : 
                       aws_lb_target_group.green.arn
  }
}
```

### GitOps Workflow
```yaml
# ArgoCD application manifest
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: production-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/k8s-manifests
    targetRevision: HEAD
    path: overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Performance Considerations
- Use terraform plan to preview changes
- Implement resource tagging strategies
- Monitor infrastructure costs
- Use auto-scaling for dynamic workloads
- Implement proper backup strategies

## Infrastructure Tools
- **IaC:** Terraform, Pulumi, CloudFormation, ARM Templates
- **Kubernetes:** kubectl, Helm, Kustomize, ArgoCD
- **Configuration:** Ansible, Chef, Puppet, SaltStack
- **Monitoring:** Prometheus, Grafana, Datadog, New Relic
- **Security:** Vault, Secrets Manager, Key Vault