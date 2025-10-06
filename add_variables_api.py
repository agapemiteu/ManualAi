#!/usr/bin/env python3
"""
Add Variables to HuggingFace Space using Web API
"""

import requests
import sys
from huggingface_hub import HfApi

SPACE_ID = "agapemiteu/ManualAi"

print()
print("=" * 70)
print("🔧 Adding Variables via HuggingFace Web API")
print("=" * 70)
print()

try:
    # Get authentication token
    from huggingface_hub import HfFolder
    token = HfFolder.get_token()
    
    if not token:
        print("❌ No authentication token found!")
        print("   Please run: huggingface-cli login")
        sys.exit(1)
    
    api = HfApi()
    
    user = api.whoami()
    print(f"✅ Authenticated as: {user['name']}")
    print()
    
    # HuggingFace API endpoint for adding variables
    base_url = "https://huggingface.co"
    
    variables = [
        {"key": "MANUAL_DISABLE_OCR", "value": "true"},
        {"key": "MANUAL_INGESTION_TIMEOUT", "value": "120"},
        {"key": "MANUALAI_LOG_LEVEL", "value": "INFO"},
    ]
    
    print(f"📝 Adding variables to space: {SPACE_ID}")
    print()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    for var in variables:
        print(f"   Adding {var['key']} = {var['value']}...", end=" ")
        
        # Try adding as a variable (not secret)
        url = f"{base_url}/api/spaces/{SPACE_ID}/variables"
        
        payload = {
            "key": var["key"],
            "value": var["value"],
            "description": ""
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201, 204]:
                print("✅")
            elif response.status_code == 409:
                # Variable might already exist, try updating
                print("⚠️ (already exists, trying update...)", end=" ")
                update_url = f"{base_url}/api/spaces/{SPACE_ID}/variables/{var['key']}"
                update_response = requests.put(update_url, json={"value": var["value"]}, headers=headers, timeout=10)
                if update_response.status_code in [200, 201, 204]:
                    print("✅")
                else:
                    print(f"❌ ({update_response.status_code})")
                    print(f"      Response: {update_response.text[:200]}")
            else:
                print(f"❌ ({response.status_code})")
                print(f"      Response: {response.text[:200]}")
                
                # Try alternative endpoint
                print(f"      Trying alternative method...", end=" ")
                alt_url = f"{base_url}/api/spaces/{SPACE_ID}/env"
                alt_payload = {
                    "variables": [{"key": var["key"], "value": var["value"]}]
                }
                alt_response = requests.post(alt_url, json=alt_payload, headers=headers, timeout=10)
                if alt_response.status_code in [200, 201, 204]:
                    print("✅")
                else:
                    print(f"❌ ({alt_response.status_code})")
                    
        except Exception as e:
            print(f"❌ ({e})")
    
    print()
    print("=" * 70)
    print("🔄 Restarting space...")
    print("=" * 70)
    print()
    
    try:
        api.restart_space(repo_id=SPACE_ID)
        print("✅ Restart command sent!")
        print()
    except Exception as e:
        print(f"⚠️  Could not restart: {e}")
        print("   Please restart manually from settings")
        print()
    
    print("=" * 70)
    print("✅ Configuration Complete!")
    print("=" * 70)
    print()
    print("If the web API method didn't work, please add manually:")
    print()
    print("1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings")
    print("2. Find 'Variables and secrets' section")
    print("3. Under 'Variables' (not Secrets), add:")
    print()
    print("   • MANUAL_DISABLE_OCR = true")
    print("   • MANUAL_INGESTION_TIMEOUT = 120")
    print("   • MANUALAI_LOG_LEVEL = INFO")
    print()
    print("4. Space will auto-restart")
    print("5. Wait 2 minutes for rebuild")
    print()
    
    # Wait a bit and check status
    print("⏳ Waiting 10 seconds before checking status...")
    import time
    time.sleep(10)
    
    print()
    print("🔍 Checking space status...")
    try:
        response = requests.get("https://agapemiteu-manualai.hf.space/", timeout=5)
        if response.status_code == 200:
            print("✅ Space is running!")
        else:
            print(f"⏳ Space returned {response.status_code} (still building...)")
    except:
        print("⏳ Space not accessible yet (still building...)")
    
    print()
    
except Exception as e:
    print()
    print(f"❌ Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("=" * 70)
    print("Please add variables manually:")
    print("=" * 70)
    print()
    print("1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings")
    print("2. Under 'Variables' section, add:")
    print("   • MANUAL_DISABLE_OCR = true")
    print("   • MANUAL_INGESTION_TIMEOUT = 120")
    print("   • MANUALAI_LOG_LEVEL = INFO")
    print()
    sys.exit(1)
