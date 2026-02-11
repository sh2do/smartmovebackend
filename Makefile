# Makefile for SmartMove Backend

.PHONY: up down build logs test shell help

# Sets the project name for docker-compose to avoid conflicts
COMPOSE_PROJECT_NAME=smartmove

up:
	@echo "Starting up services..."
	docker-compose up -d

down:
	@echo "Stopping services and removing volumes..."
	docker-compose down -v

build:
	@echo "Building Docker images..."
	docker-compose build

logs:
	@echo "Tailing logs..."
	docker-compose logs -f

test:
	@echo "Running tests in test service..."
	docker-compose run --rm test /bin/sh -c "pip install -r requirements-dev.txt && echo \\$PATH && ls -l /usr/local/bin && python -m pytest"
shell:
	@echo "Opening shell in web container..."
	docker-compose exec web /bin/sh

help:
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  up        - Start all services in the background"
	@echo "  down      - Stop all services and remove data volumes"
	@echo "  build     - Rebuild the Docker images"
	@echo "  logs      - Tail logs from all services"
	@echo "  test      - Run the pytest suite inside the web container"
	@echo "  shell     - Open a shell in the web container"
	@echo "  help      - Display this help message"
	@echo ""