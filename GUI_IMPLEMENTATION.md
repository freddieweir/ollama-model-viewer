# 🚀 macOS Native GUI Implementation

## Overview

This implementation adds native macOS translucent GUI support to the Ollama Model Viewer, featuring Apple's signature aesthetic of subtle depth and context-aware translucency.

## ✨ Features

### Visual Elements & Behavior
- **🎨 System Materials**: Utilizes `NSVisualEffectView` for translucent backgrounds that adapt to content and lighting
- **📊 Layered Translucency**: Two distinct layers with different opacities and blur radii (base: 15px, surface: 8px)
- **🎯 Dynamic Color Adaptation**: Automatic luminance and saturation adjustments using CIELAB-based approach
- **⚡ Gaussian Blur**: Customizable blur effects (10-30px radius) with performance optimization

### Technical Implementation
- **🍎 Native macOS Frameworks**: Leverages `objc` and Cocoa frameworks
- **⚙️ NSVisualEffectView**: Core translucency implementation
- **🎛️ Multiple Materials**: WindowBackground, Sidebar, and other native materials
- **🔄 Blending Modes**: BehindWindow and WithinWindow for proper layering

### Accessibility & Performance
- **♿ WCAG 2.1 Compliance**: Maintains ≥4.5:1 contrast ratio for text legibility
- **🔧 "Reduce Transparency" Support**: Respects macOS accessibility settings
- **⚡ Performance Optimized**: Targets <0.5ms frame time for blur operations
- **💾 Memory Efficient**: Low memory usage similar to native Cocoa performance

## 🏗️ Architecture

### Core Components

#### 1. `macos_gui.py` - Native Implementation
```python
class MacOSTranslucentWindow:
    """Main window with native macOS translucent effects"""
    
class MacOSModelListView:
    """Model list with translucent styling and performance optimization"""
```

#### 2. `gui_bridge.py` - Framework Bridge
```python
class ModelViewerGUIBridge:
    """Seamless integration between tkinter and macOS native GUIs"""
    
class GUIFramework(Enum):
    TKINTER = "tkinter"
    MACOS_NATIVE = "macos_native" 
    AUTO = "auto"
```

#### 3. Enhanced Launch System
- **Automatic Detection**: Detects macOS and PyObjC availability
- **Graceful Fallback**: Falls back to tkinter on non-macOS or when PyObjC unavailable
- **User Choice**: Interactive framework selection

## 🎯 Usage

### Automatic Mode (Recommended)
```bash
./launch.sh
```
The system will automatically:
1. Detect macOS and PyObjC availability
2. Choose the best GUI framework
3. Install dependencies if needed
4. Launch with optimal settings

### Manual Framework Selection
```python
from gui_bridge import create_gui_from_preferences, GUIPreferences, GUIFramework

# Force macOS native GUI
prefs = GUIPreferences(
    framework=GUIFramework.MACOS_NATIVE,
    enable_translucency=True,
    performance_mode=False
)

bridge = create_gui_from_preferences(prefs)
bridge.run()
```

### Interactive Selection
```python
from gui_bridge import create_interactive_gui_selector

bridge = create_interactive_gui_selector()
bridge.run()
```

## 🔧 Configuration

### GUI Preferences
```python
@dataclass
class GUIPreferences:
    framework: GUIFramework = GUIFramework.AUTO
    enable_translucency: bool = True
    respect_accessibility: bool = True
    performance_mode: bool = False
    blur_radius_base: float = 15.0
    blur_radius_surface: float = 8.0
```

### Performance Tuning
```python
# Adjust blur radius for performance
window.update_blur_radius(base_radius=10.0, surface_radius=5.0)

# Enable performance mode
prefs = GUIPreferences(performance_mode=True)
```

### Accessibility
```python
# Toggle transparency at runtime
bridge.toggle_transparency()

# Check accessibility settings
window.reduce_transparency  # Respects system "Reduce Transparency" setting
```

## 📋 Requirements

