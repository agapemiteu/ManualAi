#!/usr/bin/env python3
"""Upload files directly to HuggingFace Space using the Hub API"""
from huggingface_hub import HfApi
import os

api = HfApi()
SPACE_ID = "agapemiteu/ManualAi"

print("=" * 70)
print("📤 UPLOADING FILES TO HUGGINGFACE SPACE")
print("=" * 70)

# Files to upload from hf-space directory
files_to_upload = [
    "hf-space/main.py",
    "hf-space/document_loader.py",
    "hf-space/vector_store.py",
    "hf-space/rag_chain.py",
    "hf-space/requirements.txt",
    "hf-space/Dockerfile",
    "hf-space/README.md"
]

for file_path in files_to_upload:
    if os.path.exists(file_path):
        # Upload to root of Space (remove hf-space/ prefix)
        path_in_repo = file_path.replace("hf-space/", "")
        print(f"\n📤 Uploading: {file_path} -> {path_in_repo}")
        
        try:
            api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=path_in_repo,
                repo_id=SPACE_ID,
                repo_type="space",
                commit_message=f"Fix: Update {path_in_repo} with permission fixes"
            )
            print(f"   ✅ Uploaded successfully")
        except Exception as e:
            print(f"   ❌ Upload failed: {e}")
    else:
        print(f"\n⚠️  File not found: {file_path}")

print("\n" + "=" * 70)
print("✅ UPLOAD COMPLETE - Space will rebuild automatically")
print("=" * 70)
