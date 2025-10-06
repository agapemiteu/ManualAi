# Critical Fixes Applied - ManualAI

## Date: October 6, 2025

## Problems Solved

### 1. **Stuck Manual Processing Jobs** ✅
**Problem:** The `owner-manual` job was stuck in "processing" state indefinitely, blocking all new uploads with the same ID.

**Solution:** 
- Added `force` parameter to DELETE endpoint
- Modified `remove_manual()` to forcefully remove stuck jobs
- Jobs can now be force-deleted even while processing

**How to Use:**
```bash
# Force delete a stuck manual
curl -X DELETE "https://agapemiteu-manualai.hf.space/api/manuals/owner-manual?force=true"
```

Or from JavaScript/Frontend:
```javascript
await fetch(`${API_URL}/api/manuals/${manualId}?force=true`, {
  method: 'DELETE'
});
```

### 2. **Ingestion Timeout** ✅
**Problem:** Background ingestion tasks could hang forever, especially with OCR on free CPU tier.

**Solution:**
- Added `MANUAL_INGESTION_TIMEOUT` environment variable (default: 180 seconds / 3 minutes)
- Background worker now runs in a thread with timeout protection
- Jobs automatically fail after timeout with helpful error message
- Grace period (5s) for cleanup before force removal

**Configuration:**
```bash
# In .env or environment variables
MANUAL_INGESTION_TIMEOUT=180  # 3 minutes default (adjust as needed)
```

**Error Message When Timeout Occurs:**
```
Processing timeout after 180s. PDF too complex for free tier. 
Try: 1) Force delete this job, 2) Use text-only PDF, or 3) Set MANUAL_DISABLE_OCR=true
```

### 3. **OCR Disable Option** ✅
**Problem:** OCR processing on HuggingFace free CPU tier takes 5-10+ minutes or hangs completely.

**Solution:**
- Added `MANUAL_DISABLE_OCR` environment variable
- When enabled, skips all OCR processing
- Only extracts text that's already embedded in PDFs
- Dramatically faster processing (<30 seconds for text PDFs)

**Configuration:**
```bash
# In .env or environment variables
MANUAL_DISABLE_OCR=true  # or "1", "yes"
```