### System Requirements
- **macOS**: Required for native GUI features
- **Python 3.8+**: Core runtime
- **PyObjC**: Python-Objective-C bridge

### Dependencies
```txt
pyobjc-core>=10.0
pyobjc-framework-Cocoa>=10.0
pyobjc-framework-Quartz>=10.0
```

### Installation
```bash
# Automatic installation via launch script
./launch.sh

# Manual installation
pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz
```

## 🧪 Testing

### Test Suite
```bash
# Test GUI logic (no GUI frameworks required)
python3 test_gui_logic.py

# Test macOS implementation (requires PyObjC)
python3 test_macos_gui.py
```

### Validation
- ✅ Framework selection logic
- ✅ Graceful fallback behavior
- ✅ Type safety and imports
- ✅ Performance characteristics
- ✅ Accessibility compliance

## 🎨 Visual Design

### Color Scheme (Optimized for Translucency)
```python
colors = {
    'bg_primary': (0.12, 0.12, 0.18, 0.85),      # Semi-transparent dark
    'bg_secondary': (0.19, 0.20, 0.27, 0.90),    # Slightly less transparent
    'bg_tertiary': (0.27, 0.28, 0.35, 0.95),     # Surface layer
    'text_primary': (0.80, 0.84, 0.96, 1.0),     # High contrast text
    'accent_blue': (0.54, 0.71, 0.98, 1.0),      # Accent color
    # ... additional colors
}
```

### Visual Effects
- **Base Layer**: WindowBackground material with 15px blur
- **Surface Layer**: Sidebar material with 8px blur and 12px corner radius
- **Dynamic Contrast**: Automatic text color adjustment for readability
- **System Integration**: Respects Dark/Light mode preferences

## 🔄 Migration & Compatibility

### Backward Compatibility
- **Existing Functionality**: All original features preserved
- **Tkinter Fallback**: Seamless fallback to original implementation
- **Cross-Platform**: Works on non-macOS systems via tkinter
- **Configuration**: Existing config files remain compatible

### Migration Path
1. **Automatic**: No changes needed - launch script handles everything
2. **Gradual**: Can switch between frameworks at runtime
3. **Rollback**: Easy fallback to tkinter if issues arise

## 🚀 Performance

### Optimization Targets
- **Frame Time**: <0.5ms for blur operations
- **Memory Usage**: Comparable to native Cocoa apps
- **Startup Time**: <2s window creation
- **Responsiveness**: Smooth, fluid interactions

### Monitoring
```python
# Performance testing
python3 test_gui_logic.py  # Includes performance validation
```

## 🛠️ Development

### Adding New Features
1. **macOS Native**: Add to `MacOSTranslucentWindow` class
2. **Cross-Platform**: Add to `gui_bridge.py` wrapper
3. **Testing**: Update test suites accordingly

### Debugging
```python
# Enable debug mode
import os
os.environ['GUI_DEBUG'] = '1'

# Check framework info
bridge.get_framework_info()
```

## 📚 References

### Apple Documentation
- [NSVisualEffectView](https://developer.apple.com/documentation/appkit/nsvisualeffectview)
- [Visual Effects](https://developer.apple.com/design/human-interface-guidelines/visual-effects)
- [Accessibility Guidelines](https://developer.apple.com/accessibility/)

### PyObjC Documentation
- [PyObjC Framework](https://pyobjc.readthedocs.io/)
- [Cocoa Bindings](https://pyobjc.readthedocs.io/en/latest/tutorials/intro.html)

---

## 🎉 Summary

This implementation successfully delivers:

✅ **Native macOS translucency** with NSVisualEffectView  
✅ **Layered visual effects** with different blur radii  
✅ **Dynamic color adaptation** for optimal contrast  
✅ **Performance optimization** targeting <0.5ms frame times  
✅ **Accessibility compliance** with WCAG 2.1 standards  
✅ **Graceful fallback** to tkinter on non-macOS systems  
✅ **Seamless integration** preserving all existing functionality  

The GUI bridge architecture ensures users get the best possible experience on their platform while maintaining full compatibility and functionality across all systems. 