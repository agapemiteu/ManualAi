from __future__ import annotations

import io
import hashlib
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple
from xml.etree import ElementTree as ET

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.image import partition_image


logger = logging.getLogger(__name__)

_LOG_LEVEL = os.getenv("MANUALAI_LOG_LEVEL")
if _LOG_LEVEL:
    logger.setLevel(getattr(logging, _LOG_LEVEL.upper(), logging.INFO))
elif logger.level == logging.NOTSET:
    logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(handler)

_HTML_NS = {"html": "http://www.w3.org/1999/xhtml"}

_MIN_FAST_TEXT = 100
_MIN_PAGE_TEXT = 64
_OCR_DPI = int(os.getenv("MANUAL_OCR_DPI", "170"))
_OCR_MAX_WORKERS = max(1, min(int(os.getenv("MANUAL_OCR_WORKERS", str(os.cpu_count() or 1))), 6))
_OCR_CACHE_DIR = Path(os.getenv("MANUAL_OCR_CACHE_DIR", "../data/manual_store/ocr_cache")).resolve()
_OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_OCR_TIMEOUT = float(os.getenv("MANUAL_OCR_TIMEOUT", "12.0"))
_OCR_CONFIG = os.getenv("MANUAL_OCR_CONFIG", "--psm 6 --oem 1")


class ManualLoadCancelledError(Exception):
    """Raised when manual ingestion is cancelled by the caller."""


class _OCRElement:
    """Lightweight element to unify OCR text with Unstructured output."""

    __slots__ = ("text", "metadata")

    def __init__(self, text: str, page_number: int) -> None:
        self.text = text
        self.metadata = SimpleNamespace()
        self.metadata.page_number = page_number



def _check_cancel(cancel_callback: Optional[Callable[[], bool]]) -> None:
    if cancel_callback and cancel_callback():
        raise ManualLoadCancelledError("Manual ingestion cancelled by user.")



def _collect_page_lengths(elements: Sequence[object]) -> Dict[int, int]:
    lengths: Dict[int, int] = {}
    for element in elements:
        text = getattr(element, "text", "") or ""
        if not text:
            continue
        metadata = getattr(element, "metadata", None)
        page_number = getattr(metadata, "page_number", None)
        if page_number is None:
            continue
        page_key = int(page_number)
        lengths[page_key] = lengths.get(page_key, 0) + len(text)
    return lengths



def _filter_elements_by_pages(elements: Sequence[object], pages: Iterable[int]) -> List[object]:
    page_set = {int(page) for page in pages}
    if not page_set:
        return list(elements)
    filtered: List[object] = []
    for element in elements:
        metadata = getattr(element, "metadata", None)
        page_number = getattr(metadata, "page_number", None)
        if page_number is not None and int(page_number) in page_set:
            continue
        filtered.append(element)
    return filtered



def _merge_elements(existing: Sequence[object], extra: Sequence[object]) -> List[object]:
    combined: List[Tuple[Tuple[int, int, int], object]] = []
    for idx, element in enumerate(existing):
        metadata = getattr(element, "metadata", None)
        page_number = getattr(metadata, "page_number", None)
        page_key = int(page_number) if page_number is not None else 10**9
        combined.append(((page_key, idx, 0), element))
    base_index = len(existing)
    for offset, element in enumerate(extra):
        metadata = getattr(element, "metadata", None)
        page_number = getattr(metadata, "page_number", None)
        page_key = int(page_number) if page_number is not None else 10**9
        combined.append(((page_key, base_index + offset, 1), element))
    combined.sort(key=lambda item: item[0])
    return [item[1] for item in combined]



def _render_pages_for_ocr(path: Path, pages: Sequence[int], cancel_callback: Optional[Callable[[], bool]]) -> List[Tuple[int, bytes]]:
    if not pages:
        return []
    logger.info("PDF %s: rendering %s pages at %sdpi for OCR", path, len(pages), _OCR_DPI)
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        logger.warning("PyMuPDF not available for OCR fallback: %s", exc)
        return []
    images: List[Tuple[int, bytes]] = []
    with fitz.open(path) as pdf:
        for page_number in pages:
            _check_cancel(cancel_callback)
            if page_number < 1 or page_number > pdf.page_count:
                logger.warning("PDF %s: requested OCR for invalid page %s", path, page_number)
                continue
            page = pdf.load_page(page_number - 1)
            zoom = _OCR_DPI / 72
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csGRAY, alpha=False)
            images.append((page_number, pix.tobytes("png")))
    logger.info("PDF %s: prepared %s page images for OCR", path, len(images))
    return images


