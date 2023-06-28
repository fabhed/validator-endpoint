# Make Requests to Endpoints

How to make requests to the Validator Endpoint.

## Basic Request with Python

```python
import requests
import json

URL = "http://localhost:8000/chat"  # Update to match your server url
API_KEY = "h3t5tiRs4GUZFXzhHTnyQkPDe22S4Sj6ibMW_SuR14fVTwdFO6rk5mZA3OlWP_Pp"  # Update to match your API key

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
    "Endpoint-Version": "2023-05-19",
}

data = {
    'messages': [{'role': 'user', 'content': 'What is 1+1?'}]
}

response = requests.post(URL, headers=headers, data=json.dumps(data))

# handle errors
if response.status_code != 200:
    print("Error:", response.json()["detail"])

else:
  choice = response.json()["choices"][0]
  data["messages"].append(choice["message"])
  reply = choice["message"]["content"]
  print("Reply:", reply, "\n")
```

Output:

```
Reply: 1+1 equals 2.
```

## Basic Request with Using Curl

```bash
curl http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Endpoint-Version: 2023-05-19" \
  -d '{
     "messages": [{"role": "user", "content": "What is 1+1?"}]
   }'
```

Response:

```json
{
  "choices": [
    {
      "index": 0,
      "responder_hotkey": "5ETyaEdDp2RQDoGazHzdGRmJUSzfrXCrMj5PyoFoskFdtsyH",
      "message": {
        "role": "assistant",
        "content": "this is a test!"
      }
    }
  ]
}
```

## Continous Conversation Using Python

Have a ChatGPT like back and forth conversation with the network:

```python
import requests
import json

URL = "http://localhost:8000/chat"  # Update to match your server url
API_KEY = "h3t5tiRs4GUZFXzhHTnyQkPDe22S4Sj6ibMW_SuR14fVTwdFO6rk5mZA3OlWP_Pp"  # Update to match your API key

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
    "Endpoint-Version": "2023-05-19",
}
data = {"messages": []}

print("You are talking to the Bittensor network. What do you want to ask?\n")

for i in range(5):
    message = input("Message: ")
    data["messages"].append({"role": "user", "content": message})
    response = requests.post(URL, headers=headers, data=json.dumps(data))

    # handle errors
    if response.status_code != 200:
        print("Error:", response.json()["detail"])
        continue

    choice = response.json()["choices"][0]
    data["messages"].append(choice["message"])
    reply = choice["message"]["content"]
    print("Reply:", reply, "\n")
```
