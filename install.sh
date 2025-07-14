#!/bin/bash

echo "Installing Ollama Chat App dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "Python3 is required but not installed. Please install Python3 first."
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installation complete!"
echo ""
echo "To run the app:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the app: python3 main.py"
echo ""
echo "Or use the run script: ./run.sh"