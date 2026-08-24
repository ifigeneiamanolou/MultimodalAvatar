FROM python:3.11

COPY . /app

WORKDIR /app

RUN pip install poetry

RUN mkdir -p /app

RUN poetry env use python3.11

RUN poetry install

CMD ["poetry", "run", "python", "-m", "src/server/routes/main.py"]