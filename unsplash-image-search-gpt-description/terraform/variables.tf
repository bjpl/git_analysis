# Variables for Terraform configuration

variable "supabase_access_token" {
  description = "Supabase access token for managing projects"
  type        = string
  sensitive   = true
}

variable "supabase_db_password" {
  description = "Database password for Supabase project"
  type        = string
  sensitive   = true
  
  validation {
    condition     = length(var.supabase_db_password) >= 8
    error_message = "Database password must be at least 8 characters long."
  }
}

variable "vercel_api_token" {
  description = "Vercel API token for deployment management"
  type        = string
  sensitive   = true
}

variable "vercel_team_id" {
  description = "Vercel team ID (optional for personal accounts)"
  type        = string
  default     = ""
}

variable "github_token" {
  description = "GitHub personal access token for repository management"
  type        = string
  sensitive   = true
}

variable "github_owner" {
  description = "GitHub repository owner/organization"
  type        = string
  default     = "your-org"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "unsplash-image-search-gpt-description"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "project_name" {
  description = "Base project name"
  type        = string
  default     = "unsplash-gpt"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "supabase_region" {
  description = "Supabase project region"
  type        = string
  default     = "us-east-1"
  
  validation {
    condition = contains([
      "us-east-1", "us-west-1", "us-west-2", 
      "eu-west-1", "eu-west-2", "eu-central-1",
      "ap-northeast-1", "ap-southeast-1", "ap-southeast-2"
    ], var.supabase_region)
    error_message = "Invalid Supabase region specified."
  }
}

variable "supabase_plan" {
  description = "Supabase plan tier"
  type        = string
  default     = "free"
  
  validation {
    condition     = contains(["free", "pro", "team"], var.supabase_plan)
    error_message = "Supabase plan must be one of: free, pro, team."
  }
}

# API Keys and External Service Configuration
variable "openai_api_key" {
  description = "OpenAI API key for AI description generation"
  type        = string
  sensitive   = true
}

variable "unsplash_access_key" {
  description = "Unsplash access key for image search"
  type        = string
  sensitive   = true
}

variable "sentry_dsn" {
  description = "Sentry DSN for error tracking"
  type        = string
  sensitive   = true
  default     = ""
}

variable "sentry_auth_token" {
  description = "Sentry auth token for release management"
  type        = string
  sensitive   = true
  default     = ""
}

variable "sentry_org" {
  description = "Sentry organization slug"
  type        = string
  default     = "unsplash-gpt"
}

variable "posthog_key" {
  description = "PostHog API key for analytics"
  type        = string
  sensitive   = true
  default     = ""
}

variable "posthog_host" {
  description = "PostHog host URL"
  type        = string
  default     = "https://app.posthog.com"
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for deployment notifications"
  type        = string
  sensitive   = true
  default     = ""
}

# Domain and SSL Configuration
variable "domain_name" {
  description = "Custom domain name for the application"
  type        = string
  default     = ""
}

variable "subdomain_prefix" {
  description = "Subdomain prefix for environment-specific URLs"
  type        = string
  default     = ""
}

variable "enable_custom_domain" {
  description = "Enable custom domain configuration"
  type        = bool
  default     = false
}

# Security Configuration
variable "enable_waf" {
  description = "Enable Web Application Firewall"
  type        = bool
  default     = true
}

variable "allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["https://localhost:3000"]
}

variable "rate_limit_requests_per_minute" {
  description = "Rate limit for API requests per minute"
  type        = number
  default     = 60
}

# Monitoring and Alerting
variable "enable_monitoring" {
  description = "Enable comprehensive monitoring setup"
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email address for alerts and notifications"
  type        = string
  default     = ""
}

variable "enable_backup" {
  description = "Enable automated database backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain database backups"
  type        = number
  default     = 30
  
  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 365
    error_message = "Backup retention must be between 1 and 365 days."
  }
}

# Feature Flags
variable "enable_analytics" {
  description = "Enable analytics tracking"
  type        = bool
  default     = true
}

variable "enable_error_tracking" {
  description = "Enable error tracking with Sentry"
  type        = bool
  default     = true
}

variable "enable_performance_monitoring" {
  description = "Enable performance monitoring"
  type        = bool
  default     = true
}

variable "enable_feature_flags" {
  description = "Enable feature flag system"
  type        = bool
  default     = false
}

# Resource Scaling Configuration
variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 10
}

variable "auto_scaling_enabled" {
  description = "Enable auto-scaling"
  type        = bool
  default     = true
}

# Database Configuration
variable "db_max_connections" {
  description = "Maximum database connections"
  type        = number
  default     = 100
}

variable "db_statement_timeout" {
  description = "Database statement timeout in milliseconds"
  type        = number
  default     = 60000
}

variable "db_idle_timeout" {
  description = "Database idle connection timeout in seconds"
  type        = number
  default     = 600
}

# Tags
variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Application = "UnsplashGPT"
    ManagedBy   = "Terraform"
    Repository  = "unsplash-image-search-gpt-description"
  }
}