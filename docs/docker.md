# Validator Endpoint with Docker

This guide will walk you through the process of setting up and running the Validator Endpoint using Docker Compose.

## Install Docker

To install Docker, you can follow the official Docker documentation:

- [Install Docker Engine](https://docs.docker.com/engine/install/)

## Setting Up Docker Compose and Configuration

You can replace the `HOTKEY_MNEMONIC` with your actual mnemonic and `REDIS_URL` with your actual Redis URL.

## Starting the Container

You can start the Validator Endpoint container using Docker Compose with the following command:

```bash
docker-compose up -d
```

This command starts the container in the background and maps the container's port 80 to port 80 on your host machine.

## Running Commands

To run commands inside the running Docker container, use the `docker exec` command:

```bash
docker exec -it <container_name> <command>
```

Replace `<container_name>` with the name of your running Docker container, and `<command>` with the command you want to run inside the container. For example, to run the `btvep key create` command inside a container named `validator-endpoint`, you would run:

```bash
docker exec -it validator-endpoint btvep key create
```

You can run any number of commands inside the container using this method.

That's it! You now have your Validator Endpoint running in a Docker container. Happy validating!
