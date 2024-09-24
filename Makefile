# Makefile for Raspberry Pi 4 using Python 3.11

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

# Run the WebSocket client (for Raspberry Pi)
run-client:
	@echo "Running WebSocket client..."
	pipenv run python websocket_client.py

# Clean up
clean:
	@echo "Removing virtual environment and cache files..."
	rm -rf .venv
	rm -rf __pycache__
