#!/usr/bin/env python3
"""List and manage HuggingFace Space environment variables"""
from huggingface_hub import HfApi
import requests

api = HfApi()
SPACE_ID = "agapemiteu/ManualAi"

print("=" * 70)
print("CURRENT HUGGINGFACE SPACE VARIABLES")
print("=" * 70)

# Get space info
headers = {"authorization": f"Bearer {api.token}"}
response = requests.get(f"https://huggingface.co/api/spaces/{SPACE_ID}", headers=headers)
data = response.json()

# Try to find variables
if "runtime" in data:
    runtime = data["runtime"]
    if "secrets" in runtime:
        print("\nSecrets:")
        for secret in runtime.get("secrets", []):
            print(f"  - {secret}")
    
    if "hardware" in runtime:
        print(f"\nHardware: {runtime['hardware']}")

# List SDK variables 
try:
    # Get variables endpoint
    vars_response = requests.get(
        f"https://huggingface.co/api/spaces/{SPACE_ID}/variables",
        headers=headers
    )
    if vars_response.status_code == 200:
        variables = vars_response.json()
        print(f"\nVariables ({len(variables)}):")
        for var in variables:
            key = var.get("key", var.get("name", "unknown"))
            value = var.get("value", "***")
            print(f"  - {key} = {value}")
            
            # Delete problematic variable
            if key == "MANUAL_OCR_CACHE_DIR":
                print(f"\n⚠️  Found {key} - this might be set to old path!")
                choice = input("Delete this variable? (y/n): ")
                if choice.lower() == 'y':
                    del_resp = requests.delete(
                        f"https://huggingface.co/api/spaces/{SPACE_ID}/variables/{key}",
                        headers=headers
                    )
                    if del_resp.status_code in [200, 204]:
                        print(f"✅ Deleted {key}")
                    else:
                        print(f"❌ Failed to delete: {del_resp.status_code} {del_resp.text}")
    else:
        print(f"\nCould not fetch variables: {vars_response.status_code}")
except Exception as e:
    print(f"\nError fetching variables: {e}")

print("\n" + "=" * 70)
