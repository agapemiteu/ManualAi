#!/usr/bin/env python3
"""Add environment variables including LLM support"""
import requests

# Get token from user
print("\n" + "="*70)
print("🔑 HUGGINGFACE TOKEN NEEDED")
print("="*70)
print("\n1. Go to: https://huggingface.co/settings/tokens")
print("2. Create a token with 'read' permission (or use existing)")
print("3. Copy the token\n")

token = input("Paste your HuggingFace token here: ").strip()

if not token:
    print("❌ Token is required!")
    exit(1)

SPACE_ID = "Agapemiteu/ManualAi"

headers = {
    "authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

variables = [
    {"key": "MANUAL_DISABLE_OCR", "value": "true"},
    {"key": "MANUAL_INGESTION_TIMEOUT", "value": "120"},
    {"key": "MANUALAI_LOG_LEVEL", "value": "INFO"},
    {"key": "MANUAL_USE_LLM", "value": "true"},
    {"key": "HF_TOKEN", "value": token}  # For Inference API
]

print("\n" + "="*70)
print(f"📤 ADDING VARIABLES TO {SPACE_ID}")
print("="*70 + "\n")

for var in variables:
    key = var["key"]
    value = var["value"] if key != "HF_TOKEN" else "***hidden***"
    
    print(f"Adding: {key} = {value}")
    
    response = requests.post(
        f"https://huggingface.co/api/spaces/{SPACE_ID}/variables",
        headers=headers,
        json={"key": var["key"], "value": var["value"]}
    )
    
    if response.status_code in [200, 201]:
        print(f"  ✅ Success")
    elif response.status_code == 409:
        print(f"  ⚠️  Already exists")
    else:
        print(f"  ❌ Failed: {response.status_code}")

print("\n" + "="*70)
print("✅ CONFIGURATION COMPLETE!")
print("="*70)
print("\nSpace will restart automatically...")
print("Wait 1-2 minutes, then test!")
