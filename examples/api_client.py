import urllib.request
import urllib.error
import json

URL = "http://localhost:8000/api/v1/evaluate"

payload = {
    "scenario": "The application reflects the search parameter without sanitization.",
    "evidence": [
        "Passing <script>alert(1)</script> results in it being executed in the browser."
    ]
}

data = json.dumps(payload).encode('utf-8')

req = urllib.request.Request(URL, data=data, method='POST')
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print("Evaluation Successful!")
        print(f"ID: {result['evaluation_id']}")
        print(f"Classification: {result['classification']}")
        print(f"State: {result['evidence_state']}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"API Error {e.code}: {error_body}")
except urllib.error.URLError as e:
    print(f"Connection Error: Is the API server running on port 8000? ({e.reason})")
