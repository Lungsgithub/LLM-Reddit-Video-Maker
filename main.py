import requests
from subprocess import call
import json

url = "http://localhost:11434/api/generate"

headers = {
    "Content-Type": "application/json"    
}

data = {
    "model": "dolphin-mistral",
    "prompt": "write a post about your life. something like r/aita. immediately start with the title",
    "stream": False
}

try:
    # Send POST request and handle response
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=False)

    if response.status_code == 200:
        responses = []
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    actual_response = data.get("response", "")
                    responses.append(actual_response)
                except json.JSONDecodeError as e:
                    print(f"JSONDecodeError: {e}")

        # Save responses to a JSON file with the key "story"
        output = {"story": " ".join(responses)}

        with open('story.json', 'w') as f:
            json.dump(output, f, indent=4)

        print("Responses saved to story.json")
    else:
        print("Error:", response.status_code, response.text)
 
except requests.RequestException as e:
    print(f"Request Exception: {e}")
except Exception as e:
    print(f"Error: {e}")


def open_py_file():
    call(["python", "make-vid.py"])

open_py_file()
