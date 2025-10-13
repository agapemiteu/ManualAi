# Upload Guidelines

## File Size Limits

| Size | Status | Processing Time | Recommendation |
|------|--------|----------------|----------------|
| **< 10MB** | ✅ Ideal | 1-3 minutes | **Recommended** - Fast and reliable |
| **10-20MB** | ⚠️ Warning | 3-5 minutes | May take longer but should work |
| **> 20MB** | ❌ Blocked | N/A | Rejected - Too large for current deployment |

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

The full 2023 Toyota 4Runner manual is **12.4MB (608 pages)** - works great!

**Upload options:**
- **Full manual**: Upload all 608 pages (~12MB) - now supported!
- **Extract sections**: For faster processing, extract key sections
  - Safety & Warnings: Pages 1-50 (~500KB)
  - Maintenance Schedule: Pages 540-560 (~200KB)  
  - Troubleshooting: Pages 485-515 (~300KB)

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

The deployment has:
- ⏱️ **Processing capacity** optimized for up to 20MB files
- 💾 **Memory allocation** sufficient for most manuals
- ⌛ **Request timeouts** (5 minutes for upload, background processing continues)

Large manuals (10-20MB) will:
- Take 3-5 minutes to process
- Work reliably in the background
- Be ready for queries once processing completes

## For Even Larger Files

For manuals over 20MB:
- **Local deployment**: No limits, fastest processing
- **Extract sections**: Focus on relevant chapters
- **Compress PDF**: Use online tools to reduce size

## Summary

🎯 **Sweet Spot**: Under 10MB - Fast and reliable  
✅ **Works Great**: Up to 20MB - More processing time but still works  
🚀 **Best Demo**: Full car manuals (600+ pages) now supported!  

---

For the full 608-page Toyota 4Runner manual, download from:
https://github.com/agapemiteu/ManualAi/tree/main/data

Then extract the sections you need!
