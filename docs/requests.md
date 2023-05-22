# Make Requests to Endpoints

How to make requests to the Validator Endpoint.

## Basic Request with Python

```python
import requests
import json

url = 'http://<IP_ADDRESS>:<PORT>/chat'
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <API_KEY>',
    'Endpoint-Version': '2023-05-19'
}
data = {
    'messages': [{'role': 'user', 'content': 'What is 1+1?'}]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
reply = response.json()["message"]["content"]
print("Reply:", reply)
```

Output:

```
Reply: As an AI language model, I can tell you that the answer to 1+1 is 2.
```

## Basic Request with Using Curl

```bash
curl http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Endpoint-Version: 2023-05-19" \
  -d '{
     "messages": [{"role": "user", "content": "Say this is a test!"}]
   }'
```

Response:

```json
{
  "message": {
    "role": "assistant",
    "content": "this is a test!"
  }
}
```

## Continous Conversation Using Python

Have a ChatGPT like back and forth conversation with the network:

```python
import requests
import json

url = "http://<IP_ADDRESS>:<PORT>/chat"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <API_KEY>",
    "Endpoint-Version": "2023-05-19",
}
data = {"messages": []}

print("You are talking to the Bittensor network. What do you want to ask?\n")

for i in range(5):
    message = input("Message: ")
    data["messages"].append({"role": "user", "content": message})
    response = requests.post(url, headers=headers, data=json.dumps(data))

    data["messages"].append(response.json()["message"])
    reply = response.json()["message"]["content"]
    print("Reply:", reply, "\n")
```
