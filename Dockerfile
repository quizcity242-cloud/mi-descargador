FROM python:3.11-slim

# Instalar aria2, ffmpeg y dependencias de red
RUN apt-get update && apt-get install -y \
    aria2 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000
CMD ["python", "app.py"]
