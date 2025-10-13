"""
Test script for uploading the FULL Toyota 4Runner manual (11.8MB, 608 pages)
This tests the system's ability to handle large manuals on free tier hosting.
"""

import requests
import time
from pathlib import Path

# Configuration
API_BASE_URL = "https://agapemiteu-manualai.hf.space"
PDF_PATH = Path(__file__).parent / "data" / "2023-Toyota-4runner-Manual.pdf"
TIMEOUT = 600  # 10 minutes for large file

def main():
    print("=" * 60)
    print("🧪 Testing Upload with FULL Toyota 4Runner Manual")
    print("=" * 60)
    
    # Check file exists and get size
    if not PDF_PATH.exists():
        print(f"❌ Error: File not found at {PDF_PATH}")
        return
    
    file_size_mb = PDF_PATH.stat().st_size / (1024 * 1024)
    print(f"📤 Uploading {PDF_PATH.name} to {API_BASE_URL}...")
    print(f"   Size: {file_size_mb:.2f} MB")
    print(f"   Pages: 608")
    if file_size_mb > 10:
        print(f"   Note: Large file - processing may take 3-5 minutes")
    print()
    
    # Upload the manual
    try:
        with open(PDF_PATH, "rb") as f:
            files = {"file": (PDF_PATH.name, f, "application/pdf")}
            data = {
                "brand": "Toyota",
                "model": "4Runner",
                "year": "2023"
            }
            response = requests.post(
                f"{API_BASE_URL}/api/manuals",
                files=files,
                data=data,
                timeout=TIMEOUT
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 413:
            print("❌ Upload rejected: File too large (413 Payload Too Large)")
            print("   The server rejected the file due to size limits.")
            print("   Recommendation: Use the 30-page sample for free tier testing.")
            return
        
        if response.status_code != 202:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        data = response.json()
        manual_id = data.get("manual_id")
        print("✅ Upload successful!")
        print(f"   Manual ID: {manual_id}")
        print(f"   Status: {data.get('status')}")
        print()
        
        # Poll for processing status
        print("⏳ Waiting for processing (this may take 5-10 minutes for 608 pages)...")
        start_time = time.time()
        last_status = None
        
        while True:
            time.sleep(3)
            elapsed = time.time() - start_time
            
            # Check status
            status_response = requests.get(
                f"{API_BASE_URL}/api/manuals/{manual_id}",
                timeout=30
            )
            
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.status_code}")
                break
            
            status_data = status_response.json()
            current_status = status_data.get("status")
            
            if current_status != last_status:
                if current_status == "processing":
                    print(f"   Status: processing... ({elapsed:.0f}s elapsed)")
                else:
                    print(f"   Status changed to: {current_status}")
                last_status = current_status
            
            if current_status == "ready":
                chunk_count = status_data.get("chunk_count", "unknown")
                print(f"✅ Manual ready! (took {elapsed:.1f}s)")
                print(f"   Chunks created: {chunk_count}")
                print()
                break
            
            elif current_status == "failed":
                error = status_data.get("error", "Unknown error")
                print(f"❌ Processing failed: {error}")
                return
            
            # Timeout after 10 minutes
            if elapsed > 600:
                print("❌ Timeout: Processing took longer than 10 minutes")
                print("   Large manuals may take significant time to process.")
                print("   Recommendation: Check status later or use smaller test files.")
                return
        
        # Test a query
        print("💬 Testing chat query...")
        chat_response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={
                "manual_id": manual_id,
                "question": "What is the engine oil capacity?",
                "stream": False
            },
            timeout=60
        )
        
        if chat_response.status_code == 200:
            print("✅ Chat response received!")
            chat_data = chat_response.json()
            answer = chat_data.get("answer", "")
            print()
            print("Q: What is the engine oil capacity?")
            print(f"A: {answer[:300]}...")
            print()
        else:
            print(f"❌ Chat failed: {chat_response.status_code}")
            print(f"Response: {chat_response.text}")
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("   The file is too large for free tier hosting.")
        print("   Recommendation: Use the 30-page sample instead.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print()
    print("=" * 60)
    print("✅ Test complete! Try it on the web:")
    print("   https://manual-ai-psi.vercel.app")
    print("=" * 60)

if __name__ == "__main__":
    main()
