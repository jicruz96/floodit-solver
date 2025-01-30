FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["fastapi", "run"]
