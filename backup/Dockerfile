# Dockerfile for MongoDB Backup Script with Scheduled Backup
FROM python:3.9-slim

WORKDIR /app

RUN pip install pymongo schedule

COPY backup.py .

CMD ["python", "-u", "backup.py"]
