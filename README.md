[![CI](https://github.com/manzolo/bark-docker/actions/workflows/ci.yml/badge.svg)](https://github.com/manzolo/bark-docker/actions/workflows/ci.yml)

docker build -t manzolo/bark-docker .
docker run --gpus all -v ./cache:/root/.cache --name bark -p 8000:8000 manzolo/bark-docker
docker stop bark && docker rm bark

python -m bark.bark --text "Hello, my name is Suno." --output_filename "/root/.cache/example.wav"

curl -X POST "http://localhost:8000/generate-audio/" -H "Content-Type: application/json" -d '{"text": "Hello, this is a test."}' --output output.wav

#la prima generazione impiega il tempo di scaricarsi i modelli
