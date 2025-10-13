#!/usr/bin/env python3
"""
Test upload of sample PDF to HuggingFace backend.
"""

import requests
import time
from pathlib import Path

BACKEND_URL = "https://agapemiteu-manualai.hf.space"
PDF_PATH = Path("data/Toyota-4Runner-Sample-30pages.pdf")

def upload_manual():
    """Upload the sample manual."""
    print(f"📤 Uploading {PDF_PATH.name} to {BACKEND_URL}...")
    print(f"   Size: {PDF_PATH.stat().st_size / (1024*1024):.2f} MB")
    
    with open(PDF_PATH, 'rb') as f:
        files = {'file': (PDF_PATH.name, f, 'application/pdf')}
        data = {
            'manual_id': 'toyota_4runner_sample',
            'brand': 'Toyota',
            'model': '4Runner',
            'year': '2023'
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/manuals",
            files=files,
            data=data,
            timeout=300
        )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 202:
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"   Manual ID: {data.get('manual_id')}")
        print(f"   Status: {data.get('status')}")
        return data.get('manual_id')
    else:
        try:
            print(f"❌ Upload failed: {response.json()}")
        except:
            print(f"❌ Upload failed: {response.text}")
        return None

def check_status(manual_id, max_wait=180):
    """Check processing status."""
    print(f"\n⏳ Waiting for processing...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BACKEND_URL}/api/manuals/{manual_id}")
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status == 'ready':
                elapsed = time.time() - start_time
                print(f"✅ Manual ready! (took {elapsed:.1f}s)")
                return True
            elif status == 'failed':
                print(f"❌ Processing failed: {data.get('error')}")
                return False
            else:
                print(f"   Status: {status}... ({int(time.time() - start_time)}s elapsed)")
        
        time.sleep(10)
    
    print(f"⚠️ Timeout after {max_wait}s")
    return False

def test_chat(manual_id):
    """Test a chat query."""
    print(f"\n💬 Testing chat query...")
    
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        json={
            'question': 'What are the main safety features?',
            'manual_id': manual_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat response received!")
        print(f"\nQ: What are the main safety features?")
        print(f"A: {data.get('answer', 'N/A')[:300]}...")
    else:
        print(f"❌ Chat failed: {response.text}")

def main():
    print("=" * 60)
    print("🧪 Testing Upload with Sample PDF")
    print("=" * 60)
    
    if not PDF_PATH.exists():
        print(f"❌ Error: {PDF_PATH} not found!")
        print("   Run: python extract_sample.py first")
        return
    
    # Upload
    manual_id = upload_manual()
    if not manual_id:
        return
    
    # Wait for processing
    if not check_status(manual_id):
        return
    
    # Test chat
    test_chat(manual_id)
    
    print("\n" + "=" * 60)
    print("✅ Test complete! Try it on the web:")
    print("   https://manual-ai-psi.vercel.app")
    print("=" * 60)

if __name__ == "__main__":
    main()
