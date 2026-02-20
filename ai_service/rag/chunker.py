"""
DevMind - Code chunking logic.
Splits source files into ~500 token chunks for embedding and retrieval.
"""

import re
from typing import List, Tuple


def estimate_tokens(text: str) -> int:
    """
    Rough token estimate: ~4 chars per token for code.
    """
    return len(text) // 4


def chunk_code(
    content: str,
    file_path: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[Tuple[str, dict]]:
    """
    Chunk source code into overlapping segments.

    Args:
        content: Raw file content
        file_path: Source file path (for metadata)
        chunk_size: Target tokens per chunk (~2000 chars)
        overlap: Token overlap between chunks

    Returns:
        List of (chunk_text, metadata) tuples
    """
    if not content or not content.strip():
        return []

    # Convert token sizes to char sizes (approx 4 chars = 1 token)
    char_chunk = chunk_size * 4
    char_overlap = overlap * 4

    chunks: List[Tuple[str, dict]] = []
    lines = content.split("\n")
    current_chunk = []
    current_size = 0

    for i, line in enumerate(lines):
        line_with_newline = line + "\n"
        line_tokens = estimate_tokens(line_with_newline)

        if current_size + line_tokens > chunk_size and current_chunk:
            # Save current chunk
            chunk_text = "\n".join(current_chunk)
            metadata = {
                "file_path": file_path,
                "start_line": i - len(current_chunk) + 1,
                "end_line": i,
            }
            chunks.append((chunk_text, metadata))

            # Keep overlap lines for context
            overlap_chars = 0
            overlap_lines = []
            for j in range(len(current_chunk) - 1, -1, -1):
                l = current_chunk[j]
                if overlap_chars + len(l) > char_overlap:
                    break
                overlap_lines.insert(0, l)
                overlap_chars += len(l)

            current_chunk = overlap_lines
            current_size = sum(estimate_tokens(l + "\n") for l in overlap_lines)

        current_chunk.append(line)
        current_size += line_tokens

    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        metadata = {
            "file_path": file_path,
            "start_line": len(lines) - len(current_chunk) + 1,
            "end_line": len(lines),
        }
        chunks.append((chunk_text, metadata))

    return chunks
