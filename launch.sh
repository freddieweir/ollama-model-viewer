#!/bin/bash

# 🚀 Ollama Model Viewer Launcher
# Simple script to launch the ADHD-friendly Ollama Model Viewer

echo "🚀 Starting Ollama Model Viewer..."
echo "📋 ADHD-friendly desktop app for viewing your Ollama models"
echo ""

# Check if Ollama is running
if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama not found in PATH"
    echo "Please install Ollama first: https://ollama.ai"
    exit 1
fi

# Check if Ollama service is running
if ! ollama list &> /dev/null; then
    echo "⚠️  Warning: Ollama service might not be running"
    echo "Starting Ollama service..."
    ollama serve &
    sleep 2
fi

# Launch the application
echo "🎯 Launching GUI application..."
python ollama_model_viewer.py

echo "👋 Thanks for using Ollama Model Viewer!" 