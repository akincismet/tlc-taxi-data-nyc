FROM python:3.12-slim

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src