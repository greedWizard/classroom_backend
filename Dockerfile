FROM python:3.9.12-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apt-get update  && \
    apt install -y python3-dev \
    libboost-mpi-python-dev \
    gcc \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install poetry
ADD pyproject.toml .
RUN poetry install

COPY . .
