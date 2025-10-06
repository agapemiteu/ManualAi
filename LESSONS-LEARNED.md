# 🎓 LESSONS LEARNED - Docker Permission Hell Journey

**Project:** ManualAI Car Manual RAG Chatbot  
**Platform:** HuggingFace Spaces (Docker SDK)  
**Duration:** ~2 hours of debugging  
**Date:** 2025-10-06

---

## 📖 The Journey

### Initial Problem:
"Manual stuck in processing status indefinitely"

### Root Cause Discovery:
HuggingFace Spaces runs Docker containers with **highly restricted permissions**:
- Non-root user (security best practice)
- Limited write access (even to `/tmp` and `/app`)
- No persistent storage without explicit configuration
- Environment variables must be set in specific order

---

## 🔥 Iteration History

### Iteration 1: Basic `/tmp` Approach
**Attempt:** Move all storage to `/tmp`  
**Result:** ❌ Permission denied on `/tmp/manualai/*`  
**Learning:** `/tmp` isn't always writable in containerized environments

### Iteration 2: Use `/app` Directory
**Attempt:** Fallback to `/app/.manualai/*`  
**Result:** ❌ Permission denied  
**Learning:** `WORKDIR /app` doesn't guarantee subdirectory write access

### Iteration 3: chmod 777 Everything
**Attempt:** Added `RUN chmod -R 777 /tmp/manualai` to Dockerfile  
**Result:** ❌ HuggingFace Spaces ignores chmod at build time  
**Learning:** Runtime permissions override build-time permissions

### Iteration 4: `Path.home()` Fallback
**Attempt:** Use `Path.home() / ".manualai"`  
**Result:** ❌ `Path.home()` returned `"/"` (root)  
**Learning:** Containers may not have HOME environment variable set

### Iteration 5: **tempfile.mkdtemp()** ✅
**Attempt:** Use Python's tempfile module  
**Result:** ✅ WORKS! Creates unique temp dirs with guaranteed permissions  
**Learning:** Standard library solutions > custom path logic

### Iteration 6: NLTK Permission Error 🔄
**Attempt:** Set `NLTK_DATA` env var after pip install  
**Result:** ❌ `unstructured` library ignores it at runtime  
**Current Fix:** Set env vars BEFORE RUN commands in Dockerfile  
**Status:** Testing now...

---

## 💡 Key Insights

### 1. **Always Use tempfile for Ephemeral Storage**
```python
import tempfile
from pathlib import Path

# ❌ DON'T: Assume paths are writable
upload_dir = Path("/tmp/uploads")
upload_dir.mkdir(parents=True, exist_ok=True)

# ✅ DO: Use tempfile.mkdtemp()
upload_dir = Path(tempfile.mkdtemp(prefix="uploads_"))
# Guaranteed to work on any platform!
```

### 2. **Docker ENV Order Matters**
```dockerfile
# ❌ WRONG ORDER
RUN pip install unstructured
ENV NLTK_DATA=/tmp/nltk_data

# ✅ CORRECT ORDER
ENV NLTK_DATA=/tmp/nltk_data
RUN pip install unstructured
RUN python -c "import nltk; nltk.download('punkt')"
```

### 3. **Test Write Permissions, Don't Assume**
```python
def ensure_writable(path: Path) -> bool:
    try:
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True
    except (PermissionError, OSError):
        return False
```

### 4. **Fallback Chains Are Essential**
```python
def get_storage_dir():
    attempts = [
        Path("/tmp/app/storage"),          # Ideal
        Path("/app/storage"),               # App directory
        Path.cwd() / "storage",             # Current dir
        Path(tempfile.gettempdir()) / "storage",  # System temp
        Path(tempfile.mkdtemp(prefix="storage_"))  # Nuclear option
    ]
    
    for attempt in attempts:
        if ensure_writable(attempt):
            return attempt
```

### 5. **Lazy Imports Save Startup Time**
```python
# ❌ DON'T: Import heavy libraries at module level
from unstructured.partition.pdf import partition_pdf  # Slow!

# ✅ DO: Import when actually needed
def load_document(path):
    from unstructured.partition.pdf import partition_pdf  # Fast startup
    return partition_pdf(path)
```

---

## 🛠️ The Final Solution

### Directory Creation (main.py):
```python
def _ensure_directory(path: Path, description: str) -> Path:
    import tempfile
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
        return path
    except (PermissionError, OSError):
        # Try multiple fallbacks
        for fallback in [Path("/app") / path.name, Path.cwd() / path.name]:
            try:
                fallback.mkdir(parents=True, exist_ok=True)
                test_file = fallback / ".write_test"
                test_file.touch()
                test_file.unlink()
                return fallback
            except:
                continue
        
        # Nuclear option: always works
        return Path(tempfile.mkdtemp(prefix=f"manualai_{path.name}_"))
```

### Dockerfile Setup:
```dockerfile
# Set all env vars FIRST
ENV NLTK_DATA=/tmp/manualai/nltk_data \
    HF_HOME=/tmp/manualai/hf_cache \
    MPLCONFIGDIR=/tmp/matplotlib

# Install packages (will respect env vars)
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download data at build time
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger_eng')"

# Startup check script
CMD python startup.py && uvicorn main:app --host 0.0.0.0 --port 7860
```

---

## 📊 Metrics

- **Iterations:** 6
- **Time spent:** ~2 hours
- **Lines changed:** ~150
- **Coffee consumed:** ☕☕☕
- **Lessons learned:** Priceless

---

## ✅ Success Criteria Met:

- [x] Upload endpoint working (202 status)
- [x] File storage working (tempfile.mkdtemp)
- [x] Background worker starting
- [⏳] Document loading (NLTK fix deploying)
- [ ] Vector store creation
- [ ] RAG chain functioning
- [ ] LLM integration

---

## 🚀 What's Next After This Works:

1. **Test with real PDF manual**
2. **Verify LLM responses** (Phi-3-mini integration)
3. **Update frontend** to point to new Space
4. **Add error handling** for better user experience
5. **Improve logging** for easier debugging
6. **Document the deployment** process
7. **Write user guide** for the application

---

## 💬 Advice for Future Me:

1. **Start with tempfile.mkdtemp()** - Don't assume any path is writable
2. **Set env vars before RUN commands** - Order matters in Dockerfiles!
3. **Test permissions explicitly** - mkdir() success doesn't mean write access
4. **Use lazy imports** - Speeds up startup dramatically
5. **Log everything** - You'll thank yourself during debugging
6. **Read HuggingFace Spaces docs** - They have gotchas specific to their platform
7. **Keep calm** - Docker permission issues are solvable! 🧘

---

**Status:** Waiting for final NLTK fix to deploy...  
**ETA:** ~5 minutes  
**Confidence:** 95% this will work! 🤞

---

*"In retrospect, we should have used tempfile from the start. But hey, now we're Docker permission experts!"* 😅
