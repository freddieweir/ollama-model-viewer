#!/usr/bin/env python3
"""
🧪 Test Script for macOS Translucent GUI Implementation
Verifies that all components work correctly before integration.
"""

import sys
import platform
import traceback

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import macos_gui
        print("✅ macOS GUI module imported successfully")
        
        if macos_gui.MACOS_AVAILABLE:
            print("✅ PyObjC frameworks available")
        else:
            print("⚠️ PyObjC frameworks not available")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import macOS GUI module: {e}")
        return False
    
    try:
        import gui_bridge
        print("✅ GUI bridge module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import GUI bridge module: {e}")
        return False
    
    return True

def test_window_creation():
    """Test creating a translucent window."""
    print("\n🪟 Testing window creation...")
    
    try:
        from macos_gui import MacOSTranslucentWindow
        
        # Create window (don't show it)
        window = MacOSTranslucentWindow("Test Window", 800, 600)
        print("✅ Translucent window created successfully")
        
        # Test content area creation
        content_view = window.create_content_area()
        if content_view:
            print("✅ Content area created successfully")
        else:
            print("❌ Failed to create content area")
            return False
            
        # Test transparency toggle
        window.toggle_transparency()
        print("✅ Transparency toggle works")
        
        return True
        
    except Exception as e:
        print(f"❌ Window creation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 macOS Translucent GUI Test Suite")
    print("=" * 40)
    
    # System check
    system = platform.system()
    print(f"🖥️ System: {system}")
    
    if system != "Darwin":
        print("⚠️ Not running on macOS - some tests may fail")
    
    print("")
    
    # Run basic import test
    if test_imports():
        print("✅ Import tests passed")
        if system == "Darwin":
            test_window_creation()
    else:
        print("❌ Import tests failed")

if __name__ == "__main__":
    main() 