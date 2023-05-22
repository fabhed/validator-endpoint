# validator-endpoint

This is an open source repository for Bittensor validator owners, for easily setting
up a REST service with api endpoints that allows for sharing access to querying the Bittensor
network through their validator.

NOTE: This project and readme is a WIP.

## Get started

```bash
# Install with pip
python3 -m pip install https://github.com/ViktorThink/validator-endpoint/raw/main/dist/btvep-0.1.0-py3-none-any.whl
# Set your hotkey mnemonic
btvep config set hotkey_mnemonic <HOTKEY_mnemonic>
# Create an api key
btvep key create
# Start the server
btvep start --port 8000
```

Try out the api key you just created (Replace $API_KEY)

```bash
curl http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Endpoint-Version: 2023-05-19" \
  -d '{
     "messages": [{"role": "user", "content": "Say this is a test!"}]
   }'
```

## Requirements

- Python 3.10+

## API Usage Examples

### Query the bittensor network

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

### Query a specific neuron via its uid on the network

```bash
curl http://localhost:8000/chat \
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

## Dev requirements

- Poetry: https://python-poetry.org/docs/

## Dev setup

```bash
# Clone the repo
git clone https://github.com/ViktorThink/validator-endpoint.git
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
uvicorn btvep.server:app --reload
```

### Generate docs

```bash
typer btvep.cli utils docs --output docs/cli.md --name btvep
```

### grpcio dependency (from bittensor) arm fix

```
python3 -m pip install --no-binary :all: grpcio --ignore-installed
```
