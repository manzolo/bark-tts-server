# Usa un'immagine di base con Python preinstallato
FROM python:3.9-slim

# Installa le dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Copia il file requirements.txt e il codice sorgente
COPY requirements.txt .
RUN git clone https://github.com/suno-ai/bark.git /app/bark

# Installa tutte le dipendenze in un unico comando
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

COPY app.py .

# Esponi la porta (opzionale)
EXPOSE 8000

RUN pip install soundfile

# Comando di avvio
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]