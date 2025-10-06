#!/usr/bin/env python3
"""
Restart HuggingFace Space
"""

from huggingface_hub import HfApi
import time
import sys

SPACE_ID = "agapemiteu/ManualAi"

print()
print("=" * 60)
print("🔄 Restarting ManualAI HuggingFace Space")
print("=" * 60)
print()

try:
    api = HfApi()
    user = api.whoami()
    print(f"✅ Logged in as: {user['name']}")
    print()
    
    print(f"🔄 Restarting space: {SPACE_ID}...")
    api.restart_space(repo_id=SPACE_ID)
    print("✅ Restart command sent!")
    print()
    
    print("⏳ Waiting for space to restart...")
    print("   This usually takes 2-3 minutes...")
    print()
    
    # Wait and check status
    for i in range(60):  # Check for up to 5 minutes
        try:
            import requests
            response = requests.get("https://agapemiteu-manualai.hf.space/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Space is {data.get('status', 'running')}!")
                print()
                print("=" * 60)
                print("🎉 Space Successfully Restarted!")
                print("=" * 60)
                print()
                print("✅ Next Steps:")
                print("  1. Test upload at: https://manual-ai-psi.vercel.app/upload")
                print("  2. Upload should complete in ~30 seconds")
                print("  3. Check logs for 'OCR DISABLED' message")
                print()
                sys.exit(0)
        except Exception:
            pass
        
        # Progress indicator
        if i % 10 == 0:
            print(f"   Still waiting... ({i*5} seconds elapsed)")
        
        time.sleep(5)
    
    print()
    print("⚠️  Space is taking longer than expected to start")
    print("   Check status at: https://huggingface.co/spaces/agapemiteu/ManualAi")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("Please restart manually:")
    print("  1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi/settings")
    print("  2. Click 'Factory Reboot'")
    print()
    sys.exit(1)
