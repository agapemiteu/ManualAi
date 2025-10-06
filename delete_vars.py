from huggingface_hub import HfApi

api = HfApi()

try:
    api.delete_space_variable('agapemiteu/ManualAi', 'MANUAL_OCR_CACHE_DIR')
    print('✅ Deleted MANUAL_OCR_CACHE_DIR variable')
except Exception as e:
    print(f'Note: {e}')

# Also delete MPLCONFIGDIR
try:
    api.delete_space_variable('agapemiteu/ManualAi', 'MPLCONFIGDIR')
    print('✅ Deleted MPLCONFIGDIR variable')
except Exception as e:
    print(f'Note: {e}')

print("\n✅ Variables cleaned up - Space will restart automatically")
