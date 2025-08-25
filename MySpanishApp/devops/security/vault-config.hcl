# HashiCorp Vault configuration for SpanishMaster

# Storage backend
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
}

# Alternative: PostgreSQL storage for production
# storage "postgresql" {
#   connection_url = "postgres://vault:password@postgres:5432/vault?sslmode=disable"
# }

# Alternative: AWS S3 storage for cloud deployments
# storage "s3" {
#   access_key    = "AKIAIOSFODNN7EXAMPLE"
#   secret_key    = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
#   bucket        = "my-vault-bucket"
#   region        = "us-east-1"
#   encrypt       = "true"
#   kms_key_id    = "alias/my-vault-key"
# }

# Listener configuration
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/tls.crt"
  tls_key_file  = "/opt/vault/tls/tls.key"
}

# Cluster configuration
cluster_name = "spanishmaster-vault"

# API address
api_addr = "https://vault.spanishmaster.app:8200"
cluster_addr = "https://vault-internal.spanishmaster.app:8201"

# UI configuration
ui = true

# Logging
log_level = "INFO"
log_format = "json"

# Disable mlock for containerized environments
disable_mlock = true

# Enable raw endpoint for health checks
raw_storage_endpoint = true

# Default lease settings
default_lease_ttl = "168h"
max_lease_ttl = "720h"

# Plugin directory
plugin_directory = "/opt/vault/plugins"

# Seal configuration (Auto-unseal with AWS KMS)
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "alias/vault-unseal-key"
}

# Telemetry
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}

# High Availability configuration
ha_storage "consul" {
  address = "consul.spanishmaster.app:8500"
  path    = "vault-ha/"
}

# Service registration
service_registration "consul" {
  address = "consul.spanishmaster.app:8500"
}