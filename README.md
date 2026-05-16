# Bark TTS Server

[![CI](https://github.com/manzolo/bark-tts-server/actions/workflows/ci.yml/badge.svg)](https://github.com/manzolo/bark-tts-server/actions/workflows/ci.yml)

HTTP service exposing [Suno Bark](https://github.com/suno-ai/bark) text-to-speech as a simple FastAPI endpoint, packaged for GPU-enabled Docker.

Send text, get a WAV back.

## Quick start

### Docker Compose (recommended)

```bash
docker compose up -d
```

### Plain Docker

```bash
docker build -t manzolo/bark-docker .
docker run --gpus all -v ./cache:/root/.cache -p 8000:8000 --name bark manzolo/bark-docker
```

### Generate audio

```bash
curl -X POST http://localhost:8000/generate-audio/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Ciao, questo è un test."}' \
  --output output.wav
```

> First request downloads the model weights (~5 GB for `suno/bark`) into `./cache`. Subsequent runs reuse the cache, so keep the volume mount.

## Configuration

| Variable      | Default       | Description                                                                 |
| ------------- | ------------- | --------------------------------------------------------------------------- |
| `BARK_MODEL`  | `suno/bark`   | HuggingFace model id. Use `suno/bark-small` (~2 GB) for lower-resource runs. |

The voice preset is hardcoded to `v2/it_speaker_1` (Italian) in `app.py`. Change there to use another language or speaker — see the [Bark speaker library](https://suno-notion-page.notion.site/8b8e8749ed514b0cbf3f699013548683?v=bc67cff786b04b50b3ceb756fd05f68c) for the full list.

## Requirements

- Docker with NVIDIA Container Toolkit for GPU acceleration.
- ~5 GB free disk for model cache (or ~2 GB with `bark-small`).
- CPU-only inference works but is slow (minutes per short sentence).

## Development

Run the smoke test locally (uses `suno/bark-small` on CPU):

```bash
pip install -r requirements.txt fastapi uvicorn soundfile httpx
BARK_MODEL=suno/bark-small CUDA_VISIBLE_DEVICES="" python tests/smoke_test.py
```

The same test runs in CI on every push — see `.github/workflows/ci.yml`.

## Caveats

- The output file is written to a fixed path on disk and overwritten per request; the service is **not safe for concurrent requests** as-is.
- The model is loaded at import time, so the container takes ~30 s to become ready on a warm cache.
