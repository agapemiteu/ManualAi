FROM node:18-bullseye

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    libmagic1 \
    libgl1 \
    libglib2.0-0 \
    qpdf \
  && ln -sf python3 /usr/bin/python \
  && ln -sf pip3 /usr/bin/pip \
  && npm install -g npm@9 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