def _run_ocr_on_images(images: Sequence[Tuple[int, bytes]], cancel_callback: Optional[Callable[[], bool]]) -> List[_OCRElement]:
    if not images:
        return []
    try:
        import pytesseract  # type: ignore
    except ImportError as exc:
        logger.warning("pytesseract not available for OCR fallback: %s", exc)
        return []
    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:
        logger.warning("Pillow not available for OCR fallback: %s", exc)
        return []
    logger.info("Running OCR on %s rendered pages", len(images))
    results: Dict[int, str] = {}
    lang = os.getenv("MANUAL_OCR_LANG", "eng")

    def worker(page_number: int, png_bytes: bytes) -> Tuple[int, str]:
        _check_cancel(cancel_callback)
        digest = hashlib.md5(png_bytes).hexdigest()
        cache_path = _OCR_CACHE_DIR / f"{digest}.txt"
        if cache_path.exists():
            try:
                cached = cache_path.read_text(encoding="utf-8").strip()
                if cached:
                    logger.info("OCR cache hit for page %s", page_number)
                    return page_number, cached
            except Exception as exc:  # pragma: no cover
                logger.debug("Failed to read OCR cache for page %s: %s", page_number, exc)
        with Image.open(io.BytesIO(png_bytes)) as img:
            img = img.convert("L")
            try:
                text = pytesseract.image_to_string(
                    img,
                    lang=lang,
                    timeout=_OCR_TIMEOUT,
                    config=_OCR_CONFIG,
                )
            except RuntimeError as exc:
                logger.warning("OCR timed out for page %s: %s", page_number, exc)
                return page_number, ""
        cleaned = _clean_text(text)
        try:
            cache_path.write_text(cleaned, encoding="utf-8")
        except Exception as exc:  # pragma: no cover
            logger.debug("Failed to write OCR cache for page %s: %s", page_number, exc)
        logger.info("OCR extracted %s characters from page %s", len(cleaned), page_number)
        return page_number, cleaned

    with ThreadPoolExecutor(max_workers=_OCR_MAX_WORKERS) as executor:
        futures = {executor.submit(worker, page, data): page for page, data in images}
        for future in as_completed(futures):
            _check_cancel(cancel_callback)
            page_number = futures[future]
            try:
                page, text = future.result()
            except ManualLoadCancelledError:
                raise
            except Exception as exc:  # pragma: no cover
                logger.warning("OCR failed for page %s: %s", page_number, exc)
                continue
            if text:
                results[page] = text
    elements: List[_OCRElement] = []
    for page_number in sorted(results):
        cleaned = results[page_number].strip()
        if not cleaned:
            continue
        elements.append(_OCRElement(cleaned, page_number))
    logger.info("OCR produced text for %s/%s pages", len(elements), len(images))
    return elements



def _partition_pdf(path: Path, cancel_callback: Optional[Callable[[], bool]] = None):
    """Partition a PDF using the fast strategy with selective OCR fallbacks."""
    _check_cancel(cancel_callback)

    start_time = time.perf_counter()
    logger.info("PDF %s: running fast partition", path)

    fast_elements = partition_pdf(filename=str(path), strategy="fast")
    fast_text = _total_text_length(fast_elements)
    page_lengths = _collect_page_lengths(fast_elements)
    logger.info("PDF %s: fast strategy produced %s characters across %s pages", path, fast_text, len(page_lengths))

    text_replacements: List[_OCRElement] = []
    ocr_pages: List[int] = []

    try:
        import fitz  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        if fast_text < _MIN_FAST_TEXT:
            logger.warning("PyMuPDF unavailable; returning fast output without OCR fallback: %s", exc)
        return fast_elements

    with fitz.open(path) as pdf:
        total_pages = pdf.page_count
        logger.info("PDF %s: scanning %s pages for inline text", path, total_pages)
        for index in range(total_pages):
            page_number = index + 1
            _check_cancel(cancel_callback)
            if page_lengths.get(page_number, 0) > 0:
                continue
            raw_text = pdf[index].get_text("text").strip()
            if raw_text:
                cleaned = _clean_text(raw_text)
                if cleaned:
                    text_replacements.append(_OCRElement(cleaned, page_number))
                    logger.info("PDF %s: extracted %s chars directly from page %s", path, len(cleaned), page_number)
                continue
            ocr_pages.append(page_number)

    if ocr_pages:
        logger.info("PDF %s: %s pages require OCR fallback", path, len(ocr_pages))
    else:
        logger.info("PDF %s: all pages contained extractable text", path)

    pages_to_replace = {int(element.metadata.page_number) for element in text_replacements}
    pages_to_replace.update(int(page) for page in ocr_pages)

    filtered_fast = _filter_elements_by_pages(fast_elements, pages_to_replace)

    rendered_images = _render_pages_for_ocr(path, sorted(ocr_pages), cancel_callback)
    ocr_elements = _run_ocr_on_images(rendered_images, cancel_callback)

    extra_elements: List[object] = [*text_replacements, *ocr_elements]
    combined = _merge_elements(filtered_fast, extra_elements) if extra_elements else filtered_fast
    combined_length = _total_text_length(combined)
    logger.info("PDF %s: combined text after OCR contains %s characters", path, combined_length)

    if combined_length >= _MIN_FAST_TEXT or not ocr_pages:
        logger.info("PDF %s: returning combined output without hi_res fallback (elapsed %.2fs)", path, time.perf_counter() - start_time)
        return combined

    _check_cancel(cancel_callback)
    try:
        logger.info("PDF %s: invoking hi_res fallback", path)
        hi_res = partition_pdf(filename=str(path), strategy="hi_res", infer_table_structure=True)
    except Exception as exc:  # pragma: no cover - best effort logging
        logger.warning("PDF %s: hi_res OCR fallback failed: %s", path, exc)
        return combined

    hi_res_length = _total_text_length(hi_res)
    logger.info("PDF %s: hi_res fallback returned %s characters (elapsed %.2fs)", path, hi_res_length, time.perf_counter() - start_time)
    return hi_res if hi_res_length > combined_length else combined


