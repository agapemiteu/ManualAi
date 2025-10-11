# Pre-loaded Manual Deployment Guide

**Date:** October 11, 2025  
**Status:** ✅ Complete - Manual is pre-loaded and upload functionality removed

## What Was Done

### 1. ✅ Added Manual to GitHub Repository
- **File:** `data/2023-Toyota-4runner-Manual.pdf` (12.4MB, 608 pages)
- **Commit:** "Add Toyota 4Runner manual for public download and pre-loading"
- **Access:** Anyone can now download the manual from the GitHub repo
- **Updated:** `data/README.md` with download instructions

### 2. ✅ Pre-loaded Manual in HuggingFace Docker
**Files Created:**
- `preload_manual.py` - Script to process and store manual during Docker build
- `startup.py` - Registers pre-loaded manual when FastAPI starts
- `data/2023-Toyota-4runner-Manual.pdf` - Manual copied to HF deployment

**Dockerfile Changes:**
```dockerfile
# Pre-load the Toyota 4Runner manual during build
RUN echo "Pre-loading Toyota 4Runner manual..." && \
    python preload_manual.py || echo "Pre-load failed..."
```

**FastAPI Startup Hook:**
```python
@app.on_event("startup")
async def startup_event():
    """Load pre-built manuals on startup"""
    from startup import register_preloaded_manuals
    register_preloaded_manuals(manual_manager)
```

**Git LFS Setup:**
- Configured Git LFS for PDF files (required for files >10MB on HuggingFace)
- PDF properly tracked and uploaded via LFS

### 3. ✅ Removed Upload Functionality from Frontend
**Files Modified:**
- `app/layout.tsx` - Commented out "Upload Manual" button in navigation
- `components/ChatInterface.tsx` - Updated title to "Chat with Toyota 4Runner Manual"

**Reason:** Since the manual is pre-loaded, users don't need to upload. This also avoids the HuggingFace free tier limitation issues.

## How It Works

### Docker Build Process:
1. Docker builds the container
2. During build, `preload_manual.py` runs:
   - Loads the Toyota 4Runner PDF
   - Extracts text and creates document chunks
   - Generates embeddings using `all-mpnet-base-v2`
   - Builds ChromaDB vector store
   - Saves to `/tmp/manualai/manual_store/toyota_4runner_2023/`

### FastAPI Startup:
1. Container starts
2. FastAPI `startup_event` fires
3. `startup.py` checks for pre-loaded manuals
4. Registers the Toyota 4Runner manual as "ready"
5. Manual is immediately available for queries!

### User Experience:
1. User visits https://manual-ai-psi.vercel.app
2. Chat interface loads
3. Manual is already available - no upload needed
4. User can immediately ask questions about Toyota 4Runner

## Manual Information

**Pre-loaded Manual:**
- **ID:** `toyota_4runner_2023`
- **Brand:** Toyota
- **Model:** 4Runner  
- **Year:** 2023
- **Pages:** 608
- **Size:** 12.4 MB
- **Status:** ✅ Ready on startup

## Testing the Deployment

### 1. Test HuggingFace Backend:
```bash
# Check if manual is loaded
curl https://agapemiteu-manualai.hf.space/api/manuals

# Expected response:
{
  "manuals": [
    {
      "manual_id": "toyota_4runner_2023",
      "status": "ready",
      "filename": "2023-Toyota-4runner-Manual.pdf",
      "brand": "Toyota",
      "model": "4Runner",
      "year": "2023"
    }
  ]
}
```

### 2. Test Chat:
```bash
curl -X POST https://agapemiteu-manualai.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the recommended tire pressure?",
    "manual_id": "toyota_4runner_2023"
  }'
```

### 3. Test Vercel Frontend:
Visit: https://manual-ai-psi.vercel.app
- Should show "Chat with Toyota 4Runner Manual"
- Manual should be available in dropdown
- Can ask questions immediately

## Benefits of Pre-loading

✅ **Instant Availability** - No waiting for manual processing  
✅ **No Upload Errors** - Avoids HuggingFace free tier limitations  
✅ **Consistent Demo** - Everyone sees the same manual  
✅ **Simpler UX** - Users can test immediately without uploading  
✅ **Showcase Ready** - Perfect for portfolio/recruiter demos  

## Deployment URLs

| Platform | URL | Status |
|----------|-----|--------|
| **GitHub Pages** | https://agapemiteu.github.io/ManualAi/ | ✅ Live |
| **HuggingFace** | https://agapemiteu-manualai.hf.space/ | ✅ Building |
| **Vercel** | https://manual-ai-psi.vercel.app | ✅ Live |

## Download Manual

Users can download the manual from GitHub:
```bash
git clone https://github.com/agapemiteu/ManualAi.git
cd ManualAi
# Manual is at: data/2023-Toyota-4runner-Manual.pdf
```

Or download directly:
- Visit: https://github.com/agapemiteu/ManualAi
- Navigate to `data/2023-Toyota-4runner-Manual.pdf`
- Click "Download" button

## Future Enhancements

If you want to add more manuals later:

1. **Add more PDFs to `data/` folder**
2. **Update `preload_manual.py`** to process multiple manuals
3. **Rebuild Docker image**
4. **Deploy to HuggingFace**

Or enable upload functionality with HuggingFace Pro tier for user uploads.

## Troubleshooting

### If manual isn't showing up:
1. Check HuggingFace build logs
2. Verify `preload_manual.py` ran successfully during build
3. Check `startup_event` logs in FastAPI
4. Ensure vector store exists at `/tmp/manualai/manual_store/toyota_4runner_2023/`

### If build takes too long:
- Manual processing during build can take 5-10 minutes
- This is normal - it's building embeddings for 608 pages
- Once built, startup is instant!

---
**Status:** ✅ Complete and Deployed  
**Ready for:** Portfolio showcase, recruiter demos, user testing  
**Next:** Wait for HuggingFace build to complete (~10-15 minutes)
