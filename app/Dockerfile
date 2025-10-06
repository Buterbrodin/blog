FROM python:3.12.0-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    make \
    bash \
    && rm -rf /var/cache/apk/*

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup -S app && adduser -S app -G app
RUN mkdir -p /usr/src/app/static_collected /usr/src/app/media \
    && chown -R app:app /usr/src/app/static_collected /usr/src/app/media \
    && chown -R app:app /usr/src/app

USER app

