# OCR Configuration: Local vs Production

## Summary

**Local Evaluation (64% accuracy)**: OCR **ENABLED**  
**Production Deployment (HuggingFace)**: OCR **DISABLED** (PyMuPDF text-only)

---

## Background

### Local Evaluation Configuration (api/ folder)

The **Ultimate RAG experiment** that achieved **64% accuracy** used:

```python
# In rag_experiments_ultimate.py
from document_loader import _load_pdf_fast, _enrich_metadata

raw_docs = _load_pdf_fast(str(PDF_PATH))  # No disable_ocr parameter = OCR ENABLED
```

- **Library**: `unstructured[pdf,md]==0.18.11` with full OCR support
- **OCR Engine**: Tesseract via pytesseract
- **NLTK**: Required for unstructured text processing
- **Behavior**: 
  - First attempts PyMuPDF text extraction (fast)
  - Falls back to OCR for image-based or scanned pages
  - Full support for complex PDFs with mixed content

### Production Deployment (HuggingFace Spaces)

The **deployed version** uses simplified PDF parsing:

```python
# In tmp/hf-deploy/ManualAi/document_loader.py
def partition_pdf(filename, strategy="fast", **kwargs):
    """Simple PyMuPDF-based PDF parser - no NLTK required"""
    with fitz.open(filename) as pdf:
        for page_num in range(pdf.page_count):
            text = page.get_text("text").strip()
            # ... extract text only, no OCR fallback
```

- **Library**: PyMuPDF only (no unstructured, no NLTK)
- **OCR Engine**: None
- **NLTK**: Not required
- **Behavior**:
  - PyMuPDF text extraction only
  - No OCR fallback for image-based pages
  - Fast, reliable, but limited to digital PDFs with embedded text

---

## Why the Change?

### The NLTK Permission Problem

During HuggingFace deployment, we encountered a critical blocker:

```
PermissionError: [Errno 13] Permission denied: '/nltk_data'
```

**Root cause**: The `unstructured` library v0.18.11 has a hardcoded `/nltk_data` path in its source code that ignores the `NLTK_DATA` environment variable. HuggingFace Spaces only allows writing to `/tmp`, making this incompatible.

**Attempted solutions (all failed)**:
1. ✗ Set `NLTK_DATA=/tmp/nltk_data` in Dockerfile ENV
2. ✗ Patch unstructured source during build
3. ✗ Pre-download NLTK data to various locations
4. ✗ Use different directories (/data, /tmp, /app)

**Final solution**: Remove `unstructured` entirely, use PyMuPDF-only parsing.

---

## Impact Assessment

### For Digital PDFs (Most Car Manuals)

✅ **No impact** - Most modern car manuals are digital PDFs with embedded text  
✅ Production and evaluation results should be **comparable**  
✅ Faster processing, more reliable deployment

### For Scanned/Image PDFs

⚠️ **Degraded** - No text will be extracted from image-only pages  
⚠️ Accuracy will drop significantly for scanned manuals  
⚠️ Users should be advised to upload digital PDFs only

### Test Case: 2023 Toyota 4Runner Manual

**Evaluation PDF**: Likely a digital PDF with embedded text  
**Expected**: 64% accuracy should be maintained or close  
**To verify**: Upload sample and compare retrieval accuracy

---

## Deployment Strategy

### Free Tier (Current - HuggingFace)

```python
# OCR disabled by default
MANUAL_DISABLE_OCR = os.getenv("MANUAL_DISABLE_OCR", "false").lower() in ("true", "1", "yes")

# But effective behavior: NO OCR capability at all (PyMuPDF only)
```

**Reasoning**:
- Free tier has memory/timeout constraints
- OCR is slow and resource-intensive
- Most users upload digital PDFs anyway
- Simpler deployment = fewer failures

### Paid Tier (Future Consideration)

If upgrading to paid HuggingFace Spaces:
- Can use writable persistent storage
- Could re-enable full `unstructured` with OCR
- Would match local evaluation environment exactly
- Trade-off: Higher cost, slower processing, more complex deployment

---

## Configuration Matrix

