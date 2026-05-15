FROM python:3.10-slim

WORKDIR /app

RUN apt-get update -o Acquire::ForceIPv4=true --fix-missing && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    cmake \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    tesseract-ocr \
    tesseract-ocr-eng \
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries=10 \
    -r requirements.txt \
    "uvicorn[standard]==0.29.0"

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]