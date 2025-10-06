from huggingface_hub import HfApi

api = HfApi()

print("Uploading requirements.txt to force Docker cache bust...")
api.upload_file(
    path_or_fileobj='hf-space/requirements.txt',
    path_in_repo='requirements.txt',
    repo_id='agapemiteu/ManualAi',
    repo_type='space',
    commit_message='Force Docker rebuild: Update timestamp in requirements.txt'
)

print("✅ Uploaded - This will force Docker to rebuild from scratch")
print("\nSpace will rebuild in 2-3 minutes with fresh code...")
