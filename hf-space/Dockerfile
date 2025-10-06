FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for document processing and OCR
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Create writable directories in /tmp (always writable, no persistent storage issues)
RUN mkdir -p /tmp/manualai/uploads /tmp/manualai/manual_store /tmp/manualai/nltk_data /tmp/manualai/hf_cache /tmp/matplotlib

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data needed by unstructured
RUN python -c "import nltk; nltk.download('punkt', download_dir='/tmp/manualai/nltk_data'); nltk.download('averaged_perceptron_tagger_eng', download_dir='/tmp/manualai/nltk_data')"

# Set all cache directories to /tmp to avoid permission issues
ENV NLTK_DATA=/tmp/manualai/nltk_data \
    HF_HOME=/tmp/manualai/hf_cache \
    TRANSFORMERS_CACHE=/tmp/manualai/hf_cache \
    SENTENCE_TRANSFORMERS_HOME=/tmp/manualai/hf_cache \
    HUGGINGFACE_HUB_CACHE=/tmp/manualai/hf_cache \
    MPLCONFIGDIR=/tmp/matplotlib

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# Set environment variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application with cache cleanup
CMD ["./start.sh"]
