# 🔴 FACTORY REBOOT REQUIRED

## Current Situation:

✅ **All code is deployed** to HuggingFace  
❌ **Space is using cached Docker image** (old build)  
🔧 **Solution:** Factory Reboot to force complete rebuild

---

## Why Factory Reboot?

HuggingFace Spaces **caches Docker layers** for faster rebuilds. Our Dockerfile changes are in the repo, but the Space is still using the old cached image that doesn't have:
- NLTK_DATA env var set before RUN commands
- Pre-downloaded NLTK packages

A Factory Reboot **clears all caches** and rebuilds from scratch.

---

## How to Factory Reboot:

### Option 1: Via Web UI (Recommended)
1. Go to: https://huggingface.co/spaces/Agapemiteu/ManualAi/settings
2. Scroll down to **"Factory Reboot"** section
3. Click **"Reboot this Space"** button
4. Confirm the action
5. Wait ~5 minutes for complete rebuild

### Option 2: Delete and Recreate Space
(Only if Factory Reboot doesn't work)
1. Go to Settings → Delete Space
2. Create new Space with same name
3. Push code again

---

## After Factory Reboot:

The Space will:
1. ✅ Clear all Docker caches
2. ✅ Pull latest code from git
3. ✅ Rebuild Docker image from scratch
4. ✅ Set NLTK_DATA env var correctly
5. ✅ Download NLTK packages during build
6. ✅ Start the application

Then test with:
```powershell
python test_upload.py
```

---

## Expected Success Output:

```
✅ Upload directory (temp): /tmp/manualai_uploads_XXXXX
✅ Storage directory (temp): /tmp/manualai_manual_store_XXXXX
[INFO] Manual smoke-test: background ingestion started
[INFO] document_loader: Loading manual from ...
[INFO] vector_store: Building vector store...
[INFO] main: Manual smoke-test: ingestion complete, status=ready
```

Then check manual status:
```powershell
Invoke-WebRequest "https://agapemiteu-manualai.hf.space/api/manuals"
```

Should show:
```json
{
  "manuals": [{
    "manual_id": "smoke-test",
    "status": "ready",  ← This!
    ...
  }]
}
```

---

## Alternative: Quick Fix Script

If you have the HuggingFace API token, I can create a script to trigger reboot via API. But the web UI is simpler for now.

---

**ACTION REQUIRED:** Please go to the Space settings and click "Factory Reboot"! 🔄

Link: https://huggingface.co/spaces/Agapemiteu/ManualAi/settings