| Feature | Local Eval | HuggingFace Free | HuggingFace Paid (Future) |
|---------|------------|------------------|---------------------------|
| **PDF Parser** | unstructured | PyMuPDF | unstructured |
| **OCR Support** | ✅ Yes | ❌ No | ✅ Yes |
| **NLTK Required** | ✅ Yes | ❌ No | ✅ Yes |
| **Filesystem Access** | Full | `/tmp` only | Persistent storage |
| **Accuracy (digital PDFs)** | 64% | ~64% (expected) | 64% |
| **Accuracy (scanned PDFs)** | 64% | <10% (no text) | 64% |
| **Processing Speed** | Medium | Fast | Medium |
| **Deployment Complexity** | N/A | Simple | Complex |

---

## User Guidance

### Upload Guidelines (Free Tier)

**Recommended**: Digital PDFs only
- Modern car manuals (2010+)
- PDFs with selectable/copyable text
- File size: <2MB recommended, 5MB max

**Not Recommended**: 
- Scanned documents
- Image-only PDFs
- Old manuals without embedded text

**Test method**: Open PDF, try to select text with mouse
- ✅ Text selectable → Will work great
- ❌ Text not selectable → OCR needed (not available)

---

## Documentation Consistency

### README.md Claims

Current claim: **"64% accuracy within ±2 pages"**

**Clarification needed**:
```markdown
**Local Evaluation**: 64% accuracy (with OCR enabled)
**Production Deployment**: OCR disabled for reliability (digital PDFs only)
```

### Technical Approach Section

Add note:
```markdown
> **Note**: The production deployment uses PyMuPDF-only text extraction 
> (no OCR) for simplicity and reliability on free tier hosting. 
> The 64% accuracy was measured with OCR enabled locally. 
> For digital PDFs with embedded text (most modern car manuals), 
> results should be comparable.
```

---

## Future Improvements

### Option 1: Verify Accuracy on PyMuPDF-Only

1. Re-run evaluation locally with `disable_ocr=True`
2. Measure accuracy drop (if any)
3. Update README with accurate production metrics

### Option 2: Alternative OCR Solution

Investigate lightweight OCR alternatives:
- EasyOCR (no NLTK dependency)
- PaddleOCR (faster than Tesseract)
- Cloud OCR APIs (Google Vision, AWS Textract)

### Option 3: Hybrid Approach

- Keep PyMuPDF-only for free tier
- Offer OCR-enabled endpoint on paid tier
- Let users choose based on their PDF type

---

## Code Changes Summary

### Files Modified for PyMuPDF-Only

1. **tmp/hf-deploy/ManualAi/requirements.txt** (commit d6a0604)
   - Removed: `unstructured[pdf,md]==0.18.11`, `pytesseract`
   - Kept: `pymupdf`, `pillow`, core dependencies

2. **tmp/hf-deploy/ManualAi/document_loader.py** (commit d6a0604)
   - Created stub: `partition_pdf()` using PyMuPDF only
   - Removed: All unstructured imports
   - Maintained: `disable_ocr` parameter for API compatibility

3. **tmp/hf-deploy/ManualAi/Dockerfile** (commit 4748eac)
   - Removed: All NLTK download commands
   - Simplified: Dependencies installation

### Files NOT Changed (Still Use Full OCR)

- `api/document_loader.py` - Original with unstructured + OCR
- `api/requirements.txt` - Full dependencies for local dev
- `hf-space/rag_experiments_ultimate.py` - Evaluation code

---

## Testing Checklist

- [ ] Upload digital PDF sample (Toyota 4Runner 30 pages)
- [ ] Verify text extraction works
- [ ] Compare retrieval quality vs local evaluation
- [ ] Document actual production accuracy
- [ ] Update README with accurate claims
- [ ] Add user guidance for PDF type selection

---

## Contact

For questions about OCR configuration or deployment strategy, refer to:
- HuggingFace deployment issues: `HUGGINGFACE_DEPLOYMENT_GUIDE.md`
- NLTK permission errors: Git commits d6a0604, 4748eac, b81223a
- Original evaluation: `hf-space/rag_experiments_ultimate.py`

**Last Updated**: October 11, 2025  
**Status**: Production using PyMuPDF-only, local eval used OCR
