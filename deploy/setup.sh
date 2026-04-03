#!/bin/bash
set -e

echo "=== Oracle AI Server Setup ==="

# Detect architecture
ARCH=$(uname -m)
echo "Architecture: $ARCH"

# 1. Install Ollama
if command -v ollama &> /dev/null; then
    echo "Ollama already installed: $(ollama --version)"
else
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 2. Start Ollama service
echo "Starting Ollama service..."
if systemctl is-active --quiet ollama 2>/dev/null; then
    echo "Ollama service already running"
else
    sudo systemctl enable ollama
    sudo systemctl start ollama
    sleep 3
fi

# 3. Pull model
MODEL="${MODEL_NAME:-qwen3.5:4b}"
echo "Pulling model: $MODEL ..."
ollama pull "$MODEL"

# 4. Install Python dependencies
echo "Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet

# 5. Create .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit API_KEY before running!"
fi

echo ""
echo "=== Setup Complete ==="
echo "Start the server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
