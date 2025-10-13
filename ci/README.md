# CI/CD Docker Configuration

This folder contains Docker configuration for continuous integration and deployment testing.

## Contents

- `Dockerfile` - Multi-stage Docker build combining Node.js and Python environments

## Purpose

This Dockerfile was created to test deploying the full stack (frontend + backend) in a single container.

## Configuration

The Docker image includes:
- **Node.js 18** - For Next.js frontend
- **Python 3** - For FastAPI backend
- **Poppler** - PDF processing utilities
- **Tesseract** - OCR capabilities (experimental)

## Current Status

⚠️ **Not actively used in production**

Production deployment uses:
- **Frontend**: Vercel (Next.js automatic deployment)
- **Backend**: HuggingFace Spaces (Docker container)
- **Documentation**: GitHub Pages

## Usage

If you want to run the full stack locally in Docker:

```bash
# Build the image
docker build -t manualai-fullstack -f ci/Dockerfile .

# Run the container
docker run -p 3000:3000 -p 8000:8000 manualai-fullstack
```

## Why Keep This?

1. **Local Development** - Option for Docker-based dev environment
2. **Self-Hosting** - Users can deploy full stack themselves
3. **Testing** - CI/CD pipeline testing (future)

## Production Architecture

Current production uses **three separate platforms**:

```
Frontend (Vercel)  →  Backend (HuggingFace)  →  Docs (GitHub Pages)
    Next.js              FastAPI                  Static HTML
```

This separation provides:
- ✅ Free hosting on multiple platforms
- ✅ Independent scaling
- ✅ Clear separation of concerns

---

For production deployment guides, see:
- Main README.md
- PRODUCTION_CASE_STUDY.md (Section 5: Deployment Architecture)
