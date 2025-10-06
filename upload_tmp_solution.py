from huggingface_hub import HfApi

api = HfApi()
SPACE_ID = "agapemiteu/ManualAi"

files_to_upload = [
    ("hf-space/main.py", "main.py"),
    ("hf-space/document_loader.py", "document_loader.py"),
    ("hf-space/Dockerfile", "Dockerfile"),
    ("hf-space/start.sh", "start.sh"),
    ("hf-space/requirements.txt", "requirements.txt"),
]

print("=" * 70)
print("📤 UPLOADING /tmp STORAGE SOLUTION TO HUGGINGFACE")
print("=" * 70)

for local_path, remote_path in files_to_upload:
    print(f"\nUploading: {remote_path}")
    api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=remote_path,
        repo_id=SPACE_ID,
        repo_type="space"
    )
    print(f"  ✅ Done")

print("\n" + "=" * 70)
print("✅ ALL FILES UPLOADED")
print("=" * 70)
print("\n⚠️  IMPORTANT: Now delete persistent storage:")
print("1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings")
print("2. Find 'Storage' or 'Persistent Storage' section")
print("3. Click 'Delete storage' or 'Factory reboot'")
print("4. Space will rebuild with /tmp storage (no cache issues!)")
print("\n✨ After deletion, ingestion will work in ~30 seconds!")
