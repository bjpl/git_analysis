# Terraform configuration for Supabase infrastructure
# This manages Supabase projects, databases, and related resources

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
    }
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 5.0"
    }
  }
  
  backend "remote" {
    organization = "unsplash-gpt"
    workspaces {
      name = "production"
    }
  }
}

# Configure providers
provider "supabase" {
  access_token = var.supabase_access_token
}

provider "vercel" {
  api_token = var.vercel_api_token
  team      = var.vercel_team_id
}

provider "github" {
  token = var.github_token
  owner = var.github_owner
}

# Variables
variable "supabase_access_token" {
  description = "Supabase access token for API access"
  type        = string
  sensitive   = true
}

variable "vercel_api_token" {
  description = "Vercel API token"
  type        = string
  sensitive   = true
}

variable "vercel_team_id" {
  description = "Vercel team ID"
  type        = string
}

variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "your-org"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "unsplash_access_key" {
  description = "Unsplash access key"
  type        = string
  sensitive   = true
}

# Local values
locals {
  project_name = "unsplash-gpt-${var.environment}"
  common_tags = {
    Project     = "UnsplashGPT"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Supabase Organization
data "supabase_organization" "main" {
  name = "UnsplashGPT"
}

# Supabase Project
resource "supabase_project" "main" {
  organization_id = data.supabase_organization.main.id
  name           = local.project_name
  database_password = var.supabase_db_password
  region         = "us-east-1"
  
  # Performance tier
  plan = var.environment == "production" ? "pro" : "free"
  
  tags = local.common_tags
}

# Database configuration
resource "supabase_settings" "main" {
  project_ref = supabase_project.main.id
  
  # Auth settings
  auth = {
    enable_signup                = true
    jwt_expiry                  = 3600
    refresh_token_rotation_enabled = true
    security_update_password_require_reauthentication = true
    
    # External providers
    external = {
      google_enabled = true
      github_enabled = true
    }
  }
  
  # API settings
  api = {
    db_schema            = "public,graphql_public"
    db_extra_search_path = "public,extensions"
    max_rows            = 1000
  }
  
  # Storage settings
  storage = {
    file_size_limit = "50MB"
    upload_file_size_limit = "50MB"
  }
}

# Storage buckets
resource "supabase_bucket" "avatars" {
  project_ref = supabase_project.main.id
  name        = "avatars"
  public      = false
  file_size_limit = "2MB"
  allowed_mime_types = ["image/jpeg", "image/png", "image/webp"]
}

resource "supabase_bucket" "vocabulary_images" {
  project_ref = supabase_project.main.id
  name        = "vocabulary-images"
  public      = true
  file_size_limit = "10MB"
  allowed_mime_types = ["image/jpeg", "image/png", "image/webp"]
}

resource "supabase_bucket" "user_exports" {
  project_ref = supabase_project.main.id
  name        = "user-exports"
  public      = false
  file_size_limit = "50MB"
  allowed_mime_types = ["text/csv", "application/json", "text/plain"]
}

# Edge Functions
resource "supabase_function" "image_search" {
  project_ref = supabase_project.main.id
  name        = "image-search"
  source      = "../supabase/functions/image-search"
  
  # Environment variables
  secrets = {
    UNSPLASH_ACCESS_KEY = var.unsplash_access_key
  }
  
  # Function configuration
  verify_jwt = true
  
  # Import map
  import_map_path = "../supabase/functions/import_map.json"
}

resource "supabase_function" "ai_description" {
  project_ref = supabase_project.main.id
  name        = "ai-description"
  source      = "../supabase/functions/ai-description"
  
  secrets = {
    OPENAI_API_KEY = var.openai_api_key
  }
  
  verify_jwt = true
  import_map_path = "../supabase/functions/import_map.json"
}

resource "supabase_function" "translation" {
  project_ref = supabase_project.main.id
  name        = "translation"
  source      = "../supabase/functions/translation"
  
  secrets = {
    OPENAI_API_KEY = var.openai_api_key
  }
  
  verify_jwt = true
  import_map_path = "../supabase/functions/import_map.json"
}

resource "supabase_function" "vocabulary_extract" {
  project_ref = supabase_project.main.id
  name        = "vocabulary-extract"
  source      = "../supabase/functions/vocabulary-extract"
  
  secrets = {
    OPENAI_API_KEY = var.openai_api_key
  }
  
  verify_jwt = true
  import_map_path = "../supabase/functions/import_map.json"
}

# Vercel Project Configuration
resource "vercel_project" "main" {
  name             = local.project_name
  framework        = "nextjs"
  root_directory   = ""
  build_command    = "npm run build"
  output_directory = ".next"
  install_command  = "npm ci"
  
  # Git repository
  git_repository = {
    type = "github"
    repo = "${var.github_owner}/unsplash-image-search-gpt-description"
  }
  
  # Environment variables
  environment = [
    {
      key    = "NEXT_PUBLIC_SUPABASE_URL"
      value  = supabase_project.main.api_url
      target = ["production", "preview", "development"]
    },
    {
      key    = "NEXT_PUBLIC_SUPABASE_ANON_KEY"
      value  = supabase_project.main.anon_key
      target = ["production", "preview", "development"]
    },
    {
      key    = "SUPABASE_SERVICE_ROLE_KEY"
      value  = supabase_project.main.service_role_key
      target = ["production"]
      type   = "secret"
    },
    {
      key    = "NEXT_PUBLIC_APP_ENV"
      value  = var.environment
      target = ["production", "preview", "development"]
    }
  ]
  
  # Domains
  domains = var.environment == "production" ? [
    "unsplash-gpt.com",
    "www.unsplash-gpt.com"
  ] : []
}

# GitHub Repository Secrets
resource "github_actions_secret" "supabase_url" {
  repository      = "unsplash-image-search-gpt-description"
  secret_name     = "SUPABASE_URL"
  plaintext_value = supabase_project.main.api_url
}

resource "github_actions_secret" "supabase_anon_key" {
  repository      = "unsplash-image-search-gpt-description"
  secret_name     = "SUPABASE_ANON_KEY"
  plaintext_value = supabase_project.main.anon_key
}

resource "github_actions_secret" "supabase_service_key" {
  repository      = "unsplash-image-search-gpt-description"
  secret_name     = "SUPABASE_SERVICE_ROLE_KEY"
  plaintext_value = supabase_project.main.service_role_key
}

resource "github_actions_secret" "supabase_project_id" {
  repository      = "unsplash-image-search-gpt-description"
  secret_name     = "SUPABASE_PROJECT_ID"
  plaintext_value = supabase_project.main.id
}

resource "github_actions_secret" "vercel_token" {
  repository      = "unsplash-image-search-gpt-description"
  secret_name     = "VERCEL_TOKEN"
  plaintext_value = var.vercel_api_token
}

resource "github_actions_secret" "vercel_org_id" {
  repository      = "unsplash-image-search-gpt-description"
  secret_name     = "VERCEL_ORG_ID"
  plaintext_value = var.vercel_team_id
}

resource "github_actions_secret" "vercel_project_id" {
  repository      = "unsplash-image-search-gpt-description"
  secret_name     = "VERCEL_PROJECT_ID"
  plaintext_value = vercel_project.main.id
}

# Outputs
output "supabase_project_url" {
  description = "Supabase project URL"
  value       = supabase_project.main.api_url
}

output "supabase_project_id" {
  description = "Supabase project ID"
  value       = supabase_project.main.id
}

output "supabase_anon_key" {
  description = "Supabase anonymous key"
  value       = supabase_project.main.anon_key
  sensitive   = true
}

output "vercel_project_url" {
  description = "Vercel project URL"
  value       = vercel_project.main.project_domain_name
}

output "vercel_project_id" {
  description = "Vercel project ID"
  value       = vercel_project.main.id
}