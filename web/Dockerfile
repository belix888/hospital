FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY hospital_web /app/hospital_web

WORKDIR /app/hospital_web

CMD ["gunicorn", "config.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]

