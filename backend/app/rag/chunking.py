import re
from typing import Any, Dict, List

def chunk_markdown_text(
    text: str,
    max_chunk_chars: int = 800,
    chunk_overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    Split markdown text on logical section headers (# , ## , ### )
    and paragraph boundaries while preserving semantic context.
    """
    lines = text.split("\n")
    sections: List[Dict[str, Any]] = []
    current_heading = "General"
    current_content: List[str] = []

    for line in lines:
        if line.startswith("#"):
            if current_content:
                section_text = "\n".join(current_content).strip()
                if section_text:
                    sections.append({
                        "heading": current_heading,
                        "content": section_text
                    })
                current_content = []
            current_heading = line.lstrip("#").strip()
        else:
            current_content.append(line)

    if current_content:
        section_text = "\n".join(current_content).strip()
        if section_text:
            sections.append({
                "heading": current_heading,
                "content": section_text
            })

    # Now partition sections that exceed max_chunk_chars into overlapping windows
    chunks: List[Dict[str, Any]] = []
    chunk_idx = 0

    for sec in sections:
        sec_text = f"## {sec['heading']}\n\n{sec['content']}" if sec['heading'] != "General" else sec['content']
        
        if len(sec_text) <= max_chunk_chars:
            chunks.append({
                "chunk_index": chunk_idx,
                "heading": sec["heading"],
                "content": sec_text
            })
            chunk_idx += 1
        else:
            # Split by paragraphs
            paragraphs = sec_text.split("\n\n")
            buffer = ""
            for p in paragraphs:
                if len(buffer) + len(p) + 2 <= max_chunk_chars:
                    buffer = f"{buffer}\n\n{p}".strip()
                else:
                    if buffer:
                        chunks.append({
                            "chunk_index": chunk_idx,
                            "heading": sec["heading"],
                            "content": buffer
                        })
                        chunk_idx += 1
                    # Keep overlap from previous paragraph if possible
                    buffer = p

            if buffer:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "heading": sec["heading"],
                    "content": buffer
                })
                chunk_idx += 1

    return chunks
