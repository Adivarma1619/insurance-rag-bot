# Insurance RAG Chatbot with Grok AI & Streamlit

A complete Retrieval-Augmented Generation (RAG) chatbot system for an insurance agency, featuring:
- FastAPI backend with FAISS vector search
- Grok AI for chat completions
- OpenAI for text embeddings
- Streamlit web interface

## Project Structure

```
insurance-rag-bot/
├── streamlit_app.py           # Streamlit web interface
├── README.md                   # This file
├── backend/
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── pdf_to_text.py    # PDF text extraction
│   │   ├── chunking.py       # Text chunking with overlap
│   │   ├── embed_store.py    # Embeddings and FAISS indexing
│   │   ├── rag_answer.py     # Retrieval and answer generation with Grok
│   │   └── make_sample_pdf.py # Sample PDF generator
│   └── data/                  # Generated files (PDF, index, chunks)
└── frontend/                  # React frontend (optional - replaced by Streamlit)
```

## Features

- **RAG Pipeline**: Token-based chunking, OpenAI embeddings, FAISS vector search
- **Grok AI Integration**: Uses xAI's Grok for intelligent chat responses
- **FastAPI Backend**: RESTful API with CORS support
- **Streamlit Interface**: Modern, user-friendly web interface
- **Sample Data**: Auto-generated insurance FAQ PDF for testing
- **Configurable Models**: Supports custom embedding and chat models

## Prerequisites

