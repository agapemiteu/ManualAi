#!/usr/bin/env python3
"""
Quick status check for HuggingFace Space deployment.
Shows Space status and recent logs.
"""
import requests
import sys

def check_status():
    """Check if the Space is running and responsive."""
    
    space_url = "https://agapemiteu-manualai.hf.space"
    
    print("🔍 Checking ManualAI Space Status")
    print("=" * 60)
    print(f"Space URL: {space_url}")
    print()
    
    # Check root endpoint
    print("1️⃣ Checking if Space is running...")
    try:
        response = requests.get(space_url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Space is RUNNING (HTTP {response.status_code})")
        else:
            print(f"   ⚠️  Space returned HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.Timeout:
        print("   ❌ Timeout - Space might be starting up")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed - Space might be offline")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Check API endpoint
    print("\n2️⃣ Checking API endpoint...")
    try:
        response = requests.get(f"{space_url}/api/manuals", timeout=10)
        if response.status_code == 200:
            data = response.json()
            manual_count = len(data.get("manuals", []))
            print(f"   ✅ API is working")
            print(f"   📚 Manuals loaded: {manual_count}")
            if manual_count > 0:
                print(f"   Manuals: {[m.get('manual_id') for m in data['manuals']]}")
        else:
            print(f"   ⚠️  API returned HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ API check failed: {e}")
    
    # Check health endpoint
    print("\n3️⃣ Checking system info...")
    try:
        response = requests.get(f"{space_url}/api/system/logs?limit=50", timeout=10)
        if response.status_code == 200:
            data = response.json()
            logs = data.get("logs", [])
            print(f"   ✅ Got {len(logs)} log lines")
            
            # Look for startup messages
            startup_found = False
            for log in logs:
                if "ManualAI Startup Check" in log or "✅" in log:
                    startup_found = True
                    break
            
            if startup_found:
                print("   ✅ Startup checks visible in logs")
                print("\n   Recent startup logs:")
                for log in logs[:15]:  # Show first 15 lines
                    if any(x in log for x in ["🚀", "✅", "❌", "⚠️", "Startup", "directory"]):
                        print(f"      {log}")
            else:
                print("   ⚠️  No startup messages found yet")
                print("\n   Recent logs:")
                for log in logs[:10]:
                    print(f"      {log}")
        else:
            print(f"   ⚠️  Logs endpoint returned HTTP {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Could not fetch logs: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Status check complete!")
    print("\nNext steps:")
    print("  • If Space is running: python test_upload.py")
    print("  • If startup logs show ✅: Upload should work!")
    print("  • If you see ❌ in logs: We need to debug further")
    print(f"\nSpace dashboard: https://huggingface.co/spaces/Agapemiteu/ManualAi")
    
    return True

if __name__ == "__main__":
    try:
        success = check_status()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
