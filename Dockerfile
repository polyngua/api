FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt clean
RUN apt update
RUN apt upgrade -y
RUN pip install poetry

WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry config virtualenvs.create false
RUN poetry install

COPY . .

ENTRYPOINT ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
