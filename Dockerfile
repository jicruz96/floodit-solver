FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
WORKDIR /app
COPY requirements.txt main.py solvers/ helpers/ ./
RUN pip install -r requirements.txt
CMD ["fastapi", "run"]
