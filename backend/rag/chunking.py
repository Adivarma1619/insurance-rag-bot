"""
Token-based text chunking with overlap for RAG.
"""
import tiktoken


def chunk_text(text: str, chunk_tokens: int = 450, overlap_tokens: int = 80) -> list[str]:
    """
    Split text into overlapping chunks based on token count.

    Args:
        text: The text to chunk
        chunk_tokens: Target size of each chunk in tokens
        overlap_tokens: Number of tokens to overlap between chunks

    Returns:
        List of text chunks
    """
    # Get the tokenizer
    encoding = tiktoken.get_encoding("cl100k_base")

    # Tokenize the entire text
    tokens = encoding.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        # Get chunk of tokens
        end = start + chunk_tokens
        chunk_tokens_slice = tokens[start:end]

        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens_slice)
        chunks.append(chunk_text)

        # Move start position forward, accounting for overlap
        start = end - overlap_tokens

        # Prevent infinite loop if overlap >= chunk_tokens
        if start <= (end - chunk_tokens):
            start = end

    return chunks