**What This Does:**
- ✅ Extracts embedded text from PDFs (fast)
- ❌ Skips Tesseract OCR (slow/hanging)
- ⚡ Processing time: ~30 seconds vs 5-10+ minutes
- ⚠️  Image-only pages will be empty (but won't hang)

### 4. **Replace Processing Manuals** ✅
**Problem:** Couldn't replace a manual that was stuck in processing state.

**Solution:**
- Modified `register_manual()` to allow replacing processing jobs
- Cancels in-flight processing before starting new upload
- Cleans up resources properly

## Usage Examples

### Scenario 1: Clear a Stuck Job
```bash
# Check status
curl https://agapemiteu-manualai.hf.space/api/manuals/owner-manual

# Force delete if stuck
curl -X DELETE "https://agapemiteu-manualai.hf.space/api/manuals/owner-manual?force=true"

# Upload new manual
curl -X POST "https://agapemiteu-manualai.hf.space/api/manuals" \
  -F "file=@/path/to/manual.pdf" \
  -F "brand=Toyota" \
  -F "manual_id=owner-manual" \
  -F "replace=true"
```

### Scenario 2: Fast Text-Only Processing
```bash
# Set environment variable on HuggingFace Space
MANUAL_DISABLE_OCR=true

# Or in .env.local for local development
echo "MANUAL_DISABLE_OCR=true" >> .env.local

# Now uploads process in ~30 seconds instead of 5+ minutes
```

### Scenario 3: Adjust Timeout for Large Manuals
```bash
# Increase timeout to 5 minutes for larger PDFs
MANUAL_INGESTION_TIMEOUT=300

# Or decrease to 2 minutes if you want faster failures
MANUAL_INGESTION_TIMEOUT=120
```

## Environment Variables Summary

| Variable | Default | Description |
|----------|---------|-------------|
| `MANUAL_INGESTION_TIMEOUT` | `180` | Timeout in seconds before auto-failing jobs |
| `MANUAL_DISABLE_OCR` | `false` | Set to `true` to skip OCR (text-only mode) |
| `MANUAL_OCR_TIMEOUT` | `12.0` | Per-page OCR timeout (if OCR enabled) |
| `MANUAL_OCR_WORKERS` | `auto` | Number of parallel OCR workers |
| `MANUAL_OCR_DPI` | `170` | OCR image resolution (lower = faster) |

## API Changes

### DELETE /api/manuals/{manual_id}
**New Query Parameter:** `force` (boolean, default: false)

```javascript
// Regular delete (won't delete if processing)
DELETE /api/manuals/my-manual

// Force delete (removes even if processing)
DELETE /api/manuals/my-manual?force=true
```

### POST /api/manuals
**Enhanced Behavior:**
- Now allows `replace=true` even if manual is processing
- Automatically cancels in-flight processing
- Cleans up resources before starting new upload

## Frontend Changes (Already Applied)

The frontend (`app/upload/page.tsx`) already has:
- ✅ Upload cancellation support
- ✅ 45-second upload timeout
- ✅ Better error messages
- ✅ Cancel button functionality

## Deployment Checklist

### For HuggingFace Space:
1. ✅ Push updated `hf-space/main.py`
2. ✅ Push updated `hf-space/document_loader.py`
3. ⚙️  Set environment variable: `MANUAL_DISABLE_OCR=true` (recommended for free tier)
4. ⚙️  Optional: Adjust `MANUAL_INGESTION_TIMEOUT` if needed
5. 🔄 Restart the Space
6. 🗑️  Force delete any stuck manuals via API

### For Vercel Frontend:
1. ✅ Frontend changes already in `app/upload/page.tsx`
2. ✅ No additional deployment needed
3. ✔️  Test upload/cancel functionality

## Testing

### 1. Test Force Delete
```bash
# Create a test upload
curl -X POST "https://agapemiteu-manualai.hf.space/api/manuals" \
  -F "file=@test.pdf" \
  -F "brand=Test" \
  -F "manual_id=test-manual"

# Force delete it
curl -X DELETE "https://agapemiteu-manualai.hf.space/api/manuals/test-manual?force=true"

# Verify it's gone
curl "https://agapemiteu-manualai.hf.space/api/manuals/test-manual"
# Should return 404
```

### 2. Test OCR Disable
```bash
# Set MANUAL_DISABLE_OCR=true in HF Space settings

# Upload a text PDF
curl -X POST "https://agapemiteu-manualai.hf.space/api/manuals" \
  -F "file=@text-only.pdf" \
  -F "brand=Test"

# Should complete in ~30 seconds
# Check logs: should see "OCR DISABLED - text-only mode"
```

### 3. Test Timeout
```bash
# Set MANUAL_INGESTION_TIMEOUT=30 (30 seconds)

# Upload a complex PDF
curl -X POST "https://agapemiteu-manualai.hf.space/api/manuals" \
  -F "file=@complex.pdf" \
  -F "brand=Test"

# After 30 seconds, should auto-fail with timeout error
# Check status - should show FAILED with timeout message
```

## Logs & Monitoring

Check processing logs:
```bash
curl "https://agapemiteu-manualai.hf.space/api/system/logs?limit=100"
```

Look for:
- `"Manual X: background ingestion started (timeout=180s, ocr_disabled=true)"`
- `"Manual X: OCR DISABLED - text-only mode"`
- `"Manual X: TIMEOUT after 180s - forcing failure"`
- `"Manual X: FORCE removing stuck job"`

## Recommended Settings for Free Tier

```bash
# .env or HuggingFace Space Settings
MANUAL_DISABLE_OCR=true          # Skip OCR completely
MANUAL_INGESTION_TIMEOUT=120     # 2 minute timeout
MANUALAI_LOG_LEVEL=INFO          # Detailed logging
```

With these settings:
- ✅ Text PDFs process in ~30 seconds
- ✅ Stuck jobs auto-fail after 2 minutes
- ✅ Can force-delete failed jobs
- ✅ No more indefinite hangs

## Next Steps

1. **Immediate Action:** Force delete the stuck `owner-manual`:
   ```bash
   curl -X DELETE "https://agapemiteu-manualai.hf.space/api/manuals/owner-manual?force=true"
   ```

2. **Enable Fast Mode:** Set `MANUAL_DISABLE_OCR=true` on HF Space

3. **Test Upload:** Try uploading a text-only PDF

4. **Monitor Logs:** Check `/api/system/logs` endpoint

## Files Modified

- ✅ `hf-space/main.py` - Added timeout, force delete, OCR disable
- ✅ `hf-space/document_loader.py` - Added OCR skip logic, helper functions
- ℹ️  `app/upload/page.tsx` - Already had cancel/timeout (no new changes needed)
- ℹ️  `api/main.py` - Has same changes as hf-space/main.py (keep in sync)

## Support

If issues persist:
1. Check logs: `/api/system/logs`
2. Force delete stuck jobs: `?force=true`
3. Try OCR disable: `MANUAL_DISABLE_OCR=true`
4. Reduce timeout: `MANUAL_INGESTION_TIMEOUT=60`
