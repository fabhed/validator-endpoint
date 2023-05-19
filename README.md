# validator-endpoint

This is an open source repository for Bittensor validator owners, for easily setting
up a REST service with api endpoints that allows for sharing access to querying the Bittensor
network through their validator.

## Examples

### Query the bittensor network

```bash
curl https://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Endpoint-Version: 2023-05-19" \
  -d '{
     "messages": [{"role": "user", "content": "Say this is a test!"}],
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

### Query a specific neuron via its uid on the network

```bash
curl https://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Endpoint-Version: 2023-05-19" \
  -d '{
     "uid": 123,
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

## Requirements

- Python 3.10+

## Setup

```
git clone the repo
env vs config.yml ?


```

## Timeline

This is a work in progress, and we aim to have a the first version done by May 25th.
