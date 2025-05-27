#!/usr/bin/env python3
"""
🚀 Ollama Model Viewer - ADHD-Friendly Desktop App
A beautiful, interactive desktop application for viewing and managing Ollama models.

Features:
- 🎨 Color-coded models based on usage recency
- 📊 Model capabilities and storage information
- 🎯 ADHD-friendly UI with clear navigation and emojis
- ⚡ Real-time model status and information
"""

import sys
import os
import json
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# Import the virtual environment manager
import os
sys.path.append(os.path.expanduser('~/py-utils'))
from module_venv import AutoVirtualEnvironment

class OllamaModelViewer:
    """Main application class for the Ollama Model Viewer."""
    
    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.models_data = []
        self.filtered_models = []
        self.current_sort = "name"
        self.sort_reverse = False
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar()
        
        # Color scheme for ADHD-friendly design
        self.colors = {
            'bg_primary': '#1e1e2e',      # Dark background
            'bg_secondary': '#313244',     # Slightly lighter background
            'bg_tertiary': '#45475a',      # Card backgrounds
            'text_primary': '#cdd6f4',     # Main text
            'text_secondary': '#bac2de',   # Secondary text
            'accent_green': '#a6e3a1',     # Recently used (< 2 weeks)
            'accent_yellow': '#f9e2af',    # Moderately used (2-4 weeks)
            'accent_red': '#f38ba8',       # Old models (1+ month)
            'accent_blue': '#89b4fa',      # Accent color
            'accent_purple': '#cba6f7',    # Special highlights
            'border': '#6c7086',           # Borders
            'success': '#a6e3a1',          # Success states
            'warning': '#f9e2af',          # Warning states
            'error': '#f38ba8'             # Error states
        }
        
        self.setup_ui()
        self.load_models()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Configure main window
        self.root.title("🚀 Ollama Model Viewer")
        self.root.geometry("1400x900")
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Configure styles
        self.setup_styles()
        
        # Create main layout
        self.create_header()
        self.create_toolbar()
        self.create_model_list()
        self.create_status_bar()
        
        # Bind events
        self.search_var.trace('w', self.on_search_change)
        self.filter_var.trace('w', self.on_filter_change)
        
    def setup_styles(self):
        """Configure ttk styles for consistent theming."""
        style = ttk.Style()
        
        # Configure treeview style
        style.theme_use('clam')
        
        style.configure('Custom.Treeview',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_tertiary'],
                       borderwidth=0,
                       font=('SF Pro Display', 11))
        
        style.configure('Custom.Treeview.Heading',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=('SF Pro Display', 12, 'bold'))
        
        # Configure other styles
        style.configure('Custom.TFrame',
                       background=self.colors['bg_primary'])
        
        style.configure('Custom.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('SF Pro Display', 11))
        
        style.configure('Header.TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['accent_blue'],
                       font=('SF Pro Display', 24, 'bold'))
        
        style.configure('Custom.TEntry',
                       fieldbackground=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       insertcolor=self.colors['text_primary'])
        
        style.configure('Custom.TCombobox',
                       fieldbackground=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1)
        
    def create_header(self):
        """Create the application header."""
        header_frame = ttk.Frame(self.root, style='Custom.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Title
        title_label = ttk.Label(header_frame, 
                               text="🚀 Ollama Model Viewer", 
                               style='Header.TLabel')
        title_label.pack(side='left')
        
        # Refresh button
        refresh_btn = tk.Button(header_frame,
                               text="🔄 Refresh",
                               command=self.refresh_models,
                               bg=self.colors['accent_blue'],
                               fg=self.colors['bg_primary'],
                               font=('SF Pro Display', 12, 'bold'),
                               relief='flat',
                               padx=20,
                               pady=8,
                               cursor='hand2')
        refresh_btn.pack(side='right')
        
    def create_toolbar(self):
        """Create the toolbar with search and filter options."""
        toolbar_frame = ttk.Frame(self.root, style='Custom.TFrame')
        toolbar_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Search section
        search_frame = ttk.Frame(toolbar_frame, style='Custom.TFrame')
        search_frame.pack(side='left', fill='x', expand=True)
        
        search_label = ttk.Label(search_frame, text="🔍 Search:", style='Custom.TLabel')
        search_label.pack(side='left', padx=(0, 10))
        
        search_entry = ttk.Entry(search_frame, 
                                textvariable=self.search_var,
                                style='Custom.TEntry',
                                font=('SF Pro Display', 11),
                                width=30)
        search_entry.pack(side='left', padx=(0, 20))
        
        # Filter section
        filter_label = ttk.Label(toolbar_frame, text="🎯 Filter:", style='Custom.TLabel')
        filter_label.pack(side='left', padx=(0, 10))
        
        filter_combo = ttk.Combobox(toolbar_frame,
                                   textvariable=self.filter_var,
                                   style='Custom.TCombobox',
                                   values=['All Models', 'Recently Used (< 2 weeks)', 
                                          'Moderately Used (2-4 weeks)', 'Old Models (1+ month)',
                                          'Text Models', 'Vision Models', 'Large Models (>10GB)',
                                          'Small Models (<5GB)'],
                                   state='readonly',
                                   width=25)
        filter_combo.set('All Models')
        filter_combo.pack(side='left', padx=(0, 20))
        
        # Sort section
        sort_label = ttk.Label(toolbar_frame, text="📊 Sort:", style='Custom.TLabel')
        sort_label.pack(side='left', padx=(0, 10))
        
        sort_combo = ttk.Combobox(toolbar_frame,
                                 values=['Name', 'Size', 'Last Modified', 'Usage Frequency'],
                                 state='readonly',
                                 width=15)
        sort_combo.set('Name')
        sort_combo.bind('<<ComboboxSelected>>', self.on_sort_change)
        sort_combo.pack(side='left')
        
    def create_model_list(self):
        """Create the main model list view."""
        # Create frame for the treeview and scrollbars
        list_frame = ttk.Frame(self.root, style='Custom.TFrame')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        # Create treeview with columns
        columns = ('name', 'size', 'modified', 'capabilities', 'status', 'id')
        self.tree = ttk.Treeview(list_frame, 
                                columns=columns, 
                                show='headings',
                                style='Custom.Treeview',
                                height=20)
        
        # Configure column headings and widths
        self.tree.heading('name', text='📝 Model Name', command=lambda: self.sort_by_column('name'))
        self.tree.heading('size', text='💾 Size', command=lambda: self.sort_by_column('size'))
        self.tree.heading('modified', text='🕒 Last Modified', command=lambda: self.sort_by_column('modified'))
        self.tree.heading('capabilities', text='⚡ Capabilities', command=lambda: self.sort_by_column('capabilities'))
        self.tree.heading('status', text='🎯 Status', command=lambda: self.sort_by_column('status'))
        self.tree.heading('id', text='🔑 Model ID', command=lambda: self.sort_by_column('id'))
        
        # Configure column widths
        self.tree.column('name', width=350, minwidth=200)
        self.tree.column('size', width=100, minwidth=80)
        self.tree.column('modified', width=150, minwidth=120)
        self.tree.column('capabilities', width=200, minwidth=150)
        self.tree.column('status', width=150, minwidth=120)
        self.tree.column('id', width=200, minwidth=150)
        
        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.on_model_double_click)
        
    def create_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self.root, style='Custom.TFrame')
        status_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, 
                                     text="Ready", 
                                     style='Custom.TLabel')
        self.status_label.pack(side='left')
        
        # Model count label
        self.count_label = ttk.Label(status_frame, 
                                    text="", 
                                    style='Custom.TLabel')
        self.count_label.pack(side='right')
        
    def load_models(self):
        """Load Ollama models data."""
        self.update_status("🔄 Loading models...")
        
        try:
            # Run ollama list command
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True)
            
            self.models_data = self.parse_ollama_output(result.stdout)
            self.filtered_models = self.models_data.copy()
            self.populate_tree()
            self.update_status(f"✅ Loaded {len(self.models_data)} models")
            
        except subprocess.CalledProcessError as e:
            self.update_status("❌ Error: Ollama not found or not running")
            messagebox.showerror("Error", "Could not connect to Ollama. Please ensure Ollama is installed and running.")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def parse_ollama_output(self, output: str) -> List[Dict]:
        """Parse the output from 'ollama list' command."""
        models = []
        lines = output.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            if not line.strip():
                continue
                
            parts = line.split()
            if len(parts) >= 4:
                name = parts[0]
                model_id = parts[1]
                size = parts[2] + " " + parts[3]
                modified = " ".join(parts[4:])
                
                # Determine age category and color
                age_category, color = self.get_age_category(modified)
                
                # Determine capabilities based on model name
                capabilities = self.determine_capabilities(name)
                
                model_data = {
                    'name': name,
                    'id': model_id,
                    'size': size,
                    'modified': modified,
                    'age_category': age_category,
                    'color': color,
                    'capabilities': capabilities,
                    'status': self.get_model_status(name)
                }
                
                models.append(model_data)
        
        return models
    
    def get_age_category(self, modified_str: str) -> Tuple[str, str]:
        """Determine the age category and color for a model based on last modified time."""
        try:
            # Parse the modified string to determine age
            if 'day' in modified_str:
                days = int(modified_str.split()[0])
                if days <= 14:
                    return "Recently Used", self.colors['accent_green']
                elif days <= 28:
                    return "Moderately Used", self.colors['accent_yellow']
                else:
                    return "Old Model", self.colors['accent_red']
            elif 'week' in modified_str:
                weeks = int(modified_str.split()[0])
                if weeks <= 2:
                    return "Recently Used", self.colors['accent_green']
                elif weeks <= 4:
                    return "Moderately Used", self.colors['accent_yellow']
                else:
                    return "Old Model", self.colors['accent_red']
            elif 'month' in modified_str:
                return "Old Model", self.colors['accent_red']
            else:
                # Default for unclear time formats
                return "Unknown", self.colors['text_secondary']
        except:
            return "Unknown", self.colors['text_secondary']
    
    def determine_capabilities(self, model_name: str) -> str:
        """Determine model capabilities based on the model name."""
        capabilities = []
        
        # Text capabilities (all models have this)
        capabilities.append("📝 Text")
        
        # Vision capabilities
        if any(keyword in model_name.lower() for keyword in ['vision', 'vl', 'visual', 'llava', 'clip']):
            capabilities.append("👁️ Vision")
        
        # Code capabilities
        if any(keyword in model_name.lower() for keyword in ['code', 'coder', 'coding']):
            capabilities.append("💻 Code")
        
        # Embedding capabilities
        if 'embed' in model_name.lower():
            capabilities.append("🔗 Embed")
        
        # Tool use capabilities (common in newer models)
        if any(keyword in model_name.lower() for keyword in ['tool', 'function', 'agent']):
            capabilities.append("🛠️ Tools")
        
        # Reasoning capabilities
        if any(keyword in model_name.lower() for keyword in ['r1', 'reasoning', 'think']):
            capabilities.append("🧠 Reasoning")
        
        return " ".join(capabilities) if capabilities else "📝 Text"
    
    def get_model_status(self, model_name: str) -> str:
        """Get the current status of a model."""
        # This could be extended to check if model is currently loaded/running
        return "🟢 Available"
    
    def populate_tree(self):
        """Populate the treeview with model data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add models to tree
        for model in self.filtered_models:
            item_id = self.tree.insert('', 'end', values=(
                model['name'],
                model['size'],
                model['modified'],
                model['capabilities'],
                model['status'],
                model['id'][:12] + "..."  # Truncate ID for display
            ))
            
            # Set row color based on age category
            self.tree.set(item_id, 'name', f"● {model['name']}")
            
        # Update count
        self.count_label.config(text=f"📊 {len(self.filtered_models)} models displayed")
    
    def refresh_models(self):
        """Refresh the model list."""
        self.load_models()
    
    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def on_search_change(self, *args):
        """Handle search text changes."""
        search_term = self.search_var.get().lower()
        self.apply_filters()
    
    def on_filter_change(self, *args):
        """Handle filter changes."""
        self.apply_filters()
    
    def apply_filters(self):
        """Apply search and filter criteria to the model list."""
        search_term = self.search_var.get().lower()
        filter_value = self.filter_var.get()
        
        self.filtered_models = []
        
        for model in self.models_data:
            # Apply search filter
            if search_term and search_term not in model['name'].lower():
                continue
            
            # Apply category filter
            if filter_value == 'Recently Used (< 2 weeks)' and model['age_category'] != 'Recently Used':
                continue
            elif filter_value == 'Moderately Used (2-4 weeks)' and model['age_category'] != 'Moderately Used':
                continue
            elif filter_value == 'Old Models (1+ month)' and model['age_category'] != 'Old Model':
                continue
            elif filter_value == 'Vision Models' and '👁️ Vision' not in model['capabilities']:
                continue
            elif filter_value == 'Text Models' and '📝 Text' not in model['capabilities']:
                continue
            elif filter_value == 'Large Models (>10GB)':
                try:
                    size_gb = float(model['size'].split()[0])
                    if size_gb <= 10:
                        continue
                except:
                    continue
            elif filter_value == 'Small Models (<5GB)':
                try:
                    size_gb = float(model['size'].split()[0])
                    if size_gb >= 5:
                        continue
                except:
                    continue
            
            self.filtered_models.append(model)
        
        self.populate_tree()
    
    def sort_by_column(self, column: str):
        """Sort the model list by the specified column."""
        if self.current_sort == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.current_sort = column
            self.sort_reverse = False
        
        if column == 'name':
            self.filtered_models.sort(key=lambda x: x['name'], reverse=self.sort_reverse)
        elif column == 'size':
            self.filtered_models.sort(key=lambda x: float(x['size'].split()[0]), reverse=self.sort_reverse)
        elif column == 'modified':
            self.filtered_models.sort(key=lambda x: x['modified'], reverse=self.sort_reverse)
        
        self.populate_tree()
    
    def on_sort_change(self, event):
        """Handle sort dropdown changes."""
        sort_value = event.widget.get()
        if sort_value == 'Name':
            self.sort_by_column('name')
        elif sort_value == 'Size':
            self.sort_by_column('size')
        elif sort_value == 'Last Modified':
            self.sort_by_column('modified')
    
    def on_model_double_click(self, event):
        """Handle double-click on a model."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][0].replace('● ', '')
            self.show_model_details(model_name)
    
    def show_model_details(self, model_name: str):
        """Show detailed information about a model."""
        # Find the model data
        model_data = None
        for model in self.models_data:
            if model['name'] == model_name:
                model_data = model
                break
        
        if not model_data:
            return
        
        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"📋 Model Details: {model_name}")
        detail_window.geometry("600x500")
        detail_window.configure(bg=self.colors['bg_primary'])
        
        # Create scrollable frame
        canvas = tk.Canvas(detail_window, bg=self.colors['bg_primary'])
        scrollbar = ttk.Scrollbar(detail_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Custom.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add model details
        details = [
            ("📝 Name", model_data['name']),
            ("🔑 ID", model_data['id']),
            ("💾 Size", model_data['size']),
            ("🕒 Last Modified", model_data['modified']),
            ("⚡ Capabilities", model_data['capabilities']),
            ("🎯 Status", model_data['status']),
            ("🎨 Age Category", model_data['age_category'])
        ]
        
        for i, (label, value) in enumerate(details):
            label_widget = ttk.Label(scrollable_frame, 
                                   text=label, 
                                   style='Custom.TLabel',
                                   font=('SF Pro Display', 12, 'bold'))
            label_widget.pack(anchor='w', padx=20, pady=(10, 5))
            
            value_widget = ttk.Label(scrollable_frame, 
                                   text=value, 
                                   style='Custom.TLabel',
                                   font=('SF Pro Display', 11))
            value_widget.pack(anchor='w', padx=40, pady=(0, 10))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()

def main():
    """Main function to run the application."""
    # Set up virtual environment with required packages
    venv_manager = AutoVirtualEnvironment(
        custom_name="venv-ollama-model-viewer",
        auto_packages=[
            'tkinter',  # Usually comes with Python
        ]
    )
    
    # Auto-switch to virtual environment if needed
    venv_manager.auto_switch()
    
    # Create and run the application
    app = OllamaModelViewer()
    app.run()

if __name__ == "__main__":
    main() 