# Security Guide

## 🔒 Protecting Your API Keys

This guide explains how to keep your API keys secure both locally and when deploying.

## Local Development

### Step 1: Create your .env file

Copy the example file and add your real API keys:

```bash
# In the project root
cp .env.example .env

# Also create one in the backend folder
cp backend/.env.example backend/.env
```

### Step 2: Add your API keys

Edit both `.env` files and replace the placeholder values:

```env
GROK_API_KEY=xai-your-actual-grok-api-key-here
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### Step 3: Verify .gitignore

The `.gitignore` file is already configured to prevent `.env` files from being committed to Git:

```gitignore
# Environment variables - NEVER commit these!
.env
backend/.env
*.env
!.env.example
```

### Step 4: Never commit .env files

**IMPORTANT:**
- ✅ `.env.example` files are safe to commit (they contain no real keys)
- ❌ `.env` files should NEVER be committed to Git
- ❌ Never paste your API keys in code comments or documentation

## Deploying to Streamlit Cloud

When deploying to Streamlit Cloud, you'll use Streamlit's built-in secrets management instead of `.env` files.

### Option 1: Using Streamlit Cloud Secrets (Recommended)

1. Go to https://share.streamlit.io
2. Deploy your app
3. Go to app settings → Secrets
4. Add your secrets in TOML format:

```toml
GROK_API_KEY = "xai-your-actual-key"
OPENAI_API_KEY = "sk-your-actual-key"
BACKEND_URL = "https://your-backend-url.com"
```

5. The app will automatically load these secrets

### Option 2: Local Secrets File (for testing)

Create `.streamlit/secrets.toml` locally:

```toml
GROK_API_KEY = "xai-your-actual-key"
OPENAI_API_KEY = "sk-your-actual-key"
```

This file is already in `.gitignore` and won't be committed.

## Deploying the Backend

The FastAPI backend needs to be deployed separately. Here are secure options:

### Render.com (Recommended)

1. Push your code to GitHub
2. Go to https://render.com
3. Create a new Web Service
4. Connect your repository
5. Add environment variables in the Render dashboard:
   - `GROK_API_KEY`
   - `OPENAI_API_KEY`
6. Deploy

### Railway.app

1. Go to https://railway.app
2. Create a new project from your GitHub repo
3. Add environment variables:
   - `GROK_API_KEY`
   - `OPENAI_API_KEY`
4. Deploy

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
cd backend
flyctl launch

# Set secrets
flyctl secrets set GROK_API_KEY=xai-your-key
flyctl secrets set OPENAI_API_KEY=sk-your-key

# Deploy
flyctl deploy
```

## Security Best Practices

### ✅ DO:
- Use `.env` files for local development
- Use platform secrets management for production
- Keep `.env.example` files updated (without real keys)
- Rotate API keys regularly
- Use different keys for development and production
- Monitor API usage for unusual activity

### ❌ DON'T:
- Commit `.env` files to Git
- Share API keys in screenshots or videos
- Hardcode API keys in source code
- Use production keys in development
- Share `.env` files via email or messaging apps
- Push API keys to public repositories

## Checking for Exposed Keys

Before committing, always check:

```bash
# Check what will be committed
git status

# Search for potential API keys in staged files
git diff --cached | grep -i "api_key"
git diff --cached | grep -i "xai-"
git diff --cached | grep -i "sk-"

# If you find any keys, remove them immediately!
```

## If You Accidentally Expose a Key

1. **Immediately revoke the key** on the provider's website
2. Generate a new key
3. Update your `.env` file with the new key
4. If committed to Git, you must:
   - Remove it from Git history (use `git filter-branch` or BFG Repo-Cleaner)
   - Or make the repository private and generate new keys

## Environment Variables Reference

### Required for Backend:
- `GROK_API_KEY` - Your Grok API key from x.ai
- `OPENAI_API_KEY` - Your OpenAI API key (for embeddings)

### Required for Streamlit:
- `BACKEND_URL` - URL of your FastAPI backend
- `GROK_API_KEY` - (if running all-in-one version)
- `OPENAI_API_KEY` - (if running all-in-one version)

### Optional:
- `EMBED_MODEL` - Embedding model (default: text-embedding-3-small)
- `CHAT_MODEL` - Chat model (default: grok-beta)

## Testing Your Security Setup

Run these checks to ensure your keys are secure:

```bash
# 1. Verify .env is ignored
git check-ignore .env backend/.env
# Should output: .env and backend/.env

# 2. Search for API keys in tracked files
git grep -i "xai-"
git grep -i "sk-"
# Should return nothing or only .env.example placeholders

# 3. Check what's staged for commit
git diff --cached
# Should not contain any real API keys
```

## Additional Resources

- [Streamlit Secrets Documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/best-practices-for-preventing-data-leaks-in-your-organization)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
