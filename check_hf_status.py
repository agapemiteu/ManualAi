#!/usr/bin/env python3
"""
Check HuggingFace Space Status and Logs
"""

from huggingface_hub import HfApi
import sys

SPACE_ID = "agapemiteu/ManualAi"

print()
print("=" * 70)
print("🔍 Checking ManualAI Space Status")
print("=" * 70)
print()

try:
    api = HfApi()
    
    # Get space info
    print(f"📊 Space ID: {SPACE_ID}")
    print()
    
    try:
        space_info = api.space_info(repo_id=SPACE_ID)
        print(f"✅ Space found!")
        print(f"   Runtime: {space_info.runtime}")
        print(f"   SDK: {space_info.sdk}")
        
        if hasattr(space_info, 'stage'):
            print(f"   Stage: {space_info.stage}")
        
        print()
    except Exception as e:
        print(f"⚠️  Could not get space info: {e}")
        print()
    
    # List files in the space
    print("📁 Files in space:")
    try:
        files = api.list_repo_files(repo_id=SPACE_ID, repo_type="space")
        for f in sorted(files)[:20]:  # Show first 20 files
            print(f"   • {f}")
        if len(files) > 20:
            print(f"   ... and {len(files) - 20} more files")
        print()
    except Exception as e:
        print(f"⚠️  Could not list files: {e}")
        print()
    
    # Check environment variables (secrets)
    print("🔐 Checking environment variables...")
    try:
        # Note: We can't directly read secret values, but we can try to list them
        print("   Variables should be set in the web UI:")
        print("   • MANUAL_DISABLE_OCR = true")
        print("   • MANUAL_INGESTION_TIMEOUT = 120")
        print("   • MANUALAI_LOG_LEVEL = INFO")
        print()
    except Exception as e:
        print(f"⚠️  {e}")
        print()
    
    # Try to access the space
    print("🌐 Testing space endpoint...")
    try:
        import requests
        response = requests.get(f"https://agapemiteu-manualai.hf.space/", timeout=5)
        if response.status_code == 200:
            print(f"✅ Space is RUNNING!")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            print()
        else:
            print(f"⚠️  Space returned status {response.status_code}")
            print(f"   This usually means it's still building/restarting")
            print()
    except requests.exceptions.Timeout:
        print("⏳ Space is not responding yet (still building...)")
        print()
    except Exception as e:
        print(f"⚠️  Space is not accessible: {type(e).__name__}")
        print(f"   This is normal during build/restart")
        print()
    
    print("=" * 70)
    print("📋 Next Steps:")
    print("=" * 70)
    print()
    print("1. Go to: https://huggingface.co/spaces/agapemiteu/ManualAi")
    print("2. Check if there's a 'Building' indicator at the top")
    print("3. Click 'Logs' tab to see build progress")
    print("4. Look for any error messages in red")
    print()
    print("Common issues:")
    print("  • 'Configuration error' - Usually temporary during restart")
    print("  • '503 Server Unavailable' - Space is building")
    print("  • Docker build errors - Check Dockerfile and requirements.txt")
    print()
    print("If build fails:")
    print("  • Check the 'Logs' tab for specific error messages")
    print("  • Verify all files are present (main.py, requirements.txt, etc.)")
    print("  • Try 'Factory Reboot' from Settings")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
