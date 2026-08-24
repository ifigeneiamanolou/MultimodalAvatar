FROM python:3.13

RUN pip install poetry

RUN mkdir -p /app

COPY . /app

WORKDIR /app

RUN eval $(poetry env activate)

CMD ["poetry", "run", "python", "-m", "src/server/routes/main.py"]