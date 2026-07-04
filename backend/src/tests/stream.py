import requests
import traceback
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   

url = "http://localhost:8000/response/stream"
input = {
    "input" : [{
        "role": "user",
        "content": "hello"
    }],
    "interview_type" : 1
}

path = os.path.join(BASE_DIR, "../../data/testing/streamingNLP.txt")
os.makedirs(os.path.dirname(path), exist_ok = True)

with requests.post(url, stream=True, json = input) as r:
    print(r.status_code)
    print(r.headers)
    try:
        for chunk in r.iter_content(decode_unicode = True, chunk_size = 1024):
            if chunk:
                print(chunk, end='', flush=True)
                
                # Test log
                with open(path, "a") as file:       # Avoid overwriting by appending
                    file.write(chunk)
    except Exception as e:
        traceback.print_exc()

    
