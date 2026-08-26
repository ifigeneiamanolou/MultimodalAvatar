# Use a base image with python installed
FROM python:3.11

# Set up working directory for the RUN, CMD, ENTRYPTOINT and ADD commands
WORKDIR /app

# Install system dependencies required by psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Make directories for the runtime data
RUN mkdir -p /app/data/processed

# Copy poetry configuration files
COPY ./pyproject.toml ./poetry.lock /app/

# Copy the server files
COPY ./src/server /app/src/server

# Install all dependancies
RUN poetry install

# Start the server
CMD ["poetry", "run", "python", "-m", "src/server/routes/main.py"]

