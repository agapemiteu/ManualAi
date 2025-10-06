#!/usr/bin/env python3
"""Check what's actually deployed on HuggingFace Space"""
from huggingface_hub import hf_hub_download

file = hf_hub_download(
    repo_id='agapemiteu/ManualAi',
    filename='document_loader.py',
    repo_type='space',
    local_dir='tmp/hf_check',
    force_download=True
)

print(f"Downloaded: {file}\n")
print("=" * 70)
print("LINES 35-55 of document_loader.py ON HUGGINGFACE SPACE:")
print("=" * 70)

with open(file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(34, min(55, len(lines))):
        print(f"{i+1:3d}: {lines[i]}", end='')

print("\n" + "=" * 70)
