# Vault Policies for SpanishMaster

# Application Policy - for SpanishMaster application pods
path "spanishmaster/admin" {
  policy = "read"
}

# Database secrets
path "database/creds/spanishmaster-app" {
  capabilities = ["read"]
}

# Redis secrets
path "kv/data/redis/spanishmaster" {
  capabilities = ["read"]
}

# Application secrets
path "kv/data/app/spanishmaster/*" {
  capabilities = ["read"]
}

# JWT secrets
path "kv/data/jwt/spanishmaster" {
  capabilities = ["read"]
}

# Encryption keys
path "transit/encrypt/spanishmaster" {
  capabilities = ["update"]
}

path "transit/decrypt/spanishmaster" {
  capabilities = ["update"]
}

# PKI for TLS certificates
path "pki/issue/spanishmaster" {
  capabilities = ["update"]
}

# Monitoring Policy - for monitoring tools
path "kv/data/monitoring/*" {
  capabilities = ["read"]
}

path "database/creds/monitoring" {
  capabilities = ["read"]
}

# CI/CD Policy - for deployment pipelines
path "kv/data/cicd/spanishmaster" {
  capabilities = ["read", "list"]
}

path "aws/creds/deployment" {
  capabilities = ["read"]
}

# Admin Policy - for administrators
path "*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Developer Policy - for developers
path "kv/data/dev/spanishmaster/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "database/creds/dev" {
  capabilities = ["read"]
}

# Backup Policy - for backup systems
path "kv/data/backup/spanishmaster" {
  capabilities = ["read"]
}

path "aws/creds/backup" {
  capabilities = ["read"]
}

# Security Scanning Policy
path "kv/data/security/spanishmaster" {
  capabilities = ["read"]
}

# Specific policies for different environments

# Production Policy
path "kv/data/prod/spanishmaster/*" {
  capabilities = ["read"]
}

path "database/creds/prod-spanishmaster" {
  capabilities = ["read"]
}

# Staging Policy
path "kv/data/staging/spanishmaster/*" {
  capabilities = ["read"]
}

path "database/creds/staging-spanishmaster" {
  capabilities = ["read"]
}

# Development Policy
path "kv/data/dev/spanishmaster/*" {
  capabilities = ["read", "create", "update"]
}

path "database/creds/dev-spanishmaster" {
  capabilities = ["read"]
}

# Node.js application secrets
path "kv/data/nodejs/spanishmaster" {
  capabilities = ["read"]
}

# External API credentials
path "kv/data/external-apis/spanishmaster/*" {
  capabilities = ["read"]
}

# Logging and metrics
path "kv/data/logging/spanishmaster" {
  capabilities = ["read"]
}

# TLS certificates rotation
path "pki/root/generate/internal" {
  capabilities = ["sudo"]
}

path "pki/intermediate/generate/internal" {
  capabilities = ["sudo"]
}

# AWS dynamic secrets
path "aws/creds/spanishmaster-*" {
  capabilities = ["read"]
}

# GCP dynamic secrets (if using GCP)
path "gcp/key/spanishmaster-*" {
  capabilities = ["read"]
}

# Azure dynamic secrets (if using Azure)
path "azure/creds/spanishmaster-*" {
  capabilities = ["read"]
}

# SSH secrets for server access
path "ssh/sign/spanishmaster" {
  capabilities = ["update"]
}

# TOTP secrets for 2FA
path "totp/code/spanishmaster" {
  capabilities = ["update"]
}

# Identity secrets for authentication
path "identity/oidc/token/spanishmaster" {
  capabilities = ["read"]
}

# Kubernetes auth method
path "auth/kubernetes/role/spanishmaster" {
  capabilities = ["read"]
}

# GitHub auth method for CI/CD
path "auth/github/map/teams/spanishmaster" {
  capabilities = ["read"]
}

# LDAP auth method for enterprise
path "auth/ldap/groups/spanishmaster-*" {
  capabilities = ["read"]
}