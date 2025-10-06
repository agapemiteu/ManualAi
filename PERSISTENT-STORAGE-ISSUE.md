# 🚨 CRITICAL ISSUE: HuggingFace Spaces Persistent Storage Cache

## THE PROBLEM

Your HuggingFace Space has a **PERSISTENT VOLUME** mounted at `/data` that survives rebuilds. This volume contains:
- Old Python bytecode (`.pyc`) files from previous deployments
- These `.pyc` files are loaded INSTEAD of the source code
- No amount of rebuilding, restarting, or uploading new code fixes this
- Python imports the cached bytecode from `/data/__pycache__/` before reading `/app/document_loader.py`

**Evidence:**
- ✅ Source code on HF Space repo is CORRECT (lines 41-49 have the /tmp fix)
- ✅ Dockerfile is updated with cache cleanup
- ❌ Running container STILL fails at line 42 (the OLD code path)
- ❌ Error shows `/data/manual_store/ocr_cache` (old path) not `/tmp/ocr_cache` (new path)

## THE REAL SOLUTIONS

###  1️⃣ **DELETE PERSISTENT STORAGE (Recommended)**

**Steps:**
1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings
2. Scroll to **"Persistent Storage"** section
3. Click **"Delete persistent storage"** button
4. Confirm deletion
5. Space will rebuild with fresh storage
6. All `.pyc` cache will be gone

**Pros:**
- ✅ Guaranteed to work
- ✅ Clean slate

**Cons:**
- ⚠️ Deletes all uploaded manuals and vector stores
- ⚠️ Manual operation required

### 2️⃣ **MIGRATE TO A NEW SPACE**

**Steps:**
1. Create NEW Space: https://huggingface.co/new-space
2. Name it: `ManualAi-v2`
3. Set SDK: Docker
4. Clone this repo into the new space
5. Configure environment variables:
   - `OPENAI_API_KEY`
   - `MANUAL_DISABLE_OCR=true`
   - `MANUAL_INGESTION_TIMEOUT=120`
   - `MANUALAI_LOG_LEVEL=INFO`
6. Update frontend `NEXT_PUBLIC_API_URL` to new space URL
7. Delete old space

**Pros:**
- ✅ Fresh start, no cache issues
- ✅ Can test before switching

**Cons:**
- ⚠️ Need to reconfigure variables
- ⚠️ Update frontend URL
- ⚠️ More steps

### 3️⃣ **DISABLE OCR COMPLETELY (Workaround)**

Since the permission error is in OCR cache initialization, we can bypass it entirely:

**Change document_loader.py to SKIP OCR module entirely when disabled:**

```python
# At top of file, wrap ALL OCR imports and setup in a conditional
if not os.getenv("MANUAL_DISABLE_OCR", "false").lower() == "true":
    # Only import OCR stuff if enabled
    import pytesseract
    from PIL import Image
    # ... rest of OCR setup
else:
    # Stub out OCR functions
    def _ocr_pdf_fallback(*args, **kwargs):
        return []
```

**Pros:**
- ✅ Bypasses the cache issue
- ✅ You don't need OCR anyway (it's disabled)

**Cons:**
- ⚠️ Major code refactor
- ⚠️ Still doesn't fix root cause

## WHY REBUILDS DON'T WORK

1. **Persistent Volume Survives:**
   - `/data` is mounted as persistent storage
   - Contains old `__pycache__/document_loader.cpython-310.pyc`
   - This file has the OLD path hardcoded in bytecode

2. **Python Import Priority:**
   - Python checks for `.pyc` files FIRST
   - Finds cached bytecode in `/data/__pycache__/`
   - Skips reading the updated source in `/app/`

3. **Docker Cache Doesn't Help:**
   - Dockerfile rebuilds `/app` fresh
   - But `/data` is a separate mounted volume
   - Startup script runs AFTER Python imports modules

## WHAT WE'VE TRIED (ALL FAILED)

❌ Factory reboot  
❌ Multiple rebuilds  
❌ Dockerfile RUN commands to delete cache  
❌ Startup script to clean cache  
❌ `PYTHONDONTWRITEBYTECODE=1` (prevents NEW `.pyc`, doesn't delete OLD ones)  
❌ Environment variable overrides  
❌ Lazy initialization (still imports module with old code at module-level)  
❌ Uploading files directly via Hub API  
❌ Pushing to HF git remote  
❌ Deleting and re-adding environment variables  

## THE ONLY GUARANTEED FIX

**Delete the persistent storage** or **create a new Space**.

This is a known limitation of HuggingFace Spaces with persistent volumes - they can cache Python bytecode that survives deployments.

## RECOMMENDATION

1. **Delete persistent storage** (fastest)
2. Upload one test manual to verify it works
3. If users have important data, migrate to new Space instead

---

**Note:** This is why production systems use:
- Immutable infrastructure (no persistent app code)
- Separate data volumes from code volumes
- Blue/green deployments
- Container orchestration that handles cache invalidation
