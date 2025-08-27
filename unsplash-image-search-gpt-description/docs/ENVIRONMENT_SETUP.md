# Environment Setup Guide

## Overview
This guide explains how to configure environment variables for the VocabLens PWA project securely.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Get your API keys:**
   - **Unsplash API:** Visit [Unsplash Developers](https://unsplash.com/developers) and create an application
   - **OpenAI API:** Visit [OpenAI Platform](https://platform.openai.com/api-keys) and generate an API key
   - **Supabase:** Visit [Supabase Dashboard](https://supabase.com/dashboard) and get your project URL and anon key

3. **Fill in your API keys in the `.env` file**

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_UNSPLASH_ACCESS_KEY` | Your Unsplash API access key | `abc123def456...` |
| `VITE_OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-...` |
| `VITE_SUPABASE_URL` | Your Supabase project URL | `https://xyz.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anonymous key | `eyJ...` |

### Optional Configuration Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_DEFAULT_AI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use |
| `VITE_MAX_IMAGES_PER_SEARCH` | `30` | Maximum images per search |
| `VITE_DEFAULT_DAILY_GOAL` | `10` | Default vocabulary learning goal |
| `VITE_API_RATE_LIMIT_PER_MINUTE` | `60` | API rate limit |
| `VITE_ENABLE_PWA` | `true` | Enable PWA features |
| `VITE_ENABLE_OFFLINE_MODE` | `true` | Enable offline functionality |

## Security Best Practices

### ✅ Do:
- Keep your `.env` file local and never commit it
- Use different API keys for development and production
- Regularly rotate your API keys
- Monitor your API usage

### ❌ Don't:
- Share API keys in chat, email, or code
- Use production keys in development
- Commit `.env` files to version control
- Use weak or predictable keys

## Validation

The application automatically validates your API keys on startup:

1. **Unsplash keys** are checked for proper format (43+ characters, alphanumeric)
2. **OpenAI keys** must start with `sk-` and be properly formatted
3. **Supabase URLs** must be valid HTTPS URLs

## Testing Your Configuration

Run this command to test your API configuration:
```bash
npm run test:config
```

## Troubleshooting

### Common Issues

1. **Invalid API Key Format**
   - Ensure keys are copied completely without spaces
   - Check for proper prefixes (`sk-` for OpenAI)

2. **CORS Errors**
   - Verify your domain is allowlisted in API dashboards
   - Check API key permissions

3. **Rate Limiting**
   - Monitor your API usage in respective dashboards
   - Adjust rate limit settings if needed

### Getting Help

- Check the [API Integration Guide](./API_INTEGRATION_SPECIFICATIONS.md)
- Review [Troubleshooting Guide](./docs/troubleshooting.md)
- Contact support through respective API provider channels

## Production Deployment

For production deployment:

1. Use environment-specific API keys
2. Set up proper secrets management
3. Enable security headers
4. Monitor API usage and costs

See [Production Deployment Guide](./PRODUCTION_DEPLOYMENT_GUIDE.md) for detailed instructions.