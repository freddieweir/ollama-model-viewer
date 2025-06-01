#!/usr/bin/env python3
"""
🧪 Test script to verify tkinter availability
Quick test to ensure GUI components will work before running the main app.
"""

import sys

def test_tkinter():
    """Test if tkinter is available and working."""
    try:
        print("🔍 Testing tkinter availability...")
        import tkinter as tk
        print("✅ tkinter imported successfully")
        
        # Create a simple test window
        print("🖼️ Creating test window...")
        root = tk.Tk()
        root.title("🧪 Tkinter Test")
        root.geometry("300x150")
        
        # Add a simple label
        label = tk.Label(root, text="✅ Tkinter is working!\n🚀 Ready to launch Ollama Model Viewer", 
                        font=('SF Pro Display', 12), 
                        pady=20)
        label.pack()
        
        # Add close button
        button = tk.Button(root, text="🎯 Close Test", command=root.quit,
                          font=('SF Pro Display', 10, 'bold'),
                          bg='#89b4fa', fg='white', pady=5)
        button.pack()
        
        print("🎯 Test window created successfully")
        print("📋 Close the test window to continue...")
        
        # Show window briefly
        root.after(3000, root.quit)  # Auto-close after 3 seconds
        root.mainloop()
        root.destroy()
        
        print("✅ tkinter test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ tkinter not available: {e}")
        print("💡 Solution: Install tkinter for your Python distribution")
        if sys.platform == "darwin":  # macOS
            print("   On macOS: tkinter should be included with Python")
            print("   Try: brew install python-tk")
        elif sys.platform.startswith("linux"):  # Linux
            print("   On Ubuntu/Debian: sudo apt-get install python3-tk")
            print("   On CentOS/RHEL: sudo yum install tkinter")
        return False
        
    except Exception as e:
        print(f"❌ tkinter test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Ollama Model Viewer - tkinter Test")
    print("=" * 50)
    
    if test_tkinter():
        print("\n🎉 All tests passed! You can now run the main application:")
        print("   python ollama_model_viewer.py")
    else:
        print("\n⚠️ Please fix tkinter issues before running the main app")
        sys.exit(1) 