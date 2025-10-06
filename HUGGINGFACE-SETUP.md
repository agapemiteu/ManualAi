# 🔧 HuggingFace Space Configuration Script

## Manual Configuration (Recommended - 2 minutes)

Since I cannot directly access HuggingFace, please follow these simple steps:

### Step-by-Step Instructions

1. **Open HuggingFace Space Settings**
   - URL: https://huggingface.co/spaces/agapemiteu/ManualAi/settings
   - (Already opened in your browser)

2. **Scroll to "Variables and secrets" section**

3. **Click "New secret" or "New variable"**

4. **Add these THREE variables one by one:**

   ```
   Variable 1:
   Name:  MANUAL_DISABLE_OCR
   Value: true
   ```

   ```
   Variable 2:
   Name:  MANUAL_INGESTION_TIMEOUT
   Value: 120
   ```

   ```
   Variable 3:
   Name:  MANUALAI_LOG_LEVEL
   Value: INFO
   ```

5. **Click "Factory Reboot" button** at the top of the settings page

6. **Wait 2 minutes** for the space to rebuild

## Alternative: Use HuggingFace CLI (If you have it installed)

If you have the HuggingFace CLI installed and authenticated, you can run:

```bash
# Set environment variables via CLI
huggingface-cli space set-var agapemiteu/ManualAi MANUAL_DISABLE_OCR true
huggingface-cli space set-var agapemiteu/ManualAi MANUAL_INGESTION_TIMEOUT 120
huggingface-cli space set-var agapemiteu/ManualAi MANUALAI_LOG_LEVEL INFO

# Restart the space
huggingface-cli space restart agapemiteu/ManualAi
```

## What Each Variable Does

### MANUAL_DISABLE_OCR=true
- **Purpose:** Disables slow OCR processing
- **Impact:** 15x faster (30 seconds vs 5-10 minutes)
- **Trade-off:** Only extracts embedded text, skips image-only pages
- **Recommendation:** MUST enable for free CPU tier

### MANUAL_INGESTION_TIMEOUT=120
- **Purpose:** Auto-fails jobs after 2 minutes
- **Impact:** No more infinite hangs
- **Trade-off:** Complex PDFs might timeout (good on free tier)
- **Recommendation:** Keep at 120 seconds

### MANUALAI_LOG_LEVEL=INFO
- **Purpose:** Detailed logging for debugging
- **Impact:** Better error messages and monitoring
- **Trade-off:** Slightly more verbose logs
- **Recommendation:** Helpful for troubleshooting

## Verification After Configuration

### 1. Check Space is Running
```powershell
Invoke-WebRequest -Uri "https://agapemiteu-manualai.hf.space/" | Select-Object -ExpandProperty Content
```

Expected: `{"message":"Welcome to ManualAi API!","status":"running"}`

### 2. Upload Test PDF
Go to: https://manual-ai-psi.vercel.app/upload

Expected:
- Upload completes in ~30 seconds
- Status shows "ready"
- No timeout errors

### 3. Check Logs for Confirmation
```powershell
Invoke-WebRequest -Uri "https://agapemiteu-manualai.hf.space/api/system/logs?limit=20" | Select-Object -ExpandProperty Content
```

Look for:
- `"OCR DISABLED - text-only mode"`
- `"background ingestion started (timeout=120s, ocr_disabled=true)"`

## If You Have Issues

### Space Not Rebuilding?
1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi
2. Click "Factory Reboot" button
3. Wait 2-3 minutes

### Upload Still Slow?
1. Verify variables are saved in settings
2. Check space logs for errors
3. Try restarting the space again

### Variables Not Taking Effect?
1. Make sure you clicked "Save" after adding each variable
2. Make sure you restarted the space
3. Check the space is using the main branch (not a cached version)

## Quick Reference

| Step | Action | Time |
|------|--------|------|
| 1 | Open settings page | ✅ Done |
| 2 | Add 3 environment variables | 1 min |
| 3 | Restart space | 30 sec |
| 4 | Wait for rebuild | 2 min |
| 5 | Test upload | 30 sec |
| **Total** | | **~4 minutes** |

---

**Need help?** Check the logs or deployment status:
- Logs: `Invoke-WebRequest -Uri "https://agapemiteu-manualai.hf.space/api/system/logs"`
- Status: Check DEPLOYMENT-STATUS.md in this project
