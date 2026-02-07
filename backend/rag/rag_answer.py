"""
RAG retrieval and answer generation using Groq API.
"""
import os
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv
from .embed_store import EMBED_MODEL

# Load environment variables from .env file
load_dotenv()

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama-3.3-70b-versatile")


def embed_query(query: str) -> np.ndarray:
    """
    Embed a single query string.
    Uses OpenAI for embeddings as Grok doesn't support embeddings yet.

    Args:
        query: Query text

    Returns:
        Normalized embedding vector
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required for embeddings")

    client = OpenAI(api_key=openai_api_key)

    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=[query]
    )

    embedding = np.array([response.data[0].embedding], dtype=np.float32)
    faiss.normalize_L2(embedding)

    return embedding


def retrieve(query: str, index: faiss.Index, chunks: list[str], k: int = 4) -> list[str]:
    """
    Retrieve top-k most relevant chunks for a query.

    Args:
        query: User query
        index: FAISS index
        chunks: List of text chunks
        k: Number of chunks to retrieve

    Returns:
        List of relevant text chunks
    """
    # Embed the query
    query_embedding = embed_query(query)

    # Search the index
    scores, indices = index.search(query_embedding, k)

    # Get the matching chunks
    retrieved_chunks = [chunks[i] for i in indices[0]]

    return retrieved_chunks


def generate_answer(query: str, context_chunks: list[str]) -> str:
    """
    Generate an answer using Groq chat completion with retrieved context.

    Args:
        query: User query
        context_chunks: Retrieved context chunks

    Returns:
        Generated answer
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required for chat completions")

    # Groq is OpenAI-SDK-compatible — just swap base URL + key
    client = OpenAI(
        api_key=groq_api_key,
        base_url=GROQ_BASE_URL
    )

    # Combine context chunks
    context = "\n\n".join(context_chunks)

    # System prompt
    system_prompt = """You are a helpful Insurance Agency Customer Care assistant.

Your role is to answer customer questions about insurance policies, claims, and coverage using ONLY the information provided in the context below.

Guidelines:
- Provide clear, accurate answers based solely on the context
- If the answer is not in the context, politely say you don't have that information and offer to connect them with a human agent
- Be friendly and professional
- Keep answers concise but complete
- Do not make up information or provide answers not supported by the context

Context:
{context}"""

    # Create messages
    messages = [
        {"role": "system", "content": system_prompt.format(context=context)},
        {"role": "user", "content": query}
    ]

    # Generate response
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    answer = response.choices[0].message.content

    return answer
