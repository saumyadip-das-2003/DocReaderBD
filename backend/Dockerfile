FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ben \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    shobdoocr==0.1.1

COPY . .

ENV TESSERACT_CMD=/usr/bin/tesseract

EXPOSE 8080

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
