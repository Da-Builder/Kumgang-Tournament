FROM python:3.13-alpine
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

EXPOSE 8080
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY --exclude=**/__pycache__/ source .
CMD ["uvicorn", "--port=8080", "main:app"]
