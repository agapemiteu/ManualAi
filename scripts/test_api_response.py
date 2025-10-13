"""
Quick test to see what the actual API response looks like
"""
import requests
import json

API_BASE_URL = "https://agapemiteu-manualai.hf.space"
MANUAL_ID = "manual-77c2314e"

# Test question
question = "What should you do if the 'Braking Power Low Stop in a Safe Place' message appears?"
ground_truth = "Immediately stop the vehicle in a safe place and contact your Toyota dealer."
ground_truth_page = 490

print("Testing single query to understand API response format...")
print(f"Question: {question}")
print(f"Ground Truth: {ground_truth}")
print(f"Expected Page: {ground_truth_page}")
print()

try:
    response = requests.post(
        f"{API_BASE_URL}/api/chat",
        json={
            "manual_id": MANUAL_ID,
            "question": question,
            "stream": False
        },
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print("Full Response JSON:")
        print(json.dumps(data, indent=2))
        print()
        
        answer = data.get("answer", "")
        print("Answer:")
        print(answer)
        print()
        
        # Check if there's source info or context
        sources = data.get("sources", [])
        context = data.get("context", [])
        
        if sources:
            print("Sources:")
            print(sources)
        
        if context:
            print("Context:")
            print(context)
            
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
