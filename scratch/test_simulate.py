
import requests
import json

base_url = "http://127.0.0.1:8000"
dataset_id = 71

payload = {
    "missing_method": "smart",
    "outlier_method": "iqr",
    "outlier_action": "fix",
    "noisy_method": "none",
    "noisy_action": "fix",
    "drop_columns": []
}

try:
    response = requests.post(f"{base_url}/simulate/{dataset_id}", json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Failed to connect: {e}")
