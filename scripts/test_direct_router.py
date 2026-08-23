import json
import urllib.request

payload = json.dumps({
    "model": "ag/gemini-3.7-flash-high",
    "messages": [
        {"role": "user", "content": "What is 2+2? Output ONLY the single integer number."}
    ],
    "temperature": 0.0
}).encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:3040/v1/chat/completions",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-b2a2f6c6f8228b4b-prod01-71d3127b"
    }
)

with urllib.request.urlopen(req) as res:
    print(res.read().decode("utf-8"))
