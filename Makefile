SHELL := /bin/bash

IMAGE       ?= manzolo/bark-docker
CONTAINER   ?= bark
PORT        ?= 8000
TEXT        ?= Ciao, questo è un test.
OUTPUT      ?= output.wav

.DEFAULT_GOAL := help
.PHONY: help build up down restart logs shell ps test generate clean nuke

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Docker image
	docker build -t $(IMAGE) .

up: ## Start the service via docker compose (detached)
	docker compose up -d

down: ## Stop and remove the service
	docker compose down

restart: down up ## Restart the service

logs: ## Tail service logs
	docker compose logs -f

shell: ## Open a shell inside the running container
	docker exec -it $(CONTAINER) /bin/bash

ps: ## Show service status
	docker compose ps

test: ## Run the smoke test locally on CPU with bark-small
	BARK_MODEL=suno/bark-small CUDA_VISIBLE_DEVICES="" python tests/smoke_test.py

generate: ## Generate audio via the running API (TEXT=... OUTPUT=...)
	curl -fsS -X POST http://localhost:$(PORT)/generate-audio/ \
		-H "Content-Type: application/json" \
		-d '{"text": "$(TEXT)"}' \
		--output $(OUTPUT)
	@echo "Saved -> $(OUTPUT)"

clean: ## Remove generated audio artifacts
	rm -f output.wav generated_audio.wav

nuke: clean down ## Stop service and wipe the HuggingFace model cache (forces re-download)
	rm -rf cache/
