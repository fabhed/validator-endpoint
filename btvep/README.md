# btvep

## Getting started

```bash
# Install with pip
python3 -m pip install https://github.com/fabhed/validator-endpoint/raw/main/btvep/dist/btvep-0.2.0-py3-none-any.whl
# Set your hotkey mnemonic (quotes are needed since the mnemonic has spaces in it)
btvep config set hotkey_mnemonic "my_validators_secret_mnemonic_phrase_here"
# Create an API key
btvep key create
# Start the server
btvep start --port 8000
```

As an alternative to the above approach you can also use docker: [Docker Guide](../docs/docker.md)

## Tutorials

- [Colab Notebook Tutorial](https://colab.research.google.com/drive/1RRQhxSmGiULEZNj0gYswa2JksZ56cGa1?usp=sharing): A step-by-step guide on how to use our project in a Colab notebook.

## Requirements

- Python 3.10
- If Rate limiting is used [Redis](https://redis.io/docs/getting-started/installation/) is also required

## Dev requirements

- Poetry: https://python-poetry.org/docs/

## Dev setup

```bash
# Clone the repo
git clone https://github.com/fabhed/validator-endpoint.git
cd validator-endpoint/btvep

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

# You can also directly execute this command to avoid having to launch a poetry shell
poetry run btvep start --reload
```

### Generate docs

```bash
# Run under ./btvep folder
poetry run typer btvep.cli utils docs --output docs/cli.md --name btvep
```

### Build .whl files in /dist

```bash
# Run under ./btvep folder
poetry build
```

### grpcio dependency (from bittensor) arm fix

```bash
# Run under ./btvep folder
python3 -m pip install --no-binary :all: grpcio --ignore-installed
```
