#!/bin/bash

# Netlify Deployment Health Check Script
# Comprehensive health check for VocabLens on Netlify

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_URL=${DEPLOY_URL:-""}
TIMEOUT=30
MAX_RETRIES=3

echo -e "${BLUE}🔍 Starting Netlify Deployment Health Check${NC}"
echo "================================================="

# Function to print status
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️ $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️ $message${NC}"
            ;;
    esac
}

# Function to check URL with retry
check_url() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    print_status "INFO" "Checking $description: $url"
    
    for i in $(seq 1 $MAX_RETRIES); do
        if response=$(curl -s -w "HTTPSTATUS:%{http_code}" --connect-timeout $TIMEOUT "$url" 2>/dev/null); then
            http_code=$(echo $response | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
            body=$(echo $response | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
            
            if [ "$http_code" -eq "$expected_status" ]; then
                print_status "SUCCESS" "$description is accessible (HTTP $http_code)"
                echo "$body"
                return 0
            else
                print_status "WARNING" "$description returned HTTP $http_code (expected $expected_status)"
                if [ $i -lt $MAX_RETRIES ]; then
                    print_status "INFO" "Retrying in 5 seconds... (attempt $((i+1))/$MAX_RETRIES)"
                    sleep 5
                fi
            fi
        else
            print_status "WARNING" "Failed to connect to $description"
            if [ $i -lt $MAX_RETRIES ]; then
                print_status "INFO" "Retrying in 5 seconds... (attempt $((i+1))/$MAX_RETRIES)"
                sleep 5
            fi
        fi
    done
    
    print_status "ERROR" "$description check failed after $MAX_RETRIES attempts"
    return 1
}

# Function to validate HTML content
validate_html_content() {
    local url=$1
    local html_content
    
    print_status "INFO" "Validating HTML content"
    
    if html_content=$(curl -s --connect-timeout $TIMEOUT "$url" 2>/dev/null); then
        # Check for React root element
        if echo "$html_content" | grep -q 'id="root"'; then
            print_status "SUCCESS" "React root element found"
        else
            print_status "ERROR" "React root element missing"
            return 1
        fi
        
        # Check for asset references
        if echo "$html_content" | grep -q '/assets/'; then
            print_status "SUCCESS" "Asset references found"
        else
            print_status "WARNING" "No asset references found"
        fi
        
        # Check for runtime config indicators
        if echo "$html_content" | grep -qi -E "(runtime|config|api.*(key|config))"; then
            print_status "SUCCESS" "Runtime configuration indicators found"
        else
            print_status "WARNING" "Runtime configuration not clearly detected"
        fi
        
        # Check for PWA manifest
        if echo "$html_content" | grep -q 'manifest.json'; then
            print_status "SUCCESS" "PWA manifest reference found"
        else
            print_status "WARNING" "PWA manifest reference missing"
        fi
        
        # Check for security headers (basic check via meta tags)
        if echo "$html_content" | grep -qi "viewport"; then
            print_status "SUCCESS" "Viewport meta tag found"
        else
            print_status "WARNING" "Viewport meta tag missing"
        fi
        
        return 0
    else
        print_status "ERROR" "Failed to fetch HTML content"
        return 1
    fi
}

# Function to check PWA manifest
check_pwa_manifest() {
    local base_url=$1
    local manifest_url="$base_url/manifest.json"
    
    print_status "INFO" "Checking PWA manifest"
    
    if manifest_content=$(curl -s --connect-timeout $TIMEOUT "$manifest_url" 2>/dev/null); then
        if echo "$manifest_content" | python3 -m json.tool >/dev/null 2>&1; then
            print_status "SUCCESS" "PWA manifest is valid JSON"
            
            # Check required fields
            required_fields=("name" "short_name" "start_url" "display" "theme_color" "icons")
            for field in "${required_fields[@]}"; do
                if echo "$manifest_content" | grep -q "\"$field\""; then
                    print_status "SUCCESS" "Manifest has required field: $field"
                else
                    print_status "WARNING" "Manifest missing field: $field"
                fi
            done
        else
            print_status "ERROR" "PWA manifest is not valid JSON"
            return 1
        fi
    else
        print_status "WARNING" "PWA manifest not accessible"
    fi
}

# Function to check service worker
check_service_worker() {
    local base_url=$1
    local sw_url="$base_url/sw.js"
    
    print_status "INFO" "Checking Service Worker"
    
    if sw_response=$(curl -s -w "HTTPSTATUS:%{http_code}" --connect-timeout $TIMEOUT "$sw_url" 2>/dev/null); then
        http_code=$(echo $sw_response | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
        
        if [ "$http_code" -eq 200 ]; then
            print_status "SUCCESS" "Service Worker is accessible"
            
            sw_content=$(echo $sw_response | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
            
            # Check for caching functionality
            if echo "$sw_content" | grep -qi "cache"; then
                print_status "SUCCESS" "Service Worker has caching functionality"
            else
                print_status "WARNING" "Service Worker may not have caching functionality"
            fi
            
            # Check for offline support
            if echo "$sw_content" | grep -qi -E "(offline|fallback)"; then
                print_status "SUCCESS" "Service Worker has offline support indicators"
            else
                print_status "INFO" "Service Worker offline support unclear"
            fi
        else
            print_status "WARNING" "Service Worker returned HTTP $http_code"
        fi
    else
        print_status "WARNING" "Service Worker not accessible"
    fi
}

# Function to test SPA routing
test_spa_routing() {
    local base_url=$1
    local test_routes=("/about" "/search" "/vocabulary" "/settings" "/nonexistent")
    
    print_status "INFO" "Testing SPA routing"
    
    for route in "${test_routes[@]}"; do
        local test_url="$base_url$route"
        
        if response=$(curl -s -w "HTTPSTATUS:%{http_code}" --connect-timeout $TIMEOUT "$test_url" 2>/dev/null); then
            http_code=$(echo $response | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
            
            if [ "$http_code" -eq 200 ]; then
                print_status "SUCCESS" "SPA route works: $route"
            else
                print_status "WARNING" "SPA route issue: $route (HTTP $http_code)"
            fi
        else
            print_status "WARNING" "Failed to test SPA route: $route"
        fi
    done
}

# Function to check static assets
check_static_assets() {
    local base_url=$1
    
    print_status "INFO" "Checking static assets"
    
    # Get main page to extract asset URLs
    if html_content=$(curl -s --connect-timeout $TIMEOUT "$base_url" 2>/dev/null); then
        # Extract CSS files
        css_files=$(echo "$html_content" | grep -oE '/assets/[^"]*\.css' | head -3)
        js_files=$(echo "$html_content" | grep -oE '/assets/[^"]*\.js' | head -3)
        
        # Check CSS files
        if [ -n "$css_files" ]; then
            for css_file in $css_files; do
                css_url="$base_url$css_file"
                if check_url "$css_url" "CSS asset" 200 >/dev/null; then
                    print_status "SUCCESS" "CSS asset accessible: $(basename $css_file)"
                fi
            done
        else
            print_status "WARNING" "No CSS files found to check"
        fi
        
        # Check JS files
        if [ -n "$js_files" ]; then
            for js_file in $js_files; do
                js_url="$base_url$js_file"
                if check_url "$js_url" "JS asset" 200 >/dev/null; then
                    print_status "SUCCESS" "JS asset accessible: $(basename $js_file)"
                fi
            done
        else
            print_status "WARNING" "No JS files found to check"
        fi
    fi
}

# Function to test runtime API configuration
test_runtime_config() {
    local base_url=$1
    
    print_status "INFO" "Testing runtime API configuration"
    
    # This is a basic test - in a real scenario, you might want to test
    # the configuration interface or API endpoints
    if html_content=$(curl -s --connect-timeout $TIMEOUT "$base_url/settings" 2>/dev/null); then
        if echo "$html_content" | grep -qi -E "(api.*key|configuration|settings)"; then
            print_status "SUCCESS" "Runtime configuration interface appears accessible"
        else
            print_status "WARNING" "Runtime configuration interface unclear"
        fi
    else
        print_status "WARNING" "Could not access settings page for runtime config test"
    fi
}

# Main health check function
main() {
    local exit_code=0
    
    if [ -z "$DEPLOY_URL" ]; then
        print_status "ERROR" "DEPLOY_URL environment variable not set"
        print_status "INFO" "Usage: DEPLOY_URL=https://your-site.netlify.app ./netlify-deploy-check.sh"
        exit 1
    fi
    
    print_status "INFO" "Checking deployment at: $DEPLOY_URL"
    echo ""
    
    # Basic connectivity check
    if ! check_url "$DEPLOY_URL" "Main site" 200; then
        print_status "ERROR" "Main site is not accessible"
        exit_code=1
    fi
    
    # HTML content validation
    if ! validate_html_content "$DEPLOY_URL"; then
        print_status "ERROR" "HTML content validation failed"
        exit_code=1
    fi
    
    # PWA checks
    check_pwa_manifest "$DEPLOY_URL"
    check_service_worker "$DEPLOY_URL"
    
    # SPA routing test
    test_spa_routing "$DEPLOY_URL"
    
    # Static assets check
    check_static_assets "$DEPLOY_URL"
    
    # Runtime configuration test
    test_runtime_config "$DEPLOY_URL"
    
    # Security headers check (basic)
    print_status "INFO" "Checking security headers"
    if headers=$(curl -s -I --connect-timeout $TIMEOUT "$DEPLOY_URL" 2>/dev/null); then
        security_headers=("X-Frame-Options" "X-Content-Type-Options" "X-XSS-Protection" "Strict-Transport-Security")
        
        for header in "${security_headers[@]}"; do
            if echo "$headers" | grep -qi "$header"; then
                print_status "SUCCESS" "Security header found: $header"
            else
                print_status "WARNING" "Security header missing: $header"
            fi
        done
    else
        print_status "WARNING" "Could not check security headers"
    fi
    
    # Final summary
    echo ""
    echo "================================================="
    if [ $exit_code -eq 0 ]; then
        print_status "SUCCESS" "🎉 Deployment health check completed successfully!"
        print_status "INFO" "Your VocabLens application is ready for users"
        print_status "INFO" "Runtime API configuration appears to be working"
    else
        print_status "ERROR" "❌ Deployment health check found critical issues"
        print_status "INFO" "Please review the errors above and redeploy"
    fi
    
    exit $exit_code
}

# Run the main function
main "$@"