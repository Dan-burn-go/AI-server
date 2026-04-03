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
    API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/change-me-to-a-secure-random-string/$API_KEY/" .env
    echo "Created .env with auto-generated API_KEY"
    echo "API_KEY: $API_KEY"
    echo "⚠ 이 키를 학교 서버에도 설정하세요!"
fi

echo ""
echo "=== Setup Complete ==="
echo "Start the server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000"
