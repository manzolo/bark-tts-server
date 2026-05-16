"""Smoke test: carica il modello (bark-small in CI), invoca l'endpoint
/generate-audio/ via TestClient e verifica che il WAV restituito sia valido.
"""
import io
import os
import sys

os.environ.setdefault("BARK_MODEL", "suno/bark-small")

import soundfile as sf
from fastapi.testclient import TestClient

from app import app, model

client = TestClient(app)

response = client.post("/generate-audio/", json={"text": "Ciao"})
assert response.status_code == 200, f"HTTP {response.status_code}: {response.text[:200]}"
assert response.headers["content-type"] == "audio/wav", response.headers

data, sr = sf.read(io.BytesIO(response.content))
expected_sr = model.generation_config.sample_rate
assert sr == expected_sr, f"sample rate {sr} != atteso {expected_sr}"
assert len(data) > 0, "audio vuoto"

print(f"OK: {len(data)} samples @ {sr} Hz ({len(data)/sr:.2f}s)")
sys.exit(0)
