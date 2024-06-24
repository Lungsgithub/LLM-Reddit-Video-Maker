import requests
from subprocess import call
import json

url = "http://localhost:11434/api/generate"

headers = {
    "Content-Type": "application/json"    
}

data = {
    "model": "dolphin-mistral",
    "prompt": "Write a very short story for r/AmItheAsshole pretending a person in a very short form. Your story should feature a protagonist who is facing a moral dilemma involving a close family member or friend. The conflict should revolve around a specific event or decision that has caused tension. Be sure to include a little background to explain the relationships and why the situation is important. Use an outlandishly click baiting hook. The story should end with the protagonist questioning if they were in the wrong for their actions or decisions, providing enough context for readers to offer their judgment but otherwise keep it minimal. DO NOT MENTION YOU'RE AN AI MODEL. YOU ARE THE PROTAGONIST IN THE STORY. you also arent supposed to answer the question of whether you are the asshole or not, you ask the reader",
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
