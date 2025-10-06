from huggingface_hub import HfApi

api = HfApi()

print("Uploading start.sh...")
api.upload_file(
    path_or_fileobj="hf-space/start.sh",
    path_in_repo="start.sh",
    repo_id="agapemiteu/ManualAi",
    repo_type="space"
)

print("Uploading Dockerfile...")
api.upload_file(
    path_or_fileobj="hf-space/Dockerfile",
    path_in_repo="Dockerfile",
    repo_id="agapemiteu/ManualAi",
    repo_type="space",
    commit_message="Fix: Clean bytecode cache on startup to force fresh imports"
)

print("✅ Uploaded - Space will rebuild")
