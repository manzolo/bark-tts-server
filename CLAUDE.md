# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A thin FastAPI wrapper that exposes Suno's Bark text-to-speech model as an HTTP service, packaged for GPU-enabled Docker deployment. The entire application is a single file (`app.py`); the Dockerfile additionally clones the upstream `suno-ai/bark` repo into the image so the `python -m bark.bark` CLI is usable inside the container.

## Common commands

Build and run (GPU required for reasonable latency):
```
docker build -t manzolo/bark-docker .
docker run --gpus all -v ./cache:/root/.cache --name bark -p 8000:8000 manzolo/bark-docker
docker stop bark && docker rm bark
```

Or via compose (uses `runtime: nvidia`):
```
docker compose up
```

Hit the API:
```
curl -X POST "http://localhost:8000/generate-audio/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is a test."}' --output output.wav
```

Run the upstream Bark CLI directly inside the container:
```
python -m bark.bark --text "Hello, my name is Suno." --output_filename "/root/.cache/example.wav"
```

## Architecture notes

- **Model loading is at import time** (`app.py:10-15`). The processor and `BarkModel` are loaded once when the module is imported and moved to CUDA if available; there is no lazy loading or per-request reload.
- **Model is configurable via `BARK_MODEL` env var** (default `suno/bark`). CI uses `suno/bark-small` to fit on CPU runners.
- **First run downloads models** from HuggingFace into `/root/.cache`. The `./cache` host volume mount persists these between container restarts — without it, every fresh container re-downloads several GB.
- **Voice preset is hardcoded** to `v2/it_speaker_1` (Italian) in `app.py:28`. Changing voice/language means editing this constant.
- **Output file is a fixed name** (`generated_audio.wav`) written to the working directory and overwritten on each request — the service is not safe for concurrent requests as-is.
- **Sample rate is read from `model.generation_config.sample_rate`** rather than hardcoded — Bark produces 24000 Hz, so any hardcoded value (e.g. the old 22050) causes wrong pitch/speed.
