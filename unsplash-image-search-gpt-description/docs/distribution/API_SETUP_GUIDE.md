# API Key Setup Walkthrough

This guide walks you through obtaining and configuring the API keys needed for the Unsplash Image Search with GPT application.

## Table of Contents

- [Overview](#overview)
- [Unsplash API Setup](#unsplash-api-setup)
- [OpenAI API Setup](#openai-api-setup)
- [Configuration Methods](#configuration-methods)
- [Testing Your Setup](#testing-your-setup)
- [Cost Management](#cost-management)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Overview

### Required APIs

This application requires two API keys:

1. **Unsplash API** - For searching and downloading images
   - **Cost**: Free (50 requests/hour)
   - **Purpose**: Image search and retrieval
   - **Required**: Yes

2. **OpenAI API** - For generating image descriptions
   - **Cost**: Pay-per-use (~$0.001-0.01 per description)
   - **Purpose**: AI-powered Spanish descriptions
   - **Required**: Yes

### Time Required
- **Unsplash setup**: 3-5 minutes
- **OpenAI setup**: 5-10 minutes (includes payment setup)
- **Application configuration**: 1-2 minutes
- **Total**: 10-15 minutes

## Unsplash API Setup

### Step 1: Create Unsplash Account

1. **Visit**: [unsplash.com/join](https://unsplash.com/join)
2. **Sign up** with:
   - Email and password
   - Or use Google/GitHub/Facebook login
3. **Verify** your email address (check spam folder)
4. **Complete** your profile (optional but recommended)

*[Screenshot placeholder: Unsplash registration form]*

### Step 2: Access Developer Portal

1. **Navigate** to [unsplash.com/developers](https://unsplash.com/developers)
2. **Click** "Register as a developer" (if not already registered)
3. **Accept** the API Terms of Use
4. **Fill out** the developer survey (quick)

*[Screenshot placeholder: Unsplash developer portal]*

### Step 3: Create Application

1. **Click** "New Application"
2. **Fill out the form**:
   - **Application name**: "Personal Image Learning Tool" (or similar)
   - **Description**: "Educational tool for Spanish language learning using images"
   - **Website**: Your GitHub repo URL or "N/A"
   - **Privacy Policy**: "N/A" for personal use
3. **Select** "Demo Application" (free tier)
4. **Agree** to the API Terms
5. **Click** "Create Application"

*[Screenshot placeholder: Unsplash application creation form]*

### Step 4: Get Your Access Key

1. **Find** your new application in the dashboard
2. **Copy** the "Access Key" (starts with letters and numbers)
3. **Save** this key securely - you'll need it for configuration

**Example Access Key Format**: `AbCdEf1234567890GhIjKlMnOpQrStUvWxYz`

### Step 5: Understand Usage Limits

**Free Tier (Demo Application)**:
- **Requests per hour**: 50
- **Requests per month**: 5,000
- **Rate limit reset**: Every hour

**For Higher Limits**:
- Apply for "Production" status
- Requires approval process
- Up to 5,000 requests/hour

## OpenAI API Setup

### Step 1: Create OpenAI Account

1. **Visit**: [platform.openai.com/signup](https://platform.openai.com/signup)
2. **Sign up** with:
   - Email and password
   - Or use Google/Microsoft login
3. **Verify** your email address
4. **Complete** phone number verification

*[Screenshot placeholder: OpenAI registration form]*

### Step 2: Set Up Billing

⚠️ **Important**: OpenAI requires a paid account for API access

1. **Go to**: [platform.openai.com/account/billing](https://platform.openai.com/account/billing)
2. **Click** "Set up paid account"
3. **Add payment method**:
   - Credit card or PayPal
   - Valid payment method required even if you won't use much
4. **Set usage limits** (recommended):
   - **Soft limit**: $5-10/month (notification threshold)
   - **Hard limit**: $20/month (automatic cutoff)

**Cost Estimation**:
- Each image description: ~$0.001-0.01
- 100 descriptions: ~$0.10-1.00
- Monthly casual use: $1-5

*[Screenshot placeholder: OpenAI billing setup]*

### Step 3: Create API Key

1. **Go to**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. **Click** "Create new secret key"
3. **Name your key**: "Unsplash Image Tool" (or similar)
4. **Copy the key immediately**: ⚠️ You won't be able to see it again!
5. **Store securely**: Save in a password manager or secure note

**Example API Key Format**: `sk-1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`

*[Screenshot placeholder: OpenAI API key creation]*

### Step 4: Verify Account Status

1. **Check** your account status at [platform.openai.com/account](https://platform.openai.com/account)
2. **Ensure**:
   - Payment method is active
   - Usage limits are set
   - API access is enabled

### Step 5: Choose Your Model

Recommended models for this application:

1. **gpt-4o-mini** (Default)
   - **Cost**: ~$0.001 per description
   - **Quality**: Very good for most images
   - **Speed**: Fast
   - **Best for**: Casual use, learning

2. **gpt-4o**
   - **Cost**: ~$0.01 per description (10x more)
   - **Quality**: Excellent, more detailed
   - **Speed**: Slower
   - **Best for**: Professional use, complex images

## Configuration Methods

### Method 1: Setup Wizard (Recommended)

1. **Launch** the application for the first time
2. **Setup wizard** opens automatically
3. **Enter your API keys**:
   - Paste Unsplash Access Key
   - Paste OpenAI API Key
4. **Choose settings**:
   - Default GPT model (gpt-4o-mini recommended)
   - Data storage location
   - Theme preference
5. **Click** "Test Configuration" to verify
6. **Save** when tests pass

*[Screenshot placeholder: Setup wizard interface]*

### Method 2: Environment Variables

**Windows Command Prompt**:
```cmd
set UNSPLASH_ACCESS_KEY=your_unsplash_key_here
set OPENAI_API_KEY=your_openai_key_here
set GPT_MODEL=gpt-4o-mini
```

**Windows PowerShell**:
```powershell
$env:UNSPLASH_ACCESS_KEY="your_unsplash_key_here"
$env:OPENAI_API_KEY="your_openai_key_here"
$env:GPT_MODEL="gpt-4o-mini"
```

**Linux/macOS**:
```bash
export UNSPLASH_ACCESS_KEY="your_unsplash_key_here"
export OPENAI_API_KEY="your_openai_key_here"
export GPT_MODEL="gpt-4o-mini"
```

### Method 3: Configuration File

Create `config.ini` in the application directory:

```ini
[UNSPLASH]
ACCESS_KEY=your_unsplash_access_key_here

[OPENAI]
API_KEY=your_openai_api_key_here
MODEL=gpt-4o-mini

[SETTINGS]
DATA_DIR=data
THEME=system
ZOOM_LEVEL=100
FIRST_RUN=false
```

### Method 4: .env File (Development)

Create `.env` file in the project root:

```env
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
OPENAI_API_KEY=your_openai_api_key_here
GPT_MODEL=gpt-4o-mini
```

## Testing Your Setup

### Quick Test

1. **Launch** the application
2. **Enter** "sunset" in the search box
3. **Click** "Buscar Imagen"
4. **Verify**: Image loads successfully
5. **Click** "Generar Descripción"
6. **Verify**: Spanish description appears

### Test Results

✅ **Success Indicators**:
- Images load within 5 seconds
- Descriptions generate within 30 seconds  
- No error messages appear
- Vocabulary phrases are extracted

❌ **Failure Indicators**:
- "API key not found" errors
- "Rate limit exceeded" messages
- "Authentication failed" errors
- Network timeout errors

### Validation Commands

Test your keys manually:

**Unsplash API Test**:
```bash
curl -H "Authorization: Client-ID YOUR_UNSPLASH_KEY" \
  "https://api.unsplash.com/search/photos?query=nature&per_page=1"
```

**OpenAI API Test**:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_OPENAI_KEY"
```

## Cost Management

### OpenAI Usage Monitoring

1. **Monitor usage**: [platform.openai.com/usage](https://platform.openai.com/usage)
2. **Set alerts**: Get notified at 50%, 80% of your limit
3. **Review bills**: Check monthly usage patterns
4. **Adjust limits**: Modify hard/soft limits as needed

### Cost Optimization Tips

1. **Use gpt-4o-mini**: 10x cheaper than gpt-4o
2. **Batch descriptions**: Generate multiple at once
3. **Limit sessions**: Set daily usage goals
4. **Cache results**: Application automatically caches images
5. **Monitor spending**: Check usage dashboard regularly

### Typical Usage Costs

| Usage Level | Images/Month | Estimated Cost |
|-------------|--------------|----------------|
| Light (1-2/day) | 30-60 | $0.03-0.60 |
| Moderate (5-10/day) | 150-300 | $0.15-3.00 |
| Heavy (20+/day) | 600+ | $0.60+ |

*Based on gpt-4o-mini pricing*

### Unsplash Usage Management

- **Free tier**: 50 requests/hour, 5,000/month
- **Reset time**: Every hour at minute 0
- **Monitor**: Check developer dashboard
- **Upgrade**: Apply for Production status if needed

## Troubleshooting

### Common Unsplash Issues

#### "Invalid Access Key"
- **Check**: Key copied correctly (no extra spaces)
- **Verify**: Application status is "Active"
- **Test**: Use curl command above
- **Solution**: Regenerate key if needed

#### "Rate Limit Exceeded"
- **Cause**: More than 50 requests in past hour
- **Solution**: Wait for next hour or upgrade to Production
- **Prevention**: Limit searches to 40-45 per hour

#### "Application Suspended"
- **Cause**: Terms of service violation
- **Solution**: Contact Unsplash support
- **Prevention**: Follow API guidelines

### Common OpenAI Issues

#### "Invalid API Key"
- **Check**: Key starts with "sk-" and is complete
- **Verify**: No extra characters or spaces
- **Test**: Use curl command above
- **Solution**: Create new key if corrupted

#### "Insufficient Quota"
- **Cause**: Exceeded usage limits or payment failed
- **Check**: [platform.openai.com/usage](https://platform.openai.com/usage)
- **Solution**: Add more credits or wait for monthly reset

#### "Model Not Found"
- **Cause**: Specified model not available to your account
- **Solution**: Use "gpt-4o-mini" or "gpt-4o"
- **Check**: Available models at platform.openai.com

### Configuration Issues

#### "Config File Not Found"
- **Location**: Check application directory for `config.ini`
- **Permissions**: Ensure application can read/write files
- **Solution**: Re-run setup wizard

#### "Environment Variables Not Loaded"
- **Check**: Variables set in correct terminal/session
- **Test**: `echo $UNSPLASH_ACCESS_KEY` (Linux/Mac) or `echo %UNSPLASH_ACCESS_KEY%` (Windows)
- **Solution**: Set variables in system environment

### Network Issues

#### "Connection Timeout"
- **Check**: Internet connection stability
- **Test**: Access unsplash.com and openai.com directly
- **Solution**: Check firewall/proxy settings

#### "SSL Certificate Error"
- **Cause**: Corporate firewall or outdated system
- **Solution**: Update certificates or configure proxy

## Security Best Practices

### API Key Security

1. **Never commit** API keys to version control
2. **Use environment variables** for development
3. **Store securely** in password managers
4. **Rotate regularly** (every 90 days recommended)
5. **Monitor usage** for unauthorized access

### File Permissions

```bash
# Secure config file (Linux/Mac)
chmod 600 config.ini

# Secure data directory
chmod 755 data/
```

### Access Control

- **Limit scope**: Use keys only for this application
- **Monitor logs**: Check for unusual API usage
- **Revoke immediately**: If keys are compromised
- **Use separate keys**: For development vs production

### Backup and Recovery

1. **Backup configuration**: Save config.ini securely
2. **Document keys**: Store in encrypted password manager
3. **Recovery plan**: Know how to regenerate keys quickly
4. **Test restore**: Verify backup configurations work

---

## Quick Reference

### API Key Formats
- **Unsplash**: `AbCdEf1234567890GhIjKlMnOpQrStUvWxYz` (40+ characters)
- **OpenAI**: `sk-1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ` (starts with "sk-")

### Important URLs
- **Unsplash Developer**: [unsplash.com/developers](https://unsplash.com/developers)
- **OpenAI API Keys**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **OpenAI Usage**: [platform.openai.com/usage](https://platform.openai.com/usage)
- **OpenAI Billing**: [platform.openai.com/account/billing](https://platform.openai.com/account/billing)

### Configuration Locations
- **Windows**: Application installation directory
- **macOS**: Same directory as executable
- **Linux**: Current working directory
- **Portable**: Same folder as .exe file

### Support Resources
- **Unsplash API Docs**: [unsplash.com/documentation](https://unsplash.com/documentation)
- **OpenAI API Docs**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Application Help**: Press F1 in the application
- **GitHub Issues**: [Report problems](https://github.com/your-username/unsplash-image-search-gpt-description/issues)

---

**Need Help?** If you encounter issues during setup, check our [Troubleshooting Guide](TROUBLESHOOTING.md) or create an issue on GitHub with your error messages and setup details.