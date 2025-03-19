# Dockerfile for FastAPI CRUD Application
FROM python:3.9-slim

WORKDIR /app

RUN pip install fastapi uvicorn motor pydantic

COPY crud.py .

EXPOSE 8000

CMD ["uvicorn", "crud:app", "--host", "0.0.0.0", "--port", "8000"]
