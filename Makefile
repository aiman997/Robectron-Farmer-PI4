# Makefile

# Virtual environment activation
VENV := ./.venv
ACTIVATE := source $(VENV)/bin/activate

# Install dependencies and Python 3.9 from source if missing
install:
	@echo "Checking if Python 3.9 is installed..."
	@if ! python3.9 --version > /dev/null 2>&1; then \
		echo "Python 3.9 not found. Installing Python 3.9 from source..."; \
		sudo apt update && sudo apt install -y wget build-essential libffi-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev; \
		cd /usr/src; \
		sudo wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz; \
		sudo tar xzf Python-3.9.16.tgz; \
		cd Python-3.9.16; \
		sudo ./configure --enable-optimizations; \
		sudo make altinstall; \
	fi
	@echo "Python 3.9 is installed."
	@echo "Creating virtual environment with Python 3.9 and installing dependencies..."
	@if ! pipenv --python /usr/local/bin/python3.9 install --dev; then \
	    echo "Initial installation failed. Retrying..."; \
	    pipenv --clear; \
	    pipenv --python /usr/local/bin/python3.9 install --dev; \
	fi
	@echo "Generating requirements.txt from installed packages..."
	@pipenv run pip freeze > requirements.txt || echo "Failed to generate requirements.txt, ensure all dependencies are installed."

# Activate virtual environment
activate:
	@echo "Activating virtual environment..."
	$(ACTIVATE)

# Run the WebSocket client (for Raspberry Pi)
run-client:
	@echo "Running WebSocket client..."
	pipenv run python websocket_client.py

# Clean up
clean:
	@echo "Removing virtual environment and cache files..."
	rm -rf $(VENV)
	rm -rf __pycache__

# Install websockets for communication
install-websockets:
	@echo "Installing websockets..."
	pipenv install websockets
