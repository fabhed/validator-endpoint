# Validator Endpoint with Docker

This guide will walk you through the process of setting up and running the Validator Endpoint using Docker. This is preferrable if you don't want to bother installing the correct python version or redis, as all of this is pre-configured in our Dockerfile. It will however require you to start a shell within the docker container to be able to use the `btvep` cli.

## Install Docker

To install Docker, you can follow the official Docker documentation:

- [Install Docker Engine](https://docs.docker.com/engine/install/)

## Setting Up Docker Compose and Configuration

```bash
# Copy the template file to a .gitignored docker-compose.yml
cp docker-compose.template.yml docker-compose.yml
```

Replace the `HOTKEY_MNEMONIC` environemnt variable in docker-compose.yml with your actual mnemonic.

## Starting the Container

You can start the Validator Endpoint container using Docker Compose with the following command:

```bash
# Starts the containers in the background
docker-compose up -d
```

By default the `btvep_api` container is accessable on port 8000 your host machine. This can be changed in the docker-compose.yml file as well.

## Running Commands

Since the `btvep` cli is installed in the container, it won't be accessable from your host machine. To run commands inside the running Docker container, simply use the `docker exec` command:

```bash
# Start a shell with access to btvep
docker exec -it btvep_api /bin/bash

# Run any btvep commands
btvep --help # available commands
btvep key create # create an API key
```

This spawns a bash shell in the docker environment where you have access to the `btvep` command

That's it! You now have your Validator Endpoint running in a Docker container. Happy validating!

## Try it out

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