def _partition_file(path: Path, cancel_callback: Optional[Callable[[], bool]] = None):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _partition_pdf(path, cancel_callback=cancel_callback)
    _check_cancel(cancel_callback)
    if suffix in {".png", ".jpg", ".jpeg", ".heic", ".bmp", ".tif", ".tiff"}:
        return partition_image(filename=str(path))
    return partition(filename=str(path))



def _load_pdf_fast(path: Path, cancel_callback: Optional[Callable[[], bool]] = None) -> List[Document]:
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        logger.warning("PyMuPDF not available for fast PDF pipeline: %s", exc)
        return []

    _check_cancel(cancel_callback)
    documents: List[Document] = []
    ocr_targets: List[int] = []
    page_texts: Dict[int, str] = {}

    with fitz.open(path) as pdf:
        total_pages = pdf.page_count
        logger.info("PDF %s: fast pipeline opened with %s pages", path, total_pages)
        for index in range(total_pages):
            page_number = index + 1
            _check_cancel(cancel_callback)
            page = pdf.load_page(index)
            extracted = page.get_text("text") or ""
            cleaned = _clean_text(extracted)
            if cleaned:
                page_texts[page_number] = cleaned
                continue
            ocr_targets.append(page_number)

        if ocr_targets:
            logger.info("PDF %s: %s pages require OCR in fast pipeline", path, len(ocr_targets))
            images: List[Tuple[int, bytes]] = []
            zoom = _OCR_DPI / 72
            matrix = fitz.Matrix(zoom, zoom)
            for page_number in ocr_targets:
                _check_cancel(cancel_callback)
                page = pdf.load_page(page_number - 1)
                pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csGRAY, alpha=False)
                images.append((page_number, pix.tobytes("png")))
            ocr_elements = _run_ocr_on_images(images, cancel_callback)
            for element in ocr_elements:
                text = _clean_text(element.text)
                if text:
                    page_texts[int(element.metadata.page_number)] = text

    for page_number in sorted(page_texts):
        documents.append(
            Document(
                page_content=page_texts[page_number],
                metadata={"source": str(path), "page": page_number},
            )
        )

    logger.info("PDF %s: fast pipeline produced %s document chunks", path, len(documents))
    return documents

def _load_unstructured(path: Path, cancel_callback: Optional[Callable[[], bool]] = None) -> List[Document]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return _load_plain_text(path)
    if suffix == ".pdf":
        fast_docs = _load_pdf_fast(path, cancel_callback=cancel_callback)
        if fast_docs:
            return fast_docs
    elements = _partition_file(path, cancel_callback=cancel_callback)

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
        _check_cancel(cancel_callback)
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


def load_manual(filepath: str, *, cancel_callback: Optional[Callable[[], bool]] = None) -> List[Document]:
    """Load and process a car manual with intelligent chunking and metadata enrichment"""
    path = Path(filepath)
    _check_cancel(cancel_callback)

    # Try to load structured warning tables first
    table_docs = _load_warning_tables(path)
    if table_docs:
        # Enrich table documents
        return [_enrich_metadata(doc) for doc in table_docs]

    # Load unstructured content
    _check_cancel(cancel_callback)
    raw_docs = _load_unstructured(path, cancel_callback=cancel_callback)
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
        _check_cancel(cancel_callback)
        cleaned = _clean_text(chunk.page_content)
        if not cleaned or len(cleaned) < 50:  # Skip very short chunks
            continue
        chunk.page_content = cleaned
        
        # Enrich with metadata
        chunk = _enrich_metadata(chunk)
        cleaned_chunks.append(chunk)
    
    return cleaned_chunks
