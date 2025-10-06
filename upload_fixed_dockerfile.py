from huggingface_hub import HfApi

api = HfApi()
api.upload_file(
    path_or_fileobj='hf-space/Dockerfile',
    path_in_repo='Dockerfile',
    repo_id='agapemiteu/ManualAi',
    repo_type='space',
    commit_message='Fix: Remove startup script, use direct uvicorn command'
)
print('✅ Uploaded fixed Dockerfile - Space will rebuild')
