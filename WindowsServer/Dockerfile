# Use a base image with python installed
FROM python:3.12

# Set up working directory for the RUN, CMD, ENTRYPTOINT and ADD commands
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry configuration files
COPY ./pyproject.toml ./poetry.lock /app/

# Copy the server files
COPY ./src/server /app/src/server

# Make directories for the runtime data
RUN mkdir /app/data/processed

RUN mkdir /app/data/raw

# Activate the poetry virtual environment
RUN eval $(poetry env activate)

# Install all dependancies
RUN poetry install

# Start the server
CMD ["poetry", "run", "python", "-m", "src/server/routes/main.py"]