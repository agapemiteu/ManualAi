#!/bin/sh
# Startup script for ManualAI

echo "🚀 Starting ManualAI..."
echo "📁 Using /tmp for all storage (no persistent volume issues)"
echo "📊 Storage dir: ${MANUAL_STORAGE_DIR:-/tmp/manualai/manual_store}"
echo "📤 Upload dir: ${MANUAL_UPLOAD_DIR:-/tmp/manualai/uploads}"

# Ensure directories exist
mkdir -p /tmp/manualai/uploads /tmp/manualai/manual_store /tmp/ocr_cache /tmp/matplotlib

echo "✅ Ready!"
exec uvicorn main:app --host 0.0.0.0 --port 7860
