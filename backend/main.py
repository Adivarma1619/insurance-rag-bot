"""
FastAPI backend for Insurance RAG Chatbot.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from rag.pdf_to_text import extract_text, SUPPORTED_EXTENSIONS
from rag.chunking import chunk_text
from rag.embed_store import build_and_save_index, load_index
from rag.rag_answer import retrieve, generate_answer

# Load environment variables from .env file
load_dotenv()


# Initialize FastAPI app
app = FastAPI(title="Insurance RAG Chatbot API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for index and chunks
faiss_index = None
text_chunks = None

# Paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PDF_PATH = os.path.join(DATA_DIR, 'knowledge.pdf')
INDEX_PATH = os.path.join(DATA_DIR, 'index.faiss')
CHUNKS_PATH = os.path.join(DATA_DIR, 'chunks.json')


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: int


class IngestResponse(BaseModel):
    status: str
    chunks_count: int


class UploadResponse(BaseModel):
    status: str
    filename: str
    message: str


class FileListResponse(BaseModel):
    files: List[str]


@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdf():
    """
    Ingest PDF, create chunks, and build FAISS index.
    This should be called once before using the chat endpoint.
    """
    try:
        # Check if PDF exists
        if not os.path.exists(PDF_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"PDF not found at {PDF_PATH}. Please run 'python rag/make_sample_pdf.py' first."
            )

        # Extract text
        print(f"Extracting text from {PDF_PATH}...")
        text = extract_text(PDF_PATH)

        # Chunk the text
        print("Chunking text...")
        chunks = chunk_text(text, chunk_tokens=450, overlap_tokens=80)
        print(f"Created {len(chunks)} chunks")

        # Build and save index
        print("Building FAISS index...")
        build_and_save_index(chunks, INDEX_PATH, CHUNKS_PATH)

        return IngestResponse(
            status="success",
            chunks_count=len(chunks)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return an answer using RAG.
    """
    global faiss_index, text_chunks

    try:
        # Load index if not already loaded
        if faiss_index is None or text_chunks is None:
            if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
                raise HTTPException(
                    status_code=400,
                    detail="Index not found. Please call /ingest endpoint first to build the index."
                )

            print("Loading index...")
            faiss_index, text_chunks = load_index(INDEX_PATH, CHUNKS_PATH)
            print(f"Loaded index with {len(text_chunks)} chunks")

        # Retrieve relevant chunks
        relevant_chunks = retrieve(
            query=request.message,
            index=faiss_index,
            chunks=text_chunks,
            k=4
        )

        # Generate answer
        answer = generate_answer(
            query=request.message,
            context_chunks=relevant_chunks
        )

        return ChatResponse(
            answer=answer,
            sources=len(relevant_chunks)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload any supported file (.pdf .txt .md .docx .csv .json .xlsx).
    """
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format '{ext}'. Allowed: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        file_path = os.path.join(DATA_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        return UploadResponse(
            status="success",
            filename=file.filename,
            message=f"Uploaded '{file.filename}'. Select it and click Build Knowledge Base."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files", response_model=FileListResponse)
async def list_files():
    """
    List every supported file currently in the data directory.
    """
    try:
        files = [
            f for f in os.listdir(DATA_DIR)
            if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
        ]
        return FileListResponse(files=sorted(files))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/use-file/{filename}", response_model=IngestResponse)
async def use_file(filename: str):
    """
    Build the FAISS index from any supported file in the data directory.
    """
    try:
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"'{filename}' not found.")

        print(f"Extracting text from {file_path}...")
        text = extract_text(file_path)

        print("Chunking text...")
        chunks = chunk_text(text, chunk_tokens=450, overlap_tokens=80)
        print(f"Created {len(chunks)} chunks")

        print("Building FAISS index...")
        build_and_save_index(chunks, INDEX_PATH, CHUNKS_PATH)

        # Reset in-memory index so next /chat reloads from disk
        global faiss_index, text_chunks
        faiss_index = None
        text_chunks = None

        return IngestResponse(status="success", chunks_count=len(chunks))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Insurance RAG Chatbot API is running",
        "endpoints": {
            "POST /upload": "Upload any supported file",
            "GET /files": "List all uploaded files",
            "POST /use-file/{filename}": "Build index from a specific file",
            "POST /ingest": "Build index from default knowledge.pdf",
            "POST /chat": "Chat with the bot"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
