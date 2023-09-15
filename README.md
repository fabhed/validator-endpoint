<div align="center">

# **Bittensor Validator Endpoint**

### Prompt the Bittensor network via an API <!-- omit in toc -->

**[Getting started](btvep/README.md#getting-started)** |
**[Documentation](./docs/README.md)**

</div>

## Overview

- `btvep` - Contains the backend, which includes an API and CLI, written in python. `btvep` Allows validators to easily host an API for other services to prompt the Bittensor network.
- `admin-ui` - Admin interface for validator owners to view all and manage API-keys and request logs (similar to the cli, but more approachable and )
- `chat-ui` - An end-user interface similar to ChatGPT, but powered by Bittensor. This interface is made to work out of the box with the backend API.

## Features

### `btvep`

- Host an API server with API key authentication
- [`btvep` CLI](./docs/cli.md) for configuration and key management
- API key lifetimes - set expiry dates
- API key credits - limit amount of requests with credits
- Request logs
- Rate limits - Configure default limits or custom per API key
- Drop-in replacement for [OpenAI's Chat API](https://platform.openai.com/docs/api-reference/chat)
- Easily Filter requests via [OpenAI's Moderation Endpoint](https://platform.openai.com/docs/guides/moderation/overview)
- 3 Query strategies
  - `top_n` - Query top n incentive miners. This allows for querying the whole network with one request, e.g. setting top_n to the number of uids on the subnet.
  - `uids` - Query specific uids.
  - `default` - When no strategy is specified in the request, query a default uid. This should normaly be the validator itself to utilize its own miner selection model for prompts.

### `admin-ui`

- View request logs
- Manage API-keys (same functionality as cli)
- Manage API configuration
- Preview CURL-requests

### `chat-ui`

- A frontend for end users to query the backend, similar to chat.openai.com. Users can on the same page also specify UIDs, and search through UIDs with descriptions/tags. Login system via email & password, Google and Github
- Signup & Login via Github, Google or Username/Password (Requires Auth0 setup)

## Planned features

- Adding options for payment for credits. Payment could for example be handled with TAO or an integration with Stripe for card payments.
- Add additional future subnetworks, ex for image and audio.
- LangChain integration

## Example request

Make a request with the key you just created (Replace $API_KEY)

```bash
curl http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Endpoint-Version: 2023-05-19" \
  -d '{
     "messages": [{"role": "user", "content": "What is 1+1?"}]
   }'
```

## API Usage Examples

### Prompt the bittensor network

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

### Prompt a specific neurons via uids on the network

```bash
curl http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Endpoint-Version: 2023-05-19" \
  -d '{
     "uids": [0, 1],
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

### Prompt top neurons sorted by incentive on the network

```bash
curl http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Endpoint-Version: 2023-05-19" \
  -d '{
     "top_n": 5,
     "messages": [{"role": "user", "content": "What is 1+1?"}]
   }'
```

This will send the prompt to the top 5 miners, change `top_n` to 1 to only query the top miner.
