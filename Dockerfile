FROM python:3.13

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
WORKDIR /app
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt .
COPY main.py .
COPY solvers/ solvers/
COPY helpers/ helpers/
COPY index.html .
RUN pip install -r requirements.txt
CMD ["fastapi", "run", "--port", "8080"]
