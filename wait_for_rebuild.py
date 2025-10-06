#!/usr/bin/env python3
"""
Quick status checker - Wait for rebuild and verify fix
"""

import requests
import time
import sys

print()
print("=" * 70)
print("⏳ Waiting for HuggingFace Space Rebuild")
print("=" * 70)
print()
print("Checking every 10 seconds...")
print("(This usually takes 2-3 minutes)")
print()

attempt = 0
max_attempts = 30  # 5 minutes max

while attempt < max_attempts:
    attempt += 1
    try:
        response = requests.get("https://agapemiteu-manualai.hf.space/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print()
            print("=" * 70)
            print("✅ Space is READY!")
            print("=" * 70)
            print()
            print(f"Status: {data.get('status', 'running')}")
            print()
            print("🧪 Ready to test!")
            print()
            print("1. Go to: https://manual-ai-psi.vercel.app/upload")
            print("2. Upload a text-based PDF")
            print("3. Should complete in ~30 seconds")
            print()
            sys.exit(0)
    except Exception:
        pass
    
    elapsed = attempt * 10
    print(f"  [{elapsed}s] Still building...", end="\r")
    time.sleep(10)

print()
print()
print("⚠️  Taking longer than expected")
print("Check manually: https://huggingface.co/spaces/agapemiteu/ManualAi")
print()
