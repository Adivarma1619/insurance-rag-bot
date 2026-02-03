# Quick Start Guide

Get your Insurance RAG Chatbot running in 5 minutes!

## Prerequisites

Before you begin, make sure you have:
- [ ] Python 3.8 or higher installed
- [ ] A Grok API key from https://x.ai
- [ ] An OpenAI API key from https://platform.openai.com

## Setup Steps

### 1. Install Dependencies

```bash
cd insurance-rag-bot/backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables (SECURE METHOD) 🔒

**Create your .env file:**

```bash
# Copy the example file
cp .env.example .env
```

**Edit the .env file and add your real API keys:**

```env
GROK_API_KEY=xai-your-actual-grok-key-here
OPENAI_API_KEY=sk-your-actual-openai-key-here
EMBED_MODEL=text-embedding-3-small
CHAT_MODEL=grok-beta
```

**IMPORTANT:**
- ✅ Your `.env` file is automatically protected by `.gitignore`
- ❌ NEVER commit `.env` files to Git
- ✅ Only commit `.env.example` files

### 3. Generate Sample Knowledge Base

```bash
python rag/make_sample_pdf.py
```

You should see: `Sample PDF created at: .../data/knowledge.pdf`

### 4. Start Backend Server

```bash
uvicorn main:app --reload --port 8000
```

Keep this terminal running! You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 5. Launch Streamlit (New Terminal)

```bash
# Open a new terminal
cd insurance-rag-bot
streamlit run streamlit_app.py
```

Streamlit will automatically open in your browser at `http://localhost:8501`

### 6. Build Knowledge Base

1. In the Streamlit sidebar, click **"Build Knowledge Base"**
2. Wait for completion (takes ~30 seconds)
3. You'll see a success message with the number of chunks created

### 7. Start Chatting!

Try asking:
- "How do I file a claim?"
- "What is a deductible?"
- "Can I add a driver to my policy?"

## 🔒 Security Check

Before you commit any code:

```bash
# Verify your .env file is protected
git status
# .env should NOT appear in the list

# Check .gitignore is working
git check-ignore .env backend/.env
# Should output: .env and backend/.env
```

## Troubleshooting

**"GROK_API_KEY environment variable is required"**
- Check that you created the `.env` file in the `backend/` folder
- Verify your API keys are correct (no extra spaces)
- Make sure the `.env` file is in the same directory as where you run uvicorn

**Backend not running?**
- Check terminal for errors
- Verify API keys are set in `.env`
- Make sure port 8000 is free: `lsof -i :8000` (macOS/Linux)

**Can't build knowledge base?**
- Run `python rag/make_sample_pdf.py` first
- Check that `backend/data/knowledge.pdf` exists

**API errors?**
- Verify your Grok API key is valid (starts with `xai-`)
- Verify your OpenAI API key is valid (starts with `sk-`)
- Check you have API credits on both platforms

## Alternative: Environment Variables (Less Secure)

If you prefer not to use `.env` files locally:

**macOS/Linux:**
```bash
export GROK_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

**Windows:**
```bash
set GROK_API_KEY=your-key
set OPENAI_API_KEY=your-key
```

**Note:** These must be set in every new terminal session and are less secure.

## What's Next?

- Replace `backend/data/knowledge.pdf` with your own insurance documents
- Rebuild the knowledge base in Streamlit
- Customize the UI in `streamlit_app.py`
- Read [SECURITY.md](SECURITY.md) for deployment security
- Deploy to Streamlit Cloud (see [README.md](README.md))

## File Structure

```
insurance-rag-bot/
├── .env                    # YOUR API KEYS (never commit!)
├── .env.example            # Template (safe to commit)
├── .gitignore              # Protects .env files
├── backend/
│   ├── .env                # Backend API keys (never commit!)
│   └── ...
└── ...
```

For detailed information, see:
- [README.md](README.md) - Full documentation
- [SECURITY.md](SECURITY.md) - Security best practices
