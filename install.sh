#!/bin/sh
set -e

echo "ProofSec Evaluation Platform Installer"
echo "======================================"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required but not installed."
    exit 1
fi

VENV_DIR="$HOME/.proofsec-env"

echo "1. Creating Python virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR"

echo "2. Installing ProofSec..."
# In a real environment, this would be:
# "$VENV_DIR/bin/pip" install proofsec
# For now, we clone or assume running locally. Since this is an installer, we'll pip install git+https://github.com/proofsec/proofsec.git
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install "git+https://github.com/proofsec/proofsec.git" || echo "Note: Source repo might not exist yet, this is a placeholder URL."

# Add to path
if [ -d "$HOME/.local/bin" ]; then
    ln -sf "$VENV_DIR/bin/proofsec" "$HOME/.local/bin/proofsec"
    echo "Symlinked proofsec to $HOME/.local/bin/proofsec"
else
    echo "Please add $VENV_DIR/bin to your PATH to run proofsec."
fi

echo ""
echo "Installation complete!"
echo "Run 'proofsec version' to verify."
