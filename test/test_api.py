import requests
import json
import time

url = "http://localhost:8000/chat"
payload = {
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "question": "What is the main promise made in the song?"
}
headers = {
    "Content-Type": "application/json"
}

print("--- Request 1 (Cache Miss - should take a few seconds) ---")
start_time = time.time()
try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = time.time()
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")
except Exception as e:
    print(f"Error: {e}")

print("\n--- Request 2 (Cache Hit - should be near-instant) ---")
start_time = time.time()
try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = time.time()
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"Time Taken: {end_time - start_time:.2f} seconds")
except Exception as e:
    print(f"Error: {e}")
