from __future__ import annotations

import re
from pathlib import Path
from typing import List
from xml.etree import ElementTree as ET

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.image import partition_image


_HTML_NS = {"html": "http://www.w3.org/1999/xhtml"}


def _cell_text(cell) -> str:
    parts = [text.strip() for text in cell.itertext() if text and text.strip()]
    return " ".join(parts)


def _load_warning_tables(filepath: Path) -> List[Document]:
    try:
        tree = ET.parse(filepath)
    except ET.ParseError:
        return []

    root = tree.getroot()
    docs: List[Document] = []

    for table in root.findall(".//html:table", _HTML_NS):
        rows = table.findall("html:tr", _HTML_NS)
        if len(rows) <= 1:
            continue
        for row in rows[1:]:
            cells = row.findall("html:td", _HTML_NS)
            if len(cells) < 2:
                cells = row.findall("html:th", _HTML_NS)
            if len(cells) < 2:
                continue
            warning = _cell_text(cells[0])
            procedure = _cell_text(cells[1])
            if not warning or not procedure:
                continue
            page_content = f"Warning: {warning}\nProcedure: {procedure}"
            docs.append(
                Document(
                    page_content=page_content,
                    metadata={"warning": warning, "procedure": procedure},
                )
            )
    return docs





def _load_plain_text(path: Path) -> List[Document]:
    """Fallback loader for simple text/markdown files."""
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text_content = path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text_content = path.read_text(errors="ignore")
    normalized = text_content.strip()
    if not normalized:
        return []
    return [Document(page_content=normalized, metadata={"source": path.name})]
def _is_noise(line: str) -> bool:
    if not line:
        return True
    if line.isdigit():
        return True
    if len(line) <= 4 and not any(ch.isalpha() for ch in line):
        return True
    return False


def _clean_text(text: str) -> str:
    """Clean text while preserving important structure and context"""
    cleaned_lines: List[str] = []
    prev_line_empty = False
    
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if _is_noise(line):
            # Allow one empty line for paragraph separation
            if not prev_line_empty and cleaned_lines:
                prev_line_empty = True
            continue
        
        # Remove excessive punctuation artifacts from OCR
        line = re.sub(r'\.{3,}', '...', line)
        line = re.sub(r'-{3,}', '—', line)
        
        # Fix common OCR errors
        line = re.sub(r'\s+', ' ', line)  # Multiple spaces to single
        line = re.sub(r'(\w)\s+([.,;:!?])', r'\1\2', line)  # Remove space before punctuation
        
        # Preserve important formatting markers
        line = line.strip()
        
        cleaned_lines.append(line)
        prev_line_empty = False
    
    return "\n".join(cleaned_lines).strip()


def _total_text_length(elements) -> int:
    total = 0
    for element in elements:
        text = getattr(element, 'text', '') or ''
        total += len(text)
    return total


def _partition_pdf(path: Path):
    fast_elements = partition_pdf(filename=str(path), strategy="fast")
    if _total_text_length(fast_elements) >= 800:
        return fast_elements
    try:
        return partition_pdf(
            filename=str(path),
            strategy="hi_res",
            infer_table_structure=True,
        )
    except Exception:
        return fast_elements


def _partition_file(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _partition_pdf(path)
    if suffix in {".png", ".jpg", ".jpeg", ".heic", ".bmp", ".tif", ".tiff"}:
        return partition_image(filename=str(path))
    return partition(filename=str(path))


def _load_unstructured(path: Path) -> List[Document]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return _load_plain_text(path)
    elements = _partition_file(path)

    docs: List[Document] = []
    buffer: List[str] = []
    buffer_pages: set[int] = set()
    buffer_types: set[str] = set()
    buffer_chars = 0

    def flush_buffer() -> None:
        nonlocal buffer, buffer_pages, buffer_types, buffer_chars
        if not buffer:
            return
        metadata = {"source": str(path)}
        if buffer_pages:
            metadata["pages"] = ','.join(str(p) for p in sorted(buffer_pages))
        if buffer_types:
            metadata["types"] = ','.join(sorted(buffer_types))
        docs.append(
            Document(
                page_content='\n\n'.join(buffer),
                metadata=metadata,
            )
        )
        buffer.clear()
        buffer_pages.clear()
        buffer_types.clear()
        buffer_chars = 0

    for element in elements:
        text = getattr(element, 'text', None)
        if not text:
            continue
        cleaned = _clean_text(text)
        if not cleaned:
            continue
        if buffer_chars + len(cleaned) > 1200:
            flush_buffer()
        page_number = getattr(getattr(element, 'metadata', None), 'page_number', None)
        if page_number is not None:
            buffer_pages.add(int(page_number))
        buffer_types.add(element.__class__.__name__)
        buffer.append(cleaned)
        buffer_chars += len(cleaned)

    flush_buffer()
    return docs

def _enrich_metadata(chunk: Document) -> Document:
    """Enrich document metadata with extracted information"""
    content_lower = chunk.page_content.lower()
    
    # Detect document type/topic
    if any(word in content_lower for word in ["warning", "caution", "danger", "alert"]):
        chunk.metadata["type"] = "warning"
    elif any(word in content_lower for word in ["procedure", "step", "how to", "instructions"]):
        chunk.metadata["type"] = "procedure"
    elif any(word in content_lower for word in ["specification", "capacity", "dimension"]):
        chunk.metadata["type"] = "specification"
    else:
        chunk.metadata["type"] = "general"
    
    # Extract key terms for better retrieval
    key_terms = []
    automotive_terms = [
        "engine", "brake", "transmission", "suspension", "steering", "tire", "tyre",
        "battery", "alternator", "starter", "fuel", "oil", "coolant", "airbag",
        "abs", "esp", "traction", "cruise", "climate", "ac", "heater", "light",
        "indicator", "dashboard", "speedometer", "odometer", "warning", "fault"
    ]
    
    for term in automotive_terms:
        if term in content_lower:
            key_terms.append(term)
    
    if key_terms:
        chunk.metadata["key_terms"] = ",".join(key_terms[:5])  # Top 5 terms
    
    return chunk


def load_manual(filepath: str) -> List[Document]:
    """Load and process a car manual with intelligent chunking and metadata enrichment"""
    path = Path(filepath)
    
    # Try to load structured warning tables first
    table_docs = _load_warning_tables(path)
    if table_docs:
        # Enrich table documents
        return [_enrich_metadata(doc) for doc in table_docs]

    # Load unstructured content
    raw_docs = _load_unstructured(path)
    if not raw_docs:
        return []

    # Use semantic chunking with overlap for better context preservation
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
        keep_separator=True,
    )
    chunks = splitter.split_documents(raw_docs)

    # Clean and enrich chunks
    cleaned_chunks: List[Document] = []
    for chunk in chunks:
        cleaned = _clean_text(chunk.page_content)
        if not cleaned or len(cleaned) < 50:  # Skip very short chunks
            continue
        chunk.page_content = cleaned
        
        # Enrich with metadata
        chunk = _enrich_metadata(chunk)
        cleaned_chunks.append(chunk)
    
    return cleaned_chunks
