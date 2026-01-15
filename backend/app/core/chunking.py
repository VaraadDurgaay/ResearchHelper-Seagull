"""
Chunking Module
Handles text chunking strategies for splitting papers into smaller chunks.
"""
from typing import List
from dataclasses import dataclass
import re


@dataclass
class Chunk:
    """Represents a text chunk"""
    text: str
    chunk_index: int
    page_number: int
    start_char: int
    end_char: int
    paper_id: str


def chunk_text(
    text: str, 
    page_number: int, 
    paper_id: str,
    chunk_size: int = 1000, 
    overlap: int = 200
) -> List[Chunk]:
    """
    Split text into chunks with overlap.
    
    Args:
        text: Text to chunk
        page_number: Page number this text is from
        paper_id: ID of the paper
        chunk_size: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of Chunk objects
    """
    if not text or len(text.strip()) == 0:
        return []
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If this isn't the last chunk, try to break at a sentence boundary
        if end < len(text):
            # Look for sentence endings near the chunk boundary
            # Check last 100 characters for sentence endings
            boundary_search = text[max(start, end - 100):end]
            sentence_endings = re.finditer(r'[.!?]\s+', boundary_search)
            sentence_ends = list(sentence_endings)
            
            if sentence_ends:
                # Use the last sentence ending found
                last_sentence_end = sentence_ends[-1]
                # Adjust end to include the sentence ending
                end = start + (end - 100) + last_sentence_end.end()
        
        chunk_text = text[start:end].strip()
        
        if chunk_text:
            chunks.append(Chunk(
                text=chunk_text,
                chunk_index=chunk_index,
                page_number=page_number,
                start_char=start,
                end_char=min(end, len(text)),
                paper_id=paper_id
            ))
            chunk_index += 1
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def chunk_by_sentences(
    text: str, 
    page_number: int,
    paper_id: str,
    max_chunk_size: int = 1000
) -> List[Chunk]:
    """
    Chunk text by sentences, respecting sentence boundaries.
    
    Args:
        text: Text to chunk
        page_number: Page number this text is from
        paper_id: ID of the paper
        max_chunk_size: Maximum characters per chunk
        
    Returns:
        List of Chunk objects
    """
    if not text or len(text.strip()) == 0:
        return []
    
    # Split by sentence endings
    sentences = re.split(r'([.!?]\s+)', text)
    
    # Recombine sentences with their endings
    combined_sentences = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            combined_sentences.append(sentences[i] + sentences[i + 1])
        else:
            combined_sentences.append(sentences[i])
    
    chunks = []
    current_chunk = ""
    chunk_index = 0
    start_char = 0
    
    for sentence in combined_sentences:
        # If adding this sentence would exceed max size, save current chunk
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(Chunk(
                text=current_chunk.strip(),
                chunk_index=chunk_index,
                page_number=page_number,
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                paper_id=paper_id
            ))
            chunk_index += 1
            start_char += len(current_chunk)
            current_chunk = sentence
        else:
            current_chunk += sentence
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(Chunk(
            text=current_chunk.strip(),
            chunk_index=chunk_index,
            page_number=page_number,
            start_char=start_char,
            end_char=start_char + len(current_chunk),
            paper_id=paper_id
        ))
    
    return chunks


def chunk_with_sliding_window(
    text: str,
    page_number: int,
    paper_id: str,
    window_size: int = 1000,
    stride: int = 500
) -> List[Chunk]:
    """
    Chunk text using a sliding window approach.
    
    Args:
        text: Text to chunk
        page_number: Page number this text is from
        paper_id: ID of the paper
        window_size: Size of the sliding window
        stride: Step size for the window
        
    Returns:
        List of Chunk objects
    """
    if not text or len(text.strip()) == 0:
        return []
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        end = min(start + window_size, len(text))
        chunk_text = text[start:end].strip()
        
        if chunk_text:
            chunks.append(Chunk(
                text=chunk_text,
                chunk_index=chunk_index,
                page_number=page_number,
                start_char=start,
                end_char=end,
                paper_id=paper_id
            ))
            chunk_index += 1
        
        start += stride
        if start >= len(text):
            break
    
    return chunks
