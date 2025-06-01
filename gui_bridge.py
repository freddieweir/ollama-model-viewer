#!/usr/bin/env python3
"""
🌉 GUI Bridge for Ollama Model Viewer
Seamlessly integrates tkinter and macOS native GUI implementations.

This bridge allows users to choose between:
- 🖥️ Tkinter (Cross-platform compatibility)
- 🍎 macOS Native (Translucent effects, native performance)
"""

import sys
import os
import platform
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# Import the original tkinter implementation
from ollama_model_viewer import OllamaModelViewer as TkinterModelViewer

# Import the new macOS implementation
try:
    from macos_gui import MacOSTranslucentWindow, MacOSModelListView, MACOS_AVAILABLE
except ImportError:
    MACOS_AVAILABLE = False
    MacOSTranslucentWindow = None
    MacOSModelListView = None


class GUIFramework(Enum):
    """Available GUI frameworks."""
    TKINTER = "tkinter"
    MACOS_NATIVE = "macos_native"
    AUTO = "auto"


@dataclass
class GUIPreferences:
    """User preferences for GUI selection and behavior."""
    framework: GUIFramework = GUIFramework.AUTO
    enable_translucency: bool = True
    respect_accessibility: bool = True
    performance_mode: bool = False
    blur_radius_base: float = 15.0
    blur_radius_surface: float = 8.0


