FROM python:3.12

COPY . /app

WORKDIR /app

RUN pip install poetry

RUN mkdir -p /app

RUN eval $(poetry env activate)

RUN poetry install

CMD ["poetry", "run", "python", "-m", "src/server/routes/main.py"]