- Python 3.8+
- Grok API key (from https://x.ai)
- OpenAI API key (for embeddings only)

## Setup Instructions

### 1. Navigate to backend directory

```bash
cd insurance-rag-bot/backend
```

### 2. Create and activate virtual environment

**On macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set API keys

**On macOS/Linux:**
```bash
export GROK_API_KEY="your-grok-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
```

**On Windows:**
```bash
set GROK_API_KEY=your-grok-api-key-here
set OPENAI_API_KEY=your-openai-api-key-here
```

**Note:**
- `GROK_API_KEY` is used for chat completions (answering questions)
- `OPENAI_API_KEY` is used for text embeddings (since Grok doesn't support embeddings yet)

### 5. Generate sample PDF

```bash
python rag/make_sample_pdf.py
```

This creates `data/knowledge.pdf` with sample insurance FAQs.

### 6. Start the backend server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Running the Streamlit App

### Option 1: From the project root

In a new terminal (keep backend running):

```bash
cd insurance-rag-bot
streamlit run streamlit_app.py
```

### Option 2: Set environment variables if needed

If your backend is running on a different port:

**On macOS/Linux:**
```bash
export BACKEND_URL="http://localhost:8000"
streamlit run streamlit_app.py
```

**On Windows:**
```bash
set BACKEND_URL=http://localhost:8000
streamlit run streamlit_app.py
```

The Streamlit app will open automatically in your browser (usually at `http://localhost:8501`)

## Using the Application

### First Time Setup

1. Start the backend server (see step 6 above)
2. Launch the Streamlit app
3. Click **"Build Knowledge Base"** in the sidebar
4. Wait for the indexing to complete (you'll see a success message)
5. Start chatting!

### Asking Questions

Example questions you can ask:
- "How do I file a claim?"
- "What is a deductible?"
- "Can I add another driver to my policy?"
- "What documents do I need for a claim?"
- "How long does claim processing take?"
- "What does homeowners insurance cover?"
- "Are natural disasters covered?"
- "How can I lower my premium?"

### Rebuilding the Knowledge Base

If you update the PDF or want to rebuild the index:
1. Click **"Rebuild Knowledge Base"** in the sidebar
2. Wait for completion

### Clearing Chat History

Click **"Clear Chat History"** in the sidebar to start a new conversation.

## API Endpoints (Backend)

### `GET /`
Health check endpoint.

### `POST /ingest`
Ingests the PDF, creates chunks, and builds the FAISS index.

**Response:**
```json
{
  "status": "success",
  "chunks_count": 15
}
```

### `POST /chat`
Processes a chat message and returns an AI-generated answer.

**Request:**
```json
{
  "message": "How do I file a claim?"
}
```

**Response:**
```json
{
  "answer": "To file a claim, you can call our 24/7 claims hotline...",
  "sources": 4
}
```

## Configuration

### Environment Variables

**Required:**
- `GROK_API_KEY`: Your Grok API key from x.ai
- `OPENAI_API_KEY`: Your OpenAI API key (for embeddings)

**Optional:**
- `BACKEND_URL`: Backend URL for Streamlit app (default: `http://localhost:8000`)
- `EMBED_MODEL`: Embedding model (default: `text-embedding-3-small`)
- `CHAT_MODEL`: Chat model (default: `grok-beta`)

### Chunking Parameters

Edit [backend/rag/chunking.py](backend/rag/chunking.py):
- `chunk_tokens`: Size of each chunk (default: 450)
- `overlap_tokens`: Overlap between chunks (default: 80)

### Retrieval Parameters

Edit [backend/rag/rag_answer.py](backend/rag/rag_answer.py):
- `k`: Number of chunks to retrieve (default: 4)

## How It Works

### RAG Pipeline

1. **PDF Ingestion**: PDF → Text extraction → Token-based chunking
2. **Indexing**: Text chunks → OpenAI embeddings → FAISS index
3. **Retrieval**: User query → Embedding → FAISS similarity search → Top-k chunks
4. **Generation**: Query + Context → Grok AI Chat Completion → Answer

### Architecture

```
User Input (Streamlit)
    ↓
FastAPI Backend
    ↓
1. Query Embedding (OpenAI)
    ↓
2. FAISS Search (Find relevant chunks)
    ↓
3. Context + Query → Grok AI
    ↓
4. Generated Answer
    ↓
Streamlit Display
```

## Technology Stack

**Backend:**
- FastAPI - Modern web framework
- OpenAI API - Text embeddings
- Grok API (xAI) - Chat completions
- FAISS - Vector similarity search
- tiktoken - Token counting
- pypdf - PDF text extraction
- reportlab - PDF generation

**Frontend:**
- Streamlit - Web interface
- Requests - HTTP client

## Deploying to Streamlit Cloud

### Step 1: Prepare your repository

1. Push your code to GitHub
2. Make sure `streamlit_app.py` is in the root directory
3. Create a `.streamlit/secrets.toml` file (don't commit this):

```toml
GROK_API_KEY = "your-grok-api-key"
OPENAI_API_KEY = "your-openai-api-key"
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file to `streamlit_app.py`
6. Click "Advanced settings"
7. Add your secrets:
   - `GROK_API_KEY`
   - `OPENAI_API_KEY`
8. Click "Deploy"

**Note:** For Streamlit Cloud deployment, you'll need to modify the app to run the backend within the same process or deploy the backend separately (e.g., on Render, Railway, or Fly.io).

### Alternative: All-in-One Streamlit Deployment

For a simpler deployment that doesn't require a separate backend, consider moving the RAG logic directly into the Streamlit app. This would eliminate the need for the FastAPI backend.

## Troubleshooting

### "Backend is not running" error
- Make sure you started the backend server: `uvicorn main:app --reload --port 8000`
- Check that it's running on port 8000
- Verify no firewall is blocking the connection

### "Knowledge base not loaded" warning
- Click "Build Knowledge Base" in the sidebar
- This must be done once before chatting

### "PDF not found" error
- Run `python rag/make_sample_pdf.py` from the backend directory
- Check that `backend/data/knowledge.pdf` exists

### API Key errors
- Verify `GROK_API_KEY` is set correctly
- Verify `OPENAI_API_KEY` is set correctly
- Check that your API keys have sufficient credits
- Ensure you have access to the models being used

### CORS errors
- Ensure the backend CORS settings allow your frontend origin
- Default is `http://localhost:5173` (for React) - not needed for Streamlit

### Slow responses
- Grok API responses may take a few seconds
- Large PDFs will take longer to index
- Consider reducing `k` (number of retrieved chunks) for faster responses

## Customizing Your Knowledge Base

### Using Your Own PDF

1. Replace `backend/data/knowledge.pdf` with your own PDF
2. Rebuild the knowledge base via the Streamlit sidebar
3. Start asking questions about your content

### Multiple PDFs

To support multiple PDFs, modify:
1. `backend/rag/pdf_to_text.py` - to read multiple files
2. `backend/main.py` - to process all PDFs in the data folder

## Cost Optimization

- **Embeddings**: OpenAI charges per token for embeddings. Larger chunks = fewer chunks = lower cost
- **Chat**: Grok API pricing varies. Shorter contexts = lower cost per request
- **Caching**: The FAISS index is cached, so you only pay for embeddings once during ingestion

## License

This is a demo project for educational purposes.

## Getting Your API Keys

### Grok API Key
1. Go to https://x.ai
2. Sign up for an account
3. Navigate to API settings
4. Create a new API key

### OpenAI API Key
1. Go to https://platform.openai.com
2. Sign up or log in
3. Navigate to API keys section
4. Create a new API key

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the code comments
- Ensure all dependencies are installed correctly
- Verify API keys are valid and have credits

## Next Steps

- Add more documents to your knowledge base
- Customize the Streamlit UI
- Add conversation memory
- Implement user authentication
- Add analytics and logging
- Deploy to production
