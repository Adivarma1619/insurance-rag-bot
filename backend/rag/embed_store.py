"""
Embedding and vector storage using Grok/OpenAI and FAISS.
"""
import os
import json
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Convert list of texts to normalized embedding vectors.
    Uses OpenAI for embeddings as Grok doesn't support embeddings yet.

    Args:
        texts: List of text strings to embed

    Returns:
        Normalized numpy array of shape (len(texts), embedding_dim)
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required for embeddings")

    client = OpenAI(api_key=openai_api_key)

    # Get embeddings from OpenAI
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )

    # Extract embeddings and convert to numpy array
    embeddings = [item.embedding for item in response.data]
    embeddings_array = np.array(embeddings, dtype=np.float32)

    # Normalize for cosine similarity using FAISS
    faiss.normalize_L2(embeddings_array)

    return embeddings_array


def build_and_save_index(chunks: list[str], index_path: str, chunks_path: str):
    """
    Build FAISS index from text chunks and save to disk.

    Args:
        chunks: List of text chunks
        index_path: Path to save FAISS index
        chunks_path: Path to save chunks metadata JSON
    """
    # Generate embeddings
    embeddings = embed_texts(chunks)

    # Create FAISS index (Inner Product for normalized vectors = cosine similarity)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)

    # Add embeddings to index
    index.add(embeddings)

    # Save index to disk
    faiss.write_index(index, index_path)

    # Save chunks metadata
    with open(chunks_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Index saved to {index_path}")
    print(f"Chunks saved to {chunks_path}")


def load_index(index_path: str, chunks_path: str) -> tuple[faiss.Index, list[str]]:
    """
    Load FAISS index and chunks from disk.

    Args:
        index_path: Path to FAISS index file
        chunks_path: Path to chunks JSON file

    Returns:
        Tuple of (FAISS index, list of chunks)
    """
    # Load FAISS index
    index = faiss.read_index(index_path)

    # Load chunks
    with open(chunks_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    return index, chunks
