# Makefile

# Virtual environment activation
VENV := ./.venv
ACTIVATE := source $(VENV)/bin/activate

# Install dependencies with retry logic for failures
install:
	@echo "Creating virtual environment and installing dependencies..."
	# Install dependencies from Pipfile and retry if it fails
	@if ! pipenv install --dev; then \
	    echo "Initial installation failed. Retrying..."; \
	    pipenv --clear; \
	    pipenv install --dev; \
	fi
	# Generate requirements.txt from pip freeze
	@pipenv run pip freeze > requirements.txt || echo "Failed to generate requirements.txt, ensure all dependencies are installed."

# Activate virtual environment
activate:
	@echo "Activating virtual environment..."
	$(ACTIVATE)

# Run the WebSocket client (for Raspberry Pi)
run-client:
	@echo "Running WebSocket client..."
	@pipenv run python websocket_client.py || echo "Failed to run WebSocket client."

# Run FastAPI server (for non-Raspberry Pi environments)
run-server:
	@echo "Running FastAPI server on MacBook or host machine..."
	@echo "FastAPI should NOT run on the Raspberry Pi."
	@pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 || echo "Failed to run FastAPI server."

# Clean up
clean:
	@echo "Removing virtual environment and cache files..."
	@rm -rf $(VENV)
	@rm -rf __pycache__
	@rm -rf requirements.txt Pipfile.lock Pipfile
	@echo "Cleaned up environment."

# Install RPi.GPIO for Raspberry Pi
install-rpi:
	@echo "Installing RPi.GPIO..."
	@pipenv install RPi.GPIO || echo "Failed to install RPi.GPIO."

# Install websockets for communication
install-websockets:
	@echo "Installing websockets..."
	@pipenv install websockets || echo "Failed to install websockets."

