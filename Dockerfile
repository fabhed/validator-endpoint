# We will use the official Python 3.10 image from Docker Hub
FROM python:3.10-slim-buster

# Set a directory for our application
WORKDIR /app

# Install system level dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install poetry for package management
RUN pip install poetry

# Copy our pyproject.toml file first to use Docker cache efficiently
COPY ./pyproject.toml /app/

# Set Path for poetry
ENV PATH="${PATH}:/root/.poetry/bin"

# Install dependencies without creating a virtual environment inside the container
RUN poetry config virtualenvs.create false \
    && poetry install

# Copy the rest of our application
COPY . /app

# Run the application
CMD ["poetry", "run", "btvep", "start", "--port", "8000"]
