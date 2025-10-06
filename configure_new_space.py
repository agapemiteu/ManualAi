#!/usr/bin/env python3
"""Add environment variables to the NEW HuggingFace Space"""
from huggingface_hub import HfApi
import requests

api = HfApi()
SPACE_ID = "Agapemiteu/ManualAi"

# Get token
token = api.token
if not token:
    print("❌ No HuggingFace token found. Please run: huggingface-cli login")
    exit(1)

headers = {
    "authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

variables = [
    {"key": "MANUAL_DISABLE_OCR", "value": "true"},
    {"key": "MANUAL_INGESTION_TIMEOUT", "value": "120"},
    {"key": "MANUALAI_LOG_LEVEL", "value": "INFO"}
]

print("=" * 70)
print("ADDING ENVIRONMENT VARIABLES TO NEW SPACE")
print("=" * 70)

for var in variables:
    key = var["key"]
    value = var["value"]
    
    print(f"\n📝 Adding: {key} = {value}")
    
    response = requests.post(
        f"https://huggingface.co/api/spaces/{SPACE_ID}/variables",
        headers=headers,
        json={"key": key, "value": value}
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Added successfully")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")

print("\n" + "=" * 70)
print("✅ VARIABLES CONFIGURED")
print("=" * 70)
print("\nSpace will restart automatically with new variables...")
