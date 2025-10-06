from huggingface_hub import HfApi

api = HfApi()
api.upload_file(
    path_or_fileobj='hf-space/document_loader.py',
    path_in_repo='document_loader.py',
    repo_id='agapemiteu/ManualAi',
    repo_type='space',
    commit_message='FINAL FIX: Lazy init OCR cache to bypass .pyc cache'
)
print('✅ Uploaded - Space will rebuild')
