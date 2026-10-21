
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir flask==3.1.1 requests==2.32.4

COPY app.py .
COPY templates ./templates

EXPOSE 8000

CMD ["python", "app.py"]
