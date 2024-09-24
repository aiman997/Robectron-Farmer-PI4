# Makefile for Raspberry Pi 4 using Python 3.11

# Virtual environment activation
SHELL := /bin/bash
VENV := ./.venv
ACTIVATE := source $(VENV)/bin/activate

# Install dependencies with Python 3.11 on Raspberry Pi
install:
	@echo "Checking if Python 3.11 is installed..."
	if ! python3.11 --version; then \
		echo "Python 3.11 not found. Installing Python 3.11..."; \
		sudo apt update && sudo apt install -y python3.11 python3.11-venv python3.11-dev; \
	fi
	@echo "Creating virtual environment with Python 3.11..."
	pipenv --python /usr/bin/python3.11
	@echo "Installing dependencies with --skip-lock..."
	pipenv install --skip-lock

# Activate virtual environment
activate:
	@echo "Activating virtual environment..."
	$(ACTIVATE)

# Run the WebSocket client (for Raspberry Pi)
run-client:
	@echo "Running WebSocket client..."
	$(ACTIVATE) && pipenv run python websocket_client.py

# Clean up
clean:
	@echo "Removing virtual environment and cache files..."
	rm -rf $(VENV)
	rm -rf __pycache__
