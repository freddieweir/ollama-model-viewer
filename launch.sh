#!/bin/bash
# 🚀 Ollama Model Viewer Launch Script
# Enhanced with automatic GUI framework detection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 Ollama Model Viewer - Enhanced Launch Script${NC}"
echo -e "${CYAN}=====================================\n${NC}"

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}🍎 macOS detected - Native GUI features available${NC}"
    GUI_ENHANCEMENT="macOS Native Translucency"
else
    echo -e "${YELLOW}🖥️ Non-macOS system detected - Using cross-platform GUI${NC}"
    GUI_ENHANCEMENT="Cross-platform compatibility"
fi

echo -e "${PURPLE}✨ GUI Enhancement: ${GUI_ENHANCEMENT}${NC}\n"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found${NC}"

# Check for virtual environment
if [ ! -d "venv-ollama-model-viewer" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv-ollama-model-viewer
fi

# Activate virtual environment
echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
source venv-ollama-model-viewer/bin/activate

# Install/upgrade dependencies
echo -e "${CYAN}📋 Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️ No requirements.txt found, installing minimal dependencies...${NC}"
    # Install basic dependencies if requirements.txt is missing
    if [[ "$OSTYPE" == "darwin"* ]]; then
        pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz > /dev/null 2>&1
        echo -e "${GREEN}✅ macOS GUI dependencies installed${NC}"
    fi
fi

# Check for Ollama
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama found${NC}"
else
    echo -e "${YELLOW}⚠️ Ollama not found in PATH${NC}"
    echo -e "${CYAN}💡 Make sure Ollama is installed and running${NC}"
fi

echo ""

# Determine which script to run
if [ -f "gui_bridge.py" ]; then
    echo -e "${PURPLE}🌉 Starting Enhanced GUI Bridge...${NC}"
    echo -e "${CYAN}🎯 Features: Automatic framework detection, translucent effects${NC}"
    echo ""
    python3 gui_bridge.py
elif [ -f "ollama_model_viewer.py" ]; then
    echo -e "${BLUE}🚀 Starting Ollama Model Viewer...${NC}"
    echo -e "${CYAN}🎯 Features: Classic interface, cross-platform${NC}"
    echo ""
    python3 ollama_model_viewer.py
else
    echo -e "${RED}❌ No application script found${NC}"
    echo -e "${YELLOW}💡 Expected gui_bridge.py or ollama_model_viewer.py${NC}"
    exit 1
fi 