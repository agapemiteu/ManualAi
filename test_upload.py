#!/usr/bin/env python3
"""Test manual upload to verify ingestion works"""
import requests
import time
import sys

API_URL = "https://agapemiteu-manualai.hf.space"
MANUAL_ID = "smoke-test"

def test_upload():
    """Upload a test manual and wait for ingestion"""
    print("=" * 70)
    print("🧪 TESTING MANUAL UPLOAD & INGESTION")
    print("=" * 70)
    
    # Step 1: Delete any existing test manual
    print("\n1️⃣ Cleaning up old test manual...")
    try:
        response = requests.delete(f"{API_URL}/api/manuals/{MANUAL_ID}?force=true")
        if response.status_code == 204:
            print("   ✅ Old manual deleted")
        elif response.status_code == 404:
            print("   ✅ No existing manual to delete")
    except Exception as e:
        print(f"   ⚠️  Delete failed: {e}")
    
    # Step 2: Upload new manual
    print("\n2️⃣ Uploading test manual...")
    with open("tmp/smoke-manual.txt", "rb") as f:
        files = {"file": ("smoke-manual.txt", f, "text/plain")}
        data = {
            "brand": "Test",
            "model": "Smoke",
            "year": "2024",
            "manual_id": MANUAL_ID
        }
        
        try:
            response = requests.post(f"{API_URL}/api/manuals", files=files, data=data)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            
            if response.status_code != 200:
                print(f"   ❌ Upload failed!")
                return False
            
            print("   ✅ Upload successful")
        except Exception as e:
            print(f"   ❌ Upload error: {e}")
            return False
    
    # Step 3: Monitor ingestion status
    print("\n3️⃣ Monitoring ingestion status...")
    start_time = time.time()
    timeout = 180  # 3 minutes max
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_URL}/api/manuals/{MANUAL_ID}")
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                elapsed = time.time() - start_time
                
                print(f"   [{elapsed:.1f}s] Status: {status}", end="")
                
                if "status_message" in data and data["status_message"]:
                    print(f" - {data['status_message']}")
                else:
                    print()
                
                if status == "ready":
                    print(f"\n   ✅ INGESTION COMPLETE in {elapsed:.1f}s!")
                    print(f"   📊 Chunks: {data.get('num_chunks', 'N/A')}")
                    return True
                elif status == "failed":
                    print(f"\n   ❌ INGESTION FAILED!")
                    print(f"   Error: {data.get('status_message', 'Unknown error')}")
                    return False
                elif status == "processing":
                    time.sleep(3)  # Check every 3 seconds
                else:
                    print(f"\n   ⚠️  Unknown status: {status}")
                    time.sleep(3)
        except Exception as e:
            print(f"\n   ❌ Status check error: {e}")
            time.sleep(3)
    
    print(f"\n   ❌ TIMEOUT after {timeout}s!")
    return False

if __name__ == "__main__":
    success = test_upload()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ TEST PASSED - Ingestion works correctly!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ TEST FAILED - Ingestion still broken")
        print("=" * 70)
        print("\nChecking logs...")
        try:
            response = requests.get(f"{API_URL}/api/system/logs?limit=50")
            logs = response.json().get("logs", [])
            print("\nLast 20 log lines:")
            for log in logs[-20:]:
                print(f"  {log}")
        except:
            pass
        sys.exit(1)
