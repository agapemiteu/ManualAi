# Upload Guidelines for Free Tier

## File Size Limits

| Size | Status | Processing Time | Recommendation |
|------|--------|----------------|----------------|
| **< 2MB** | ✅ Ideal | 30-60 seconds | **Recommended** - Fast and reliable |
| **2-5MB** | ⚠️ Warning | 2-5 minutes | May work, but could timeout |
| **> 5MB** | ❌ Blocked | N/A | Rejected - Too large for free tier |

## How to Reduce PDF Size

### Option 1: Extract Specific Sections
If you have a large manual (e.g., 600 pages), extract only relevant sections:

**Using Adobe Acrobat:**
1. Open PDF
2. Tools → Organize Pages
3. Select pages you need (e.g., pages 1-50)
4. Extract → Save as new PDF

**Using Free Tools:**
- **PDF24**: https://tools.pdf24.org/en/extract-pages
- **iLovePDF**: https://www.ilovepdf.com/split_pdf
- **Smallpdf**: https://smallpdf.com/split-pdf

### Option 2: Compress the PDF

**Online Tools:**
- **iLovePDF**: https://www.ilovepdf.com/compress_pdf
- **Smallpdf**: https://smallpdf.com/compress-pdf
- **PDF Compressor**: https://www.pdfcompressor.com/

**Offline Tools:**
- **Adobe Acrobat**: File → Save As Other → Reduced Size PDF
- **Preview (Mac)**: File → Export → Reduce File Size

## Example: Toyota 4Runner Manual

The full 2023 Toyota 4Runner manual is **12.4MB (608 pages)** - too large for free tier.

**Recommended extraction strategy:**
- Safety & Warnings: Pages 1-50 (~500KB)
- Maintenance Schedule: Pages 540-560 (~200KB)  
- Troubleshooting: Pages 485-515 (~300KB)
- Total: ~1MB - perfect for testing!

## What Works Best

✅ **Good file types:**
- Text-based PDFs (searchable)
- HTML documentation
- Plain text files

⚠️ **Slower processing:**
- Image-heavy PDFs (requires OCR)
- Scanned documents
- Complex formatting

❌ **Not supported:**
- Encrypted PDFs
- Password-protected files
- Corrupted documents

## Testing Locally (No Limits)

Want to test with larger files? Run locally:

```bash
# Clone the repo
git clone https://github.com/agapemiteu/ManualAi.git
cd ManualAi

# Start backend (handles large files fine)
cd api
python -m uvicorn main:app --reload

# In another terminal, start frontend
cd ..
npm install
npm run dev
```

Local setup has **NO size limits** and processes files much faster!

## Why These Limits?

The free tier deployment on HuggingFace has:
- ⏱️ **Limited CPU time** for processing
- 💾 **Limited memory** for embeddings
- ⌛ **Request timeouts** (5 minutes max)

Large manuals require:
- Text extraction (OCR for images)
- Embedding generation (all pages)
- Vector store building

This can easily exceed free tier capabilities.

## Pro Tier Alternative

For production use with large manuals:
- **HuggingFace Pro**: $9/month - More resources, longer timeouts
- **Local deployment**: No limits, fastest processing
- **Dedicated server**: Full control

## Summary

🎯 **Sweet Spot**: 20-50 page PDFs (1-2MB)  
✅ **Works Great**: Fast processing, reliable results  
🚀 **Best Demo**: Shows off the system without timeouts  

---

For the full 608-page Toyota 4Runner manual, download from:
https://github.com/agapemiteu/ManualAi/tree/main/data

Then extract the sections you need!
