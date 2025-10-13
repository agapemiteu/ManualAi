"""Test if API returns source pages"""
import requests

API_BASE_URL = "https://agapemiteu-manualai.hf.space"
MANUAL_ID = "manual-77c2314e"

print("Testing API with source pages...")
print()

response = requests.post(
    f"{API_BASE_URL}/api/chat",
    json={
        "manual_id": MANUAL_ID,
        "question": "What should you do if the parking brake is engaged?",
        "stream": False
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print()

if response.status_code == 200:
    data = response.json()
    print("✅ Response received!")
    print()
    print(f"Answer: {data.get('answer', 'N/A')[:300]}...")
    print()
    print(f"Source Pages: {data.get('source_pages', 'N/A')}")
    print()
    
    if data.get('source_pages'):
        print("✅ Source pages are being returned!")
    else:
        print("❌ No source pages in response")
else:
    print(f"❌ Error: {response.text}")
