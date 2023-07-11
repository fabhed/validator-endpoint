<div align="center">

# **Bittensor Validator Endpoint**

### Prompt the Bittensor network via an API <!-- omit in toc -->

[Documentation](./docs)

</div>

Allow validators to easily host an API for other services to prompt the Bittensor network.

## Features

- Host an API server with API key authentication
- Web Dashboard for statistics, configuration and key management
- [`btvep`](./docs/cli.md) CLI for configuration and key management
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

## Planned features

- A frontend for end users to query the backend, similar to chat.openai.com
  Users can on the same page also specify UIDs, and search through UIDs with descriptions/tags. Login system via email & password, Google and Github
- Adding options for payment for credits. Payment could for example be handled with TAO or an integration with Stripe for card payments.
- Add additional future subnetworks, ex for image and audio.
- LangChain integration

## Getting started

```bash
# Install with pip
python3 -m pip install https://github.com/fabhed/validator-endpoint/raw/main/dist/btvep-0.1.1-py3-none-any.whl
# Set your hotkey mnemonic (quotes are needed since the mnemonic has spaces in it)
btvep config set hotkey_mnemonic "my_validators_secret_mnemonic_phrase_here"
# Create an API key
btvep key create
# Start the server
btvep start --port 8000
```

As an alternative to the above approach you can also use docker: [Docker Guide](./docs/docker.md)

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

## Tutorials

- [Colab Notebook Tutorial](https://colab.research.google.com/drive/1RRQhxSmGiULEZNj0gYswa2JksZ56cGa1?usp=sharing): A step-by-step guide on how to use our project in a Colab notebook.

## Requirements

- Python 3.10
- If Rate limiting is used [Redis](https://redis.io/docs/getting-started/installation/) is also required

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

## Dev requirements

- Poetry: https://python-poetry.org/docs/

## Dev setup

```bash
# Clone the repo
git clone https://github.com/fabhed/validator-endpoint.git
cd validator-endpoint

# Install depedencies
poetry install

# Launch the shell enviornment
poetry shell

# Run your editor
code .

# You can now run the cli
btvep --help

# Run the server with auto reloading
btvep start --reload
```

### Generate docs

```bash
poetry run typer btvep.cli utils docs --output docs/cli.md --name btvep
```

### Build .whl files in /dist

```bash
poetry build
```

### grpcio dependency (from bittensor) arm fix

```
python3 -m pip install --no-binary :all: grpcio --ignore-installed
```
