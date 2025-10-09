# FortiForge Dockerfile (simulation-first)
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    FORTIFORGE_ENV=docker

RUN useradd -ms /bin/bash app && \
    apt-get update && apt-get install -y --no-install-recommends \
      gcc openssh-client git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install -U pip && pip install -e . -r requirements.txt

USER app
CMD ["fortiforge", "--help"]
