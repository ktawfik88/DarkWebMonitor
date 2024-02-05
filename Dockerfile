FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nano \
    wget \
    git \
    curl \
    tor \
    unzip

ARG DEBIAN_FRONTEND=noninteractive



WORKDIR /app

RUN python3.10 -m venv venv
ENV PATH="/app/venv/bin:${PATH}"

COPY requirements.txt /app
RUN /app/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app



CMD ["python3", "main.py"]