class ModelViewerGUIBridge:
    """Bridge between different GUI implementations for the Ollama Model Viewer."""
    
    def __init__(self, preferences: Optional[GUIPreferences] = None):
        """Initialize the GUI bridge with user preferences."""
        self.preferences = preferences or GUIPreferences()
        self.current_framework = None
        self.viewer_instance = None
        self.models_data = []
        
        # Determine the best GUI framework to use
        self.selected_framework = self._determine_framework()
        
        print(f"🎨 GUI Bridge initialized with {self.selected_framework.value} framework")
    
    def _determine_framework(self) -> GUIFramework:
        """Determine which GUI framework to use based on system and preferences."""
        if self.preferences.framework == GUIFramework.AUTO:
            # Auto-detection logic
            if platform.system() == "Darwin" and MACOS_AVAILABLE:
                if self.preferences.enable_translucency:
                    print("🍎 Auto-detected: macOS with translucency support available")
                    return GUIFramework.MACOS_NATIVE
                else:
                    print("🍎 Auto-detected: macOS, but translucency disabled")
                    return GUIFramework.TKINTER
            else:
                print("🖥️ Auto-detected: Non-macOS system or PyObjC unavailable")
                return GUIFramework.TKINTER
        
        elif self.preferences.framework == GUIFramework.MACOS_NATIVE:
            if not MACOS_AVAILABLE:
                print("⚠️ macOS native GUI requested but not available, falling back to tkinter")
                return GUIFramework.TKINTER
            if platform.system() != "Darwin":
                print("⚠️ macOS native GUI requested on non-macOS system, falling back to tkinter")
                return GUIFramework.TKINTER
            return GUIFramework.MACOS_NATIVE
        
        else:  # TKINTER
            return GUIFramework.TKINTER
    
    def initialize_gui(self) -> bool:
        """Initialize the selected GUI framework."""
        try:
            if self.selected_framework == GUIFramework.MACOS_NATIVE:
                return self._initialize_macos_gui()
            else:
                return self._initialize_tkinter_gui()
        except Exception as e:
            print(f"❌ Failed to initialize {self.selected_framework.value} GUI: {e}")
            if self.selected_framework == GUIFramework.MACOS_NATIVE:
                print("🔄 Falling back to tkinter GUI...")
                self.selected_framework = GUIFramework.TKINTER
                return self._initialize_tkinter_gui()
            return False
    
    def _initialize_macos_gui(self) -> bool:
        """Initialize the macOS native GUI implementation."""
        print("🚀 Initializing macOS translucent GUI...")
        
        try:
            # Create the translucent window
            self.macos_window = MacOSTranslucentWindow(
                title="🚀 Ollama Model Viewer - macOS Native",
                width=1400,
                height=900
            )
            
            # Configure performance settings
            if self.preferences.performance_mode:
                self.macos_window.update_blur_radius(
                    self.preferences.blur_radius_base,
                    self.preferences.blur_radius_surface
                )
            
            # Create content views
            content_view = self.macos_window.create_content_area()
            self.macos_model_list = MacOSModelListView(content_view, self.macos_window.colors)
            
            # Create a wrapper that mimics the tkinter interface
            self.viewer_instance = MacOSViewerWrapper(
                window=self.macos_window,
                model_list=self.macos_model_list,
                bridge=self
            )
            
            self.current_framework = GUIFramework.MACOS_NATIVE
            print("✅ macOS GUI initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize macOS GUI: {e}")
            return False
    
    def _initialize_tkinter_gui(self) -> bool:
        """Initialize the tkinter GUI implementation."""
        print("🚀 Initializing tkinter GUI...")
        
        try:
            self.viewer_instance = TkinterModelViewer()
            self.current_framework = GUIFramework.TKINTER
            print("✅ tkinter GUI initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize tkinter GUI: {e}")
            return False
    
    def run(self):
        """Run the application with the selected GUI framework."""
        if not self.viewer_instance:
            if not self.initialize_gui():
                print("❌ Failed to initialize any GUI framework")
                return
        
        print(f"🎯 Running Ollama Model Viewer with {self.current_framework.value} GUI")
        print("🔧 Features enabled:")
        
        if self.current_framework == GUIFramework.MACOS_NATIVE:
            print("  ✨ Native macOS translucency")
            print("  🌈 Layered visual effects")
            print("  ♿ Accessibility compliance")
            print("  ⚡ Performance optimization")
        else:
            print("  🖥️ Cross-platform compatibility")
            print("  🎨 Custom theming")
            print("  ⚡ Lightweight implementation")
        
        try:
            self.viewer_instance.run()
        except KeyboardInterrupt:
            print("\n👋 Application terminated by user")
        except Exception as e:
            print(f"❌ Application error: {e}")
    
    def switch_framework(self, new_framework: GUIFramework) -> bool:
        """Switch to a different GUI framework at runtime."""
        if new_framework == self.current_framework:
            print(f"ℹ️ Already using {new_framework.value} framework")
            return True
        
        print(f"🔄 Switching from {self.current_framework.value} to {new_framework.value}...")
        
        # Save current state
        current_data = self.get_models_data()
        
        # Clean up current instance
        if self.viewer_instance:
            try:
                if hasattr(self.viewer_instance, 'root'):
                    self.viewer_instance.root.quit()
                elif hasattr(self.viewer_instance, 'window'):
                    self.viewer_instance.window.close()
            except:
                pass
        
        # Switch framework
        old_framework = self.selected_framework
        self.selected_framework = new_framework
        
        if self.initialize_gui():
            # Restore data
            self.set_models_data(current_data)
            print(f"✅ Successfully switched to {new_framework.value}")
            return True
        else:
            # Fallback to original framework
            print(f"❌ Failed to switch to {new_framework.value}, reverting...")
            self.selected_framework = old_framework
            self.initialize_gui()
            self.set_models_data(current_data)
            return False
    
    def get_models_data(self) -> List[Dict]:
        """Get current models data from the active GUI."""
        if self.viewer_instance:
            if hasattr(self.viewer_instance, 'models_data'):
                return self.viewer_instance.models_data
            elif hasattr(self.viewer_instance, 'get_models_data'):
                return self.viewer_instance.get_models_data()
        return []
    
    def set_models_data(self, data: List[Dict]):
        """Set models data in the active GUI."""
        self.models_data = data
        if self.viewer_instance:
            if hasattr(self.viewer_instance, 'models_data'):
                self.viewer_instance.models_data = data
                if hasattr(self.viewer_instance, 'populate_tree'):
                    self.viewer_instance.populate_tree()
            elif hasattr(self.viewer_instance, 'set_models_data'):
                self.viewer_instance.set_models_data(data)
    
    def toggle_transparency(self) -> bool:
        """Toggle transparency effects (macOS only)."""
        if self.current_framework == GUIFramework.MACOS_NATIVE and self.viewer_instance:
            if hasattr(self.viewer_instance, 'toggle_transparency'):
                self.viewer_instance.toggle_transparency()
                return True
        return False
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get information about the current GUI framework."""
        return {
            'current_framework': self.current_framework.value if self.current_framework else None,
            'available_frameworks': [f.value for f in GUIFramework if f != GUIFramework.AUTO],
            'macos_available': MACOS_AVAILABLE,
            'platform': platform.system(),
            'translucency_enabled': (
                self.current_framework == GUIFramework.MACOS_NATIVE and 
                self.preferences.enable_translucency
            ),
            'preferences': {
                'framework': self.preferences.framework.value,
                'enable_translucency': self.preferences.enable_translucency,
                'respect_accessibility': self.preferences.respect_accessibility,
                'performance_mode': self.preferences.performance_mode,
            }
        }


class MacOSViewerWrapper:
    """Wrapper to make macOS GUI compatible with tkinter interface."""
    
    def __init__(self, window: 'MacOSTranslucentWindow', model_list: 'MacOSModelListView', bridge: 'ModelViewerGUIBridge'):
        """Initialize the wrapper."""
        self.window = window
        self.model_list = model_list
        self.bridge = bridge
        self.models_data = []
        
        # Import and integrate the original business logic
        self._setup_business_logic()
    
    def _setup_business_logic(self):
        """Set up the business logic from the original implementation."""
        # Create a minimal tkinter instance to reuse existing logic
        self.tkinter_backend = TkinterModelViewer()
        
        # Don't show the tkinter GUI, just use its logic
        self.tkinter_backend.root.withdraw()
        
        # Copy important attributes
        self.deletion_queue = self.tkinter_backend.deletion_queue
        self.starred_models = self.tkinter_backend.starred_models
        self.openwebui_data_path = self.tkinter_backend.openwebui_data_path
    
    def run(self):
        """Run the macOS application."""
        # Load models from the tkinter backend
        self.tkinter_backend.load_models()
        self.models_data = self.tkinter_backend.models_data
        
        # Update the macOS GUI with the data
        self.model_list.update_data(self.models_data)
        
        # Show the window and run
        self.window.show()
        self.window.run()
    
    def load_models(self):
        """Load models using the tkinter backend logic."""
        if self.tkinter_backend:
            self.tkinter_backend.load_models()
            self.models_data = self.tkinter_backend.models_data
            self.model_list.update_data(self.models_data)
    
    def refresh_models(self):
        """Refresh models data."""
        self.load_models()
    
    def toggle_transparency(self):
        """Toggle transparency effects."""
        self.window.toggle_transparency()
    
    def get_models_data(self) -> List[Dict]:
        """Get current models data."""
        return self.models_data
    
    def set_models_data(self, data: List[Dict]):
        """Set models data."""
        self.models_data = data
        self.model_list.update_data(data)


def create_gui_from_preferences(preferences: Optional[GUIPreferences] = None) -> ModelViewerGUIBridge:
    """Create a GUI bridge instance with the specified preferences."""
    return ModelViewerGUIBridge(preferences)


def create_interactive_gui_selector() -> ModelViewerGUIBridge:
    """Interactively ask user to select GUI framework and preferences."""
    print("\n🎨 Ollama Model Viewer - GUI Framework Selection")
    print("=" * 50)
    
    # Check system capabilities
    system = platform.system()
    print(f"🖥️ System: {system}")
    print(f"🍎 macOS Native GUI Available: {'Yes' if MACOS_AVAILABLE else 'No'}")
    
    if system == "Darwin" and MACOS_AVAILABLE:
        print("\n🎯 Available GUI options:")
        print("A. 🍎 macOS Native (Recommended) - Translucent effects, native performance")
        print("B. 🖥️ Tkinter - Cross-platform compatibility")
        print("C. 🤖 Auto-detect (Recommended for most users)")
        
        while True:
            choice = input("\n🤔 Select GUI framework (A/B/C): ").strip().upper()
            if choice in ['A', 'B', 'C']:
                break
            print("❌ Please enter A, B, or C")
        
        if choice == 'A':
            framework = GUIFramework.MACOS_NATIVE
            # Ask about translucency preferences
            translucency = input("✨ Enable translucency effects? (Y/n): ").strip().lower()
            enable_translucency = translucency != 'n'
        elif choice == 'B':
            framework = GUIFramework.TKINTER
            enable_translucency = False
        else:  # C
            framework = GUIFramework.AUTO
            enable_translucency = True
    else:
        print(f"\n🖥️ Using tkinter GUI (macOS native not available on {system})")
        framework = GUIFramework.TKINTER
        enable_translucency = False
    
    # Create preferences
    preferences = GUIPreferences(
        framework=framework,
        enable_translucency=enable_translucency,
        respect_accessibility=True,
        performance_mode=False
    )
    
    return ModelViewerGUIBridge(preferences)


def main():
    """Main entry point for the GUI bridge."""
    print("🚀 Ollama Model Viewer - Enhanced GUI Bridge")
    
    try:
        # Create GUI with interactive selection
        gui_bridge = create_interactive_gui_selector()
        
        # Initialize and run
        if gui_bridge.initialize_gui():
            gui_bridge.run()
        else:
            print("❌ Failed to initialize GUI")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 