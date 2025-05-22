# Python backend için Dockerfile
FROM python:3.13-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "api:app", "--bind", "0.0.0.0:5000"]
