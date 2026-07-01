import re
from typing import List, Dict, Any

def clean_text(text: str) -> str:
    """Basic text cleanup."""
    # Replace multiple spaces/newlines with single ones
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()


def chunk_by_clause(text: str, max_chars: int = 4000) -> List[Dict[str, Any]]:
    """
    Splits legal contract text into clauses.
    Attempts to identify numbered headings (e.g. '1. Scope of Work', 'SECTION 3. term', 'ARTICLE IV')
    to split text into coherent clause boundaries.
    """
    # Normalize line endings
    text = text.replace('\r\n', '\n')
    
    # Define common clause headers
    # E.g. "1. Scope of Work", "Section 2.1", "Article X", "Definitions"
    clause_header_regex = re.compile(
        r'^(?:'
        r'(?:Section|SECTION|Article|ARTICLE|Clause|CLAUSE)\s+\d+(?:\.\d+)*.*'
        r'|\d+\.\s+.*'
        r'|\d+\.\d+\s+.*'
        r'|[A-Z][A-Z\s,&\-\'\"]{5,50}:?'
        r')$'
    )

    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_length = 0
    clause_index = 0

    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
            
        # Check if line starts a new clause
        is_new_clause = False
        if len(cleaned_line) < 120:
            if clause_header_regex.match(cleaned_line) or re.match(r'^(?:\d+|\([a-zA-Z0-9]+\))\s+[A-Z]', cleaned_line):
                is_new_clause = True

        # If current chunk has content and we found a new clause, or current chunk exceeds length
        if (is_new_clause and current_chunk) or (current_length + len(cleaned_line) > max_chars and current_chunk):
            clause_text = "\n".join(current_chunk)
            chunks.append({
                "clause_index": clause_index,
                "text": clause_text
            })
            clause_index += 1
            current_chunk = []
            current_length = 0
            
        current_chunk.append(cleaned_line)
        current_length += len(cleaned_line)

    # Append remaining chunk
    if current_chunk:
        clause_text = "\n".join(current_chunk)
        chunks.append({
            "clause_index": clause_index,
            "text": clause_text
        })

    return chunks


def chunk_by_paragraph(text: str, max_chars: int = 1500) -> List[Dict[str, Any]]:
    """
    Standard paragraph-based chunker. (Placeholder / fallback).
    Groups paragraphs up to max_chars characters.
    """
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_length = 0
    chunk_index = 0
    
    for para in paragraphs:
        cleaned_para = clean_text(para)
        if not cleaned_para:
            continue
            
        if current_length + len(cleaned_para) > max_chars and current_chunk:
            chunks.append({
                "clause_index": chunk_index,
                "text": "\n".join(current_chunk)
            })
            chunk_index += 1
            current_chunk = []
            current_length = 0
            
        current_chunk.append(cleaned_para)
        current_length += len(cleaned_para)
        
    if current_chunk:
        chunks.append({
            "clause_index": chunk_index,
            "text": "\n".join(current_chunk)
        })
        
    return chunks


def chunk_document(text: str, strategy: str = "clause") -> List[Dict[str, Any]]:
    """
    Dispatches to the correct chunking strategy.
    """
    if strategy == "clause":
        return chunk_by_clause(text)
    elif strategy == "paragraph":
        return chunk_by_paragraph(text)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
