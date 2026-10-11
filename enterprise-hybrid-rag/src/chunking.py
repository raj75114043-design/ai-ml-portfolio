def chunk_text(text: str, size: int = 512, overlap: int = 100) -> list[str]:
    """Word-based chunking with overlap (512 / 100 mirrors the production configuration)."""
    words = text.split()
    if len(words) <= size:
        return [text]
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]
