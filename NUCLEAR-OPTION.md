# 🔥 NUCLEAR OPTION: Delete & Recreate Space

After hours of fighting Docker layer cache, here's the guaranteed solution:

## Why This Will Work

- Your GitHub repo has ALL the correct fixes
- HuggingFace Spaces can auto-sync from GitHub
- Deleting and recreating = guaranteed fresh Docker build
- No cached `.pyc` files, no cached Docker layers

## Steps to Fix (5 minutes)

### 1. Delete Current Space

1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings
2. Scroll to bottom
3. Click **"Delete this Space"**
4. Confirm deletion

### 2. Create New Space Linked to GitHub

1. Go to: https://huggingface.co/new-space
2. Fill in:
   - **Name:** `ManualAi`
   - **Owner:** `agapemiteu`
   - **SDK:** Docker
   - **Hardware:** CPU basic (free)
   - **Visibility:** Public
3. Under **"Files and versions"**, click **"Import from Git repository"**
4. Enter: `https://github.com/agapemiteu/ManualAi`
5. Select branch: `main`
6. In "Path in repo", enter: `hf-space`
7. Click **"Create Space"**

### 3. Configure Environment Variables

After the Space is created, go to Settings and add:

| Variable Name | Value |
|--------------|-------|
| `MANUAL_DISABLE_OCR` | `true` |
| `MANUAL_INGESTION_TIMEOUT` | `120` |
| `MANUALAI_LOG_LEVEL` | `INFO` |
| `OPENAI_API_KEY` | (your OpenAI key) |

### 4. Wait for Build

- First build takes 3-5 minutes
- Watch the build logs in the Space
- Should see: "🚀 Starting ManualAI..."

### 5. Test

```powershell
python test_upload.py
```

Or go to: https://manual-ai-psi.vercel.app/upload

## What's Fixed in the Code

✅ `/tmp` storage (no persistent volume issues)  
✅ Lazy OCR cache initialization (no module-level permission errors)  
✅ 120s timeout protection  
✅ Force delete capability  
✅ OCR disable option

## Alternative: Manual Fix via HF Web Editor

If you don't want to delete/recreate:

1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/tree/main
2. Click on `document_loader.py`
3. Click "Edit"
4. Find line 42 (the problematic `_OCR_CACHE_DIR.mkdir(...)`)
5. Replace lines 40-50 with the lazy initialization code from our GitHub repo
6. Commit with message: "Fix: Lazy OCR cache init"
7. Wait for rebuild

But honestly, **deleting and recreating is cleaner**.

## Why the Factory Rebuild Didn't Work

- Factory rebuild clears persistent storage
- But Docker still uses cached image layers
- Our code changes the INSIDE of files
- Docker only rebuilds if file timestamps change
- Even changing requirements.txt didn't force enough cache busting

**Solution:** Fresh Space = fresh everything.

## Expected Result

After recreation:
- Manual upload completes in ~30 seconds
- No permission errors
- No `.pyc` cache issues
- Clean logs showing "OCR DISABLED - text-only mode"

## Need Help?

If it still doesn't work after recreation, the issue is in the code itself (not cache), and we can debug from clean logs.
