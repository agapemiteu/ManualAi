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
    && rm -rf /var/lib/apt/lists/*

# Prepare writable directories
RUN mkdir -p /data/manualai/uploads /data/manualai/manual_store /data/manualai/nltk_data /data/manualai/hf_cache \
    && chmod -R 777 /data/manualai

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data needed by unstructured
RUN python -c "import nltk; nltk.download('punkt', download_dir='/data/manualai/nltk_data'); nltk.download('averaged_perceptron_tagger_eng', download_dir='/data/manualai/nltk_data')"

ENV NLTK_DATA=/data/manualai/nltk_data \
    HF_HOME=/data/manualai/hf_cache \
    TRANSFORMERS_CACHE=/data/manualai/hf_cache \
    SENTENCE_TRANSFORMERS_HOME=/data/manualai/hf_cache \
    HUGGINGFACE_HUB_CACHE=/data/manualai/hf_cache

# Copy application code
COPY . .

# Expose port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# Set environment variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
