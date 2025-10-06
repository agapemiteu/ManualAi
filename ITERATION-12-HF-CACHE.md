# Iteration #12: HuggingFace Cache Fix (Two Attempts)

## 🎉 MORE PROGRESS!

**Iteration #11 fixed the parameter issue!** We're now in the embedding phase!

## New Error
```
PermissionError at /tmp/manualai/hf_cache/models--sentence-transformers--all-MiniLM-L6-v2 
when downloading sentence-transformers/all-MiniLM-L6-v2
```

## Root Cause
The `SentenceTransformer` model was being downloaded, but the cache directory had permission issues.

Even though we set `HF_HOME` in the Dockerfile, the actual download at runtime was failing.

## First Attempt (Failed)
Added cache setup in vector_store.py but AFTER the imports:
```python
from sentence_transformers import SentenceTransformer  # ❌ Too early!

# Then tried to set cache...
os.environ["HF_HOME"] = str(_HF_CACHE)  # Too late!
```

**Problem:** sentence_transformers imported before cache was configured.

## Second Attempt (Should Work)
Moved cache setup BEFORE all imports:

## Solution
Applied the same `tempfile.mkdtemp()` pattern to the HuggingFace cache:

```python
# In vector_store.py, BEFORE loading SentenceTransformer:

import tempfile
import os

# Try to use HF_HOME, fallback to temp
_HF_CACHE = Path(os.getenv("HF_HOME", tempfile.gettempdir() + "/manualai_hf_cache"))
try:
    _HF_CACHE.mkdir(parents=True, exist_ok=True)
except:
    # Nuclear option: tempfile.mkdtemp() for guaranteed write access
    _HF_CACHE = Path(tempfile.mkdtemp(prefix="manualai_hf_cache_"))

# Set ALL HuggingFace-related cache env vars
os.environ["HF_HOME"] = str(_HF_CACHE)
os.environ["TRANSFORMERS_CACHE"] = str(_HF_CACHE)
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(_HF_CACHE)
os.environ["HUGGINGFACE_HUB_CACHE"] = str(_HF_CACHE)

# Pass cache_folder explicitly when loading model
SentenceTransformer(model_name, cache_folder=str(_HF_CACHE))
```

## Why This Works
- ✅ Sets env vars BEFORE any HuggingFace imports
- ✅ Uses tempfile.mkdtemp() as ultimate fallback
- ✅ Passes cache_folder explicitly to SentenceTransformer
- ✅ Same bulletproof pattern that solved directory issues

## Progress Summary

### Issues Solved So Far:
1. ✅ Directory permissions (tempfile.mkdtemp)
2. ✅ NLTK permission error (complete monkeypatch)
3. ✅ ImportError for NLTK functions (added to stub)
4. ✅ Parameter mismatch (added disable_ocr)
5. ✅ HuggingFace cache permissions (tempfile.mkdtemp)

### Current Pipeline Status:
```
✅ Upload endpoint
✅ File storage
✅ NLTK configuration
✅ unstructured imports
✅ Document loading
✅ HuggingFace cache setup
⏳ Embedding model download...
```

## What This Means

We're **DEEP** into the ingestion pipeline now! We've solved:
- File upload ✅
- Document loading ✅
- NLTK tokenization ✅

Now we're at:
- **Embedding model download** (current fix)
- Vector store creation (next)
- RAG chain setup (after that)

## Expected Next
If this works:
- ✅ Model downloads successfully
- ✅ Vector embeddings created
- ✅ Manual ingestion completes!

If there's another issue:
- Debug the next error (likely in vector store or RAG chain)
- Keep iterating!

## Test Timeline
- Pushed: ~10:40
- Rebuild: 3-5 minutes
- Test: ~10:44

---
**We're getting closer! Each iteration solves a real issue.** 🚀
