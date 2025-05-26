# 🚀 Ollama Model Viewer

A beautiful, ADHD-friendly desktop application for viewing and managing your Ollama models with intuitive color coding and comprehensive model information.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎨 ADHD-Friendly Design
- **Color-coded models** based on usage recency:
  - 🟢 **Green**: Recently used (< 2 weeks)
  - 🟡 **Yellow**: Moderately used (2-4 weeks)  
  - 🔴 **Red**: Old models (1+ month)
- **Clear visual hierarchy** with emojis and consistent spacing
- **Dark theme** optimized for reduced eye strain
- **Intuitive navigation** with keyboard and mouse support

### 📊 Comprehensive Model Information
- **Model capabilities detection**:
  - 📝 Text processing
  - 👁️ Vision/multimodal
  - 💻 Code generation
  - 🔗 Embeddings
  - 🛠️ Tool usage
  - 🧠 Reasoning (R1 models)
- **Storage information** with size display
- **Last modified timestamps**
- **Model IDs** and metadata
- **Real-time status** indicators

### 🔍 Advanced Filtering & Search
- **Real-time search** across model names
- **Smart filters**:
  - Usage recency categories
  - Model capabilities
  - Size-based filtering (large/small models)
- **Sortable columns** (name, size, last modified)
- **Model count** display

### 🖱️ Interactive Features
- **Double-click** for detailed model information
- **Refresh button** for real-time updates
- **Responsive layout** that adapts to window size
- **Scrollable views** for large model collections

## 🛠️ Installation

### Prerequisites
- **Python 3.8+** installed on your system
- **Ollama** installed and running
- **macOS/Linux/Windows** (tested on macOS)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ollama-model-viewer
   ```

2. **Run the application**:
   ```bash
   python ollama_model_viewer.py
   ```

The application will automatically:
- Set up a virtual environment using the custom `module_venv.py`
- Install any required dependencies
- Launch the GUI interface

### Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv venv-ollama-model-viewer

# Activate virtual environment
source venv-ollama-model-viewer/bin/activate  # macOS/Linux
# or
venv-ollama-model-viewer\Scripts\activate     # Windows

# Install dependencies (minimal - tkinter comes with Python)
pip install -r requirements.txt

# Run the application
python ollama_model_viewer.py
```

## 🚀 Usage

### Main Interface

1. **Launch the app** - The main window displays all your Ollama models
2. **Color coding** - Models are automatically color-coded by usage recency
3. **Search** - Use the search bar to find specific models
4. **Filter** - Apply filters to view specific model categories
5. **Sort** - Click column headers to sort by different criteria

### Model Details

- **Double-click** any model to view detailed information
- **Refresh** the list using the refresh button
- **Navigate** using keyboard arrows or mouse

### Keyboard Shortcuts

- **Ctrl+F** - Focus search bar (planned)
- **F5** - Refresh model list (planned)
- **Escape** - Close detail windows

## 🎯 Model Capability Detection

The app automatically detects model capabilities based on naming patterns:

| Capability | Detection Keywords | Icon |
|------------|-------------------|------|
| Text | All models | 📝 |
| Vision | vision, vl, visual, llava, clip | 👁️ |
| Code | code, coder, coding | 💻 |
| Embeddings | embed | 🔗 |
| Tools | tool, function, agent | 🛠️ |
| Reasoning | r1, reasoning, think | 🧠 |

## 🎨 Color Scheme

The application uses a carefully designed color palette optimized for ADHD users:

- **Background**: Dark theme for reduced eye strain
- **Text**: High contrast for readability
- **Accents**: Distinct colors for different states
- **Status indicators**: Clear visual feedback

## 🔧 Configuration

### Custom Virtual Environment

The app uses a custom virtual environment manager located at:
```
/Users/fweir/py-utils/module_venv.py
```

This ensures consistent dependency management across projects.

### Ollama Integration

The app connects to Ollama via the command line interface:
- Requires `ollama` command to be available in PATH
- Automatically parses `ollama list` output
- Real-time model status detection

## 🐛 Troubleshooting

### Common Issues

**"Ollama not found"**
- Ensure Ollama is installed and in your PATH
- Try running `ollama list` in terminal to verify

**"Virtual environment errors"**
- Check that `/Users/fweir/py-utils/module_venv.py` exists
- Verify Python 3.8+ is installed

**"GUI not displaying correctly"**
- Ensure you're running on a system with GUI support
- Try updating your Python tkinter installation

### Debug Mode

Run with debug output:
```bash
python ollama_model_viewer.py --debug
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama team** for the excellent local LLM platform
- **Python tkinter** for the GUI framework
- **ADHD community** for design inspiration and feedback

## 🔮 Future Features

- [ ] Model performance metrics
- [ ] Usage analytics and charts
- [ ] Model comparison tools
- [ ] Export/import model lists
- [ ] Integration with model hubs
- [ ] Custom color themes
- [ ] Keyboard shortcuts
- [ ] Model management actions (delete, update)
- [ ] System resource monitoring
- [ ] Model recommendation engine

---

**Made with ❤️ for the ADHD community and Ollama users** 