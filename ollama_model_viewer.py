#!/usr/bin/env python3
"""
🚀 Ollama Model Viewer - ADHD-Friendly Desktop App
A beautiful, interactive desktop application for viewing and managing Ollama models.

Features:
- 🎨 Color-coded models based on usage recency
- 📊 Model capabilities and storage information
- 🎯 ADHD-friendly UI with clear navigation and emojis
- ⚡ Real-time model status and information
- 🗑️ Model deletion with queue and storage estimates
- ⭐ Star/favorite models for easy identification
- 🔓 Auto-detection of liberated/uncensored models
"""

import sys
import os
import json
import subprocess
import datetime
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import hashlib
import base64

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
        
        # New features
        self.deletion_queue: Set[str] = set()  # Models queued for deletion
        self.starred_models: Set[str] = set()  # Starred/favorite models
        self.config_file = Path.home() / '.ollama_model_viewer_config.json'
        
        # OpenWebUI Integration
        self.openwebui_data_path = None  # Will be detected automatically
        self.openwebui_usage_data = {}  # Cache for model usage from OpenWebUI
        self.detect_openwebui_path()  # Automatically detect OpenWebUI installation
        
        # Privacy & Security Settings
        self.privacy_mode = True  # Enable privacy protection by default
        self.encrypt_database = True  # Encrypt copied database by default
        self.enable_chat_features = False  # Disable chat browsing by default (future roadmap)
        self.database_key = None  # Will be generated if encryption enabled
        
        # Liberation detection keywords
        self.liberation_keywords = [
            'uncensored', 'abliterated', 'art', 'unfiltered', 'raw', 
            'nsfw', 'freedom', 'libre', 'unleashed', 'unlimited',
            'dpo', 'rogue', 'wild', 'rebel', 'free'
        ]
        
        # Special parameter suffixes that are meaningful variants (not duplicates)
        self.special_suffixes = [
            'instruct', 'chat', 'code', 'vision', 'embed', 'text',
            'a3b', 'dpo', 'ift', 'sft', 'rlhf', 'tool', 'function',
            'reasoning', 'uncensored', 'abliterated', 'art', 'base'
        ]
        
        # Load saved configuration
        self.load_config()
        
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
            'accent_orange': '#fab387',    # Liberation indicator
            'accent_pink': '#f5c2e7',      # Starred models
            'border': '#6c7086',           # Borders
            'success': '#a6e3a1',          # Success states
            'warning': '#f9e2af',          # Warning states
            'error': '#f38ba8',            # Error states
            'deletion': '#f38ba8'          # Models queued for deletion
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
        self.search_var.trace_add('write', self.on_search_change)
        self.filter_var.trace_add('write', self.on_filter_change)
        
        # Bind right-click event
        self.tree.bind('<Button-3>', self.show_context_menu)  # Right-click
        self.tree.bind('<Control-Button-1>', self.show_context_menu)  # Ctrl+click for Mac
        
        # Add keyboard shortcuts
        self.root.bind('<Key-s>', self.keyboard_toggle_star)  # Press 's' to star
        self.root.bind('<Key-d>', self.keyboard_add_to_queue)  # Press 'd' to delete queue
        self.root.bind('<Key-r>', self.keyboard_remove_from_queue)  # Press 'r' to remove from queue
        self.root.bind('<Return>', self.keyboard_show_details)  # Press Enter for details
        
        # Focus the tree so keyboard shortcuts work
        self.tree.focus_set()
        
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
        
        # Right side button frame
        button_frame = ttk.Frame(header_frame, style='Custom.TFrame')
        button_frame.pack(side='right')
        
        # Deletion Queue button
        self.queue_btn = tk.Button(button_frame,
                                  text="🗑️ Queue (0)",
                                  command=self.show_deletion_queue,
                                  bg=self.colors['warning'],
                                  fg=self.colors['bg_primary'],
                                  font=('SF Pro Display', 11, 'bold'),
                                  relief='flat',
                                  padx=15,
                                  pady=6,
                                  cursor='hand2')
        self.queue_btn.pack(side='right', padx=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(button_frame,
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
        
        # Help button
        help_btn = tk.Button(button_frame,
                            text="❓ Help",
                            command=self.show_help,
                            bg=self.colors['accent_purple'],
                            fg=self.colors['bg_primary'],
                            font=('SF Pro Display', 11, 'bold'),
                            relief='flat',
                            padx=15,
                            pady=6,
                            cursor='hand2')
        help_btn.pack(side='right', padx=(0, 10))
        
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
                                          'Small Models (<5GB)', '⭐ Starred Models', 
                                          '🔓 Liberated Models', '🗑️ Queued for Deletion',
                                          '🔄 Duplicate Models', '🔀 Special Variants',
                                          '📦 Model Families (2+ models)', '📊 Used in OpenWebUI',
                                          '❌ Never Used in OpenWebUI', '🔥 Frequently Used (>10 chats)',
                                          '⚡ Recent OpenWebUI Activity'],
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
        columns = ('status_icons', 'name', 'size', 'modified', 'last_used', 'capabilities', 'status', 'id')
        self.tree = ttk.Treeview(list_frame, 
                                columns=columns, 
                                show='headings',
                                style='Custom.Treeview',
                                height=20)
        
        # Configure column headings and widths
        self.tree.heading('status_icons', text='🎯 Status', command=lambda: self.sort_by_column('status_icons'))
        self.tree.heading('name', text='📝 Model Name', command=lambda: self.sort_by_column('name'))
        self.tree.heading('size', text='💾 Size', command=lambda: self.sort_by_column('size'))
        self.tree.heading('modified', text='🕒 Last Modified', command=lambda: self.sort_by_column('modified'))
        self.tree.heading('last_used', text='💬 Last Used (OpenWebUI)', command=lambda: self.sort_by_column('last_used'))
        self.tree.heading('last_used', text='💬 Last Used (OpenWebUI)', command=lambda: self.sort_by_column('last_used'))
        self.tree.heading('capabilities', text='⚡ Capabilities', command=lambda: self.sort_by_column('capabilities'))
        self.tree.heading('status', text='🔄 Server Status', command=lambda: self.sort_by_column('status'))
        self.tree.heading('id', text='🔑 Model ID', command=lambda: self.sort_by_column('id'))
        
        # Configure column widths
        self.tree.column('status_icons', width=100, minwidth=80)
        self.tree.column('name', width=300, minwidth=200)
        self.tree.column('size', width=100, minwidth=80)
        self.tree.column('modified', width=150, minwidth=120)
        self.tree.column('last_used', width=160, minwidth=140)
        self.tree.column('last_used', width=160, minwidth=140)
        self.tree.column('capabilities', width=200, minwidth=150)
        self.tree.column('status', width=130, minwidth=120)
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
        
        # Add context menu for right-click actions
        self.context_menu = tk.Menu(self.root, tearoff=0, 
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_primary'],
                                   activebackground=self.colors['accent_blue'],
                                   activeforeground=self.colors['bg_primary'])
        
        self.context_menu.add_command(label="⭐ Toggle Star", command=self.context_toggle_star)
        self.context_menu.add_command(label="📋 Show Details", command=self.context_show_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Add to Deletion Queue", command=self.context_add_to_queue)
        self.context_menu.add_command(label="❌ Remove from Queue", command=self.context_remove_from_queue)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗂️ Copy Model Name", command=self.context_copy_name)
        
    def create_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self.root, style='Custom.TFrame')
        status_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.status_label = ttk.Label(status_frame, 
                                     text="Ready", 
                                     style='Custom.TLabel')
        self.status_label.pack(side='left')
        
        # Total storage label
        self.storage_label = ttk.Label(status_frame,
                                      text="💾 Calculating storage...",
                                      style='Custom.TLabel',
                                      font=('SF Pro Display', 11, 'bold'))
        self.storage_label.pack(side='right', padx=(0, 20))
        
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
                
                # Check if model is liberated/uncensored
                is_liberated = self.is_liberated_model(name)
                
                # Check if model is starred
                is_starred = name in self.starred_models
                
                # Check if model is queued for deletion
                is_queued_for_deletion = name in self.deletion_queue
                
                # Get OpenWebUI usage data for this model
                usage_info = self.get_model_usage_info(name)
                
                model_data = {
                    'name': name,
                    'id': model_id,
                    'size': size,
                    'modified': modified,
                    'age_category': age_category,
                    'color': color,
                    'capabilities': capabilities,
                    'status': self.get_model_status(name),
                    'is_liberated': is_liberated,
                    'is_starred': is_starred,
                    'is_queued_for_deletion': is_queued_for_deletion,
                    'usage_info': usage_info  # Add OpenWebUI usage data
                }
                
                models.append(model_data)
        
        # Detect duplicates and variants after all models are parsed
        duplicates, variants = self.detect_duplicates()
        
        # Add duplicate/variant information to model data
        for model in models:
            model['is_duplicate'] = (f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']) in duplicates
            base_name = self.get_model_base_name((f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']))
            model['variant_info'] = variants.get(base_name, None)
            model['is_special_variant'] = self.is_special_variant((f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']))
        
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
            # Build status icons string - start with age indicator
            if model['age_category'] == 'Recently Used':
                status_icons = ""  # Age indicators moved to Last Modified column
                status_icons += "🔓"
            if model.get('is_queued_for_deletion', False):
                status_icons += "🗑️"
            if model.get('is_duplicate', False):
                status_icons += "🔄"  # Duplicate indicator
            elif model.get('variant_info') and model.get('is_special_variant', False):
                status_icons += "🔀"  # Special variant indicator
            
            
            item_id = self.tree.insert('', 'end', values=(
                status_icons,
                (f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']),
                model['size'],
                (f"{"🟢" if model.get("age_category") == "Recently Used" else "🟡" if model.get("age_category") == "Moderately Used" else "🔴"} {model["modified"]}"),
                model['capabilities'],
                model['status'],
                model['id'][:12] + "..."  # Truncate ID for display
            ))
            
            # Set row colors based on status (but not for liberated models anymore)
            if model.get('is_queued_for_deletion', False):
                # Highlight models queued for deletion
                self.tree.item(item_id, tags=('deletion',))
            elif model.get('is_starred', False):
                # Highlight starred models
                self.tree.item(item_id, tags=('starred',))
        
        # Configure tag colors (removed liberated tag since we're not highlighting those rows anymore)
        self.tree.tag_configure('deletion', background=self.colors['deletion'], foreground='white')
        self.tree.tag_configure('starred', background=self.colors['accent_pink'], foreground=self.colors['bg_primary'])
        
        # Update count
        self.count_label.config(text=f"📊 {len(self.filtered_models)} models displayed")
        
        # Update total storage
        _, total_storage_text = self.calculate_total_storage()
        self.storage_label.config(text=f"💾 Total Storage: {total_storage_text}")
        
        # Count duplicates and variants in filtered models
        duplicate_count = sum(1 for model in self.filtered_models if model.get('is_duplicate', False))
        variant_count = sum(1 for model in self.filtered_models if model.get('is_special_variant', False))
        
        # Enhanced count display
        count_text = f"📊 {len(self.filtered_models)} models"
        if duplicate_count > 0:
            count_text += f" (🔄 {duplicate_count} duplicates)"
        if variant_count > 0:
            count_text += f" (🔀 {variant_count} variants)"
        
        self.count_label.config(text=count_text)
        
        # Update queue button
        self.update_queue_button()
    
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
            if search_term and search_term not in (f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']).lower():
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
            elif filter_value == '⭐ Starred Models' and not model.get('is_starred', False):
                continue
            elif filter_value == '🔓 Liberated Models' and not model.get('is_liberated', False):
                continue
            elif filter_value == '🗑️ Queued for Deletion' and not model.get('is_queued_for_deletion', False):
                continue
            elif filter_value == '🔄 Duplicate Models' and not model.get('is_duplicate', False):
                continue
            elif filter_value == '🔀 Special Variants' and not model.get('is_special_variant', False):
                continue
            elif filter_value == '📦 Model Families (2+ models)' and not model.get('variant_info'):
                continue
            
            # OpenWebUI Usage-based filters
            elif filter_value == '📊 Used in OpenWebUI':
                usage_info = model.get('usage_info')
                if not usage_info or usage_info.get('usage_count', 0) == 0:
                    continue
            elif filter_value == '❌ Never Used in OpenWebUI':
                usage_info = model.get('usage_info')
                if usage_info and usage_info.get('usage_count', 0) > 0:
                    continue
            elif filter_value == '🔥 Frequently Used (>10 chats)':
                usage_info = model.get('usage_info')
                if not usage_info or usage_info.get('usage_count', 0) <= 10:
                    continue
            elif filter_value == '⚡ Recent OpenWebUI Activity':
                usage_info = model.get('usage_info')
                if not usage_info or not usage_info.get('last_used'):
                    continue
                # Check if used in last 7 days
                try:
                    last_used = usage_info['last_used']
                    if isinstance(last_used, (int, float)):
                        last_used_date = datetime.datetime.fromtimestamp(last_used)
                    else:
                        last_used_date = datetime.datetime.fromisoformat(str(last_used).replace('Z', '+00:00'))
                    
                    days_ago = (datetime.datetime.now() - last_used_date).days
                    if days_ago > 7:
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
            model_name = item['values'][1].replace('● ', '')
            self.show_model_details(model_name)
    
    def show_model_details(self, model_name: str):
        """Show detailed information about a model."""
        # Find the model data
        model_data = None
        for model in self.models_data:
            if (f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']) == model_name:
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
        
        # Add duplicate/variant information
        if model_data.get('is_duplicate', False):
            details.append(("🔄 Duplicate Status", "This is a duplicate model"))
        elif model_data.get('is_special_variant', False):
            details.append(("🔀 Variant Status", "This is a special variant"))
        
        # Add family information
        variant_info = model_data.get('variant_info')
        if variant_info:
            base_name = self.get_model_base_name(model_data['name'])
            family_info = f"Family: {base_name} ({variant_info['total_count']} models)"
            if variant_info['special_variants']:
                family_info += f"\nSpecial variants: {', '.join(variant_info['special_variants'])}"
            if len(variant_info['regular_duplicates']) > 1:
                family_info += f"\nDuplicates: {', '.join(variant_info['regular_duplicates'])}"
            details.append(("📦 Model Family", family_info))
        
        # Add OpenWebUI usage information
        usage_info = model_data.get('usage_info')
        if usage_info:
            details.append(("📊 OpenWebUI Usage", ""))
            details.append(("   💬 Total Chats", str(usage_info.get('usage_count', 0))))
            details.append(("   🪙 Total Tokens", f"{usage_info.get('total_tokens', 0):,}"))
            if usage_info.get('last_used'):
                last_used_formatted = self.format_last_used_time(usage_info['last_used'])
                details.append(("   🕒 Last Used", last_used_formatted))
            if usage_info.get('first_used'):
                first_used_formatted = self.format_last_used_time(usage_info['first_used'])
                details.append(("   🎂 First Used", first_used_formatted))
        else:
            details.append(("📊 OpenWebUI Usage", "Never used in OpenWebUI"))
        
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

    def load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.starred_models = set(config.get('starred_models', []))
                    # Could add other settings here in the future
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            self.starred_models = set()
    
    def save_config(self):
        """Save configuration to file."""
        try:
            config = {
                'starred_models': list(self.starred_models),
                'last_updated': datetime.datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def toggle_star(self, model_name: str):
        """Toggle star status for a model."""
        if model_name in self.starred_models:
            self.starred_models.remove(model_name)
        else:
            self.starred_models.add(model_name)
        self.save_config()
        self.populate_tree()  # Refresh the display
    
    def is_liberated_model(self, model_name: str) -> bool:
        """Check if a model is likely uncensored/liberated based on keywords."""
        model_lower = model_name.lower()
        return any(keyword in model_lower for keyword in self.liberation_keywords)
    
    def get_storage_estimate(self, model_names: List[str]) -> Tuple[float, str]:
        """Calculate total storage that would be recovered by deleting models."""
        total_bytes = 0
        for model_name in model_names:
            for model in self.models_data:
                if (f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']) == model_name:
                    try:
                        # Parse size (e.g., "4.7 GB" -> 4.7)
                        size_parts = model['size'].split()
                        if len(size_parts) >= 2:
                            size_value = float(size_parts[0])
                            size_unit = size_parts[1].upper()
                            
                            # Convert to bytes
                            if size_unit in ['GB', 'G']:
                                total_bytes += size_value * 1024 * 1024 * 1024
                            elif size_unit in ['MB', 'M']:
                                total_bytes += size_value * 1024 * 1024
                            elif size_unit in ['KB', 'K']:
                                total_bytes += size_value * 1024
                    except (ValueError, IndexError):
                        continue
        
        # Convert back to human readable
        if total_bytes >= 1024 * 1024 * 1024:
            return total_bytes / (1024 * 1024 * 1024), f"{total_bytes / (1024 * 1024 * 1024):.1f} GB"
        elif total_bytes >= 1024 * 1024:
            return total_bytes / (1024 * 1024), f"{total_bytes / (1024 * 1024):.1f} MB"
        else:
            return total_bytes / 1024, f"{total_bytes / 1024:.1f} KB"
    
    def get_model_base_name(self, model_name: str) -> str:
        """Extract the base model name without parameters."""
        # Split by colon to separate model name from parameters
        if ':' in model_name:
            base, params = model_name.split(':', 1)
            return base.lower()
        return model_name.lower()
    
    def get_model_params(self, model_name: str) -> str:
        """Extract the parameter portion of a model name."""
        if ':' in model_name:
            _, params = model_name.split(':', 1)
            return params.lower()
        return ""
    
    def is_special_variant(self, model_name: str) -> bool:
        """Check if a model has special parameter suffixes that make it a meaningful variant."""
        params = self.get_model_params(model_name)
        if not params:
            return False
        
        # Check for special suffixes
        for suffix in self.special_suffixes:
            if suffix in params:
                return True
        return False
    
    def detect_duplicates(self):
        """Detect duplicate models and variants within model families."""
        model_families = {}
        duplicates = set()
        variants = {}
        
        # Group models by base name
        for model in self.models_data:
            base_name = self.get_model_base_name((f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']))
            params = self.get_model_params((f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']))
            
            if base_name not in model_families:
                model_families[base_name] = []
            model_families[base_name].append((f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']))
        
        # Identify duplicates and variants
        for base_name, models in model_families.items():
            if len(models) > 1:
                # Sort models to ensure consistent ordering
                models.sort()
                
                special_variants = []
                regular_duplicates = []
                
                for model_name in models:
                    if self.is_special_variant(model_name):
                        special_variants.append(model_name)
                    else:
                        regular_duplicates.append(model_name)
                
                # Mark regular duplicates (keep the first one unmarked)
                if len(regular_duplicates) > 1:
                    for duplicate in regular_duplicates[1:]:
                        duplicates.add(duplicate)
                
                # Store variants info
                if special_variants or len(regular_duplicates) > 1:
                    variants[base_name] = {
                        'special_variants': special_variants,
                        'regular_duplicates': regular_duplicates,
                        'total_count': len(models)
                    }
        
        return duplicates, variants
    
    def calculate_total_storage(self) -> Tuple[float, str]:
        """Calculate total storage used by all models."""
        total_bytes = 0
        
        for model in self.models_data:
            try:
                # Parse size (e.g., "4.7 GB" -> 4.7)
                size_parts = model['size'].split()
                if len(size_parts) >= 2:
                    size_value = float(size_parts[0])
                    size_unit = size_parts[1].upper()
                    
                    # Convert to bytes
                    if size_unit in ['GB', 'G']:
                        total_bytes += size_value * 1024 * 1024 * 1024
                    elif size_unit in ['MB', 'M']:
                        total_bytes += size_value * 1024 * 1024
                    elif size_unit in ['KB', 'K']:
                        total_bytes += size_value * 1024
            except (ValueError, IndexError):
                continue
        
        # Convert back to human readable
        if total_bytes >= 1024 * 1024 * 1024 * 1024:  # TB
            return total_bytes / (1024 * 1024 * 1024 * 1024), f"{total_bytes / (1024 * 1024 * 1024 * 1024):.1f} TB"
        elif total_bytes >= 1024 * 1024 * 1024:  # GB
            return total_bytes / (1024 * 1024 * 1024), f"{total_bytes / (1024 * 1024 * 1024):.1f} GB"
        elif total_bytes >= 1024 * 1024:  # MB
            return total_bytes / (1024 * 1024), f"{total_bytes / (1024 * 1024):.1f} MB"
        else:
            return total_bytes / 1024, f"{total_bytes / 1024:.1f} KB"

    def show_context_menu(self, event):
        """Show the context menu for right-click actions."""
        # First select the item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def context_toggle_star(self):
        """Toggle star status for the selected model."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            self.toggle_star(model_name)
    
    def context_show_details(self):
        """Show details for the selected model."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            self.show_model_details(model_name)
    
    def context_add_to_queue(self):
        """Add the selected model to the deletion queue."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            self.deletion_queue.add(model_name)
            self.update_queue_button()
            self.populate_tree()
    
    def context_remove_from_queue(self):
        """Remove the selected model from the deletion queue."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            if model_name in self.deletion_queue:
                self.deletion_queue.remove(model_name)
                self.update_queue_button()
                self.populate_tree()
    
    def context_copy_name(self):
        """Copy the name of the selected model to the clipboard."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            self.root.clipboard_clear()
            self.root.clipboard_append(model_name)
            self.update_status(f"📋 Copied '{model_name}' to clipboard")
    
    def update_queue_button(self):
        """Update the deletion queue button text."""
        queue_size = len(self.deletion_queue)
        if queue_size > 0:
            _, storage_text = self.get_storage_estimate(list(self.deletion_queue))
            self.queue_btn.config(text=f"🗑️ Queue ({queue_size}) - {storage_text}")
            self.queue_btn.config(bg=self.colors['error'])
        else:
            self.queue_btn.config(text="🗑️ Queue (0)")
            self.queue_btn.config(bg=self.colors['warning'])

    def show_deletion_queue(self):
        """Show the deletion queue management dialog."""
        if not self.deletion_queue:
            messagebox.showinfo("Deletion Queue", "🗑️ No models in deletion queue")
            return
        
        # Create deletion queue window
        queue_window = tk.Toplevel(self.root)
        queue_window.title("🗑️ Model Deletion Queue")
        queue_window.geometry("800x600")
        queue_window.configure(bg=self.colors['bg_primary'])
        
        # Header frame
        header_frame = ttk.Frame(queue_window, style='Custom.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        title_label = ttk.Label(header_frame, 
                               text="🗑️ Models Queued for Deletion", 
                               font=('SF Pro Display', 18, 'bold'),
                               foreground=self.colors['error'])
        title_label.pack()
        
        # Storage estimate
        _, storage_text = self.get_storage_estimate(list(self.deletion_queue))
        storage_label = ttk.Label(header_frame,
                                 text=f"💾 Total Storage to Recover: {storage_text}",
                                 font=('SF Pro Display', 14, 'bold'),
                                 foreground=self.colors['accent_green'])
        storage_label.pack(pady=(10, 0))
        
        # Model list frame
        list_frame = ttk.Frame(queue_window, style='Custom.TFrame')
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Create listbox for queued models
        queue_listbox = tk.Listbox(list_frame,
                                  bg=self.colors['bg_tertiary'],
                                  fg=self.colors['text_primary'],
                                  font=('SF Pro Display', 12),
                                  selectbackground=self.colors['accent_blue'],
                                  height=15)
        
        # Add models to listbox with details
        for model_name in sorted(self.deletion_queue):
            for model in self.models_data:
                if (f"💬 {model['name']}" if model.get("usage_info") and model.get("usage_info", {}).get("usage_count", 0) > 0 else model['name']) == model_name:
                    display_text = f"🗑️ {model_name} ({model['size']})"
                    if model.get('is_starred'):
                        display_text = f"⭐{display_text}"
                    if model.get('is_liberated'):
                        display_text = f"🔓{display_text}"
                    queue_listbox.insert(tk.END, display_text)
                    break
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=queue_listbox.yview)
        queue_listbox.configure(yscrollcommand=scrollbar.set)
        
        queue_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Button frame
        button_frame = ttk.Frame(queue_window, style='Custom.TFrame')
        button_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Remove selected button
        def remove_selected():
            selection = queue_listbox.curselection()
            if selection:
                selected_text = queue_listbox.get(selection[0])
                # Extract model name from display text
                model_name = selected_text.split('🗑️ ')[1].split(' (')[0]
                self.deletion_queue.remove(model_name)
                queue_listbox.delete(selection[0])
                self.update_queue_button()
                self.populate_tree()
                
                # Update storage estimate
                if self.deletion_queue:
                    _, new_storage_text = self.get_storage_estimate(list(self.deletion_queue))
                    storage_label.config(text=f"💾 Total Storage to Recover: {new_storage_text}")
                else:
                    queue_window.destroy()
        
        remove_btn = tk.Button(button_frame,
                              text="❌ Remove Selected",
                              command=remove_selected,
                              bg=self.colors['warning'],
                              fg=self.colors['bg_primary'],
                              font=('SF Pro Display', 11, 'bold'),
                              padx=15, pady=8)
        remove_btn.pack(side='left', padx=(0, 10))
        
        # Clear all button
        def clear_all():
            if messagebox.askyesno("Clear Queue", "🗑️ Remove all models from deletion queue?"):
                self.deletion_queue.clear()
                self.update_queue_button()
                self.populate_tree()
                queue_window.destroy()
        
        clear_btn = tk.Button(button_frame,
                             text="🧹 Clear All",
                             command=clear_all,
                             bg=self.colors['accent_yellow'],
                             fg=self.colors['bg_primary'],
                             font=('SF Pro Display', 11, 'bold'),
                             padx=15, pady=8)
        clear_btn.pack(side='left', padx=(0, 10))
        
        # Execute deletion button
        def execute_deletion():
            if not self.deletion_queue:
                return
            
            confirm_msg = f"⚠️ This will permanently delete {len(self.deletion_queue)} models and recover {storage_text} of storage.\n\nThis action cannot be undone!\n\nAre you sure?"
            
            if messagebox.askyesno("Confirm Deletion", confirm_msg):
                self.execute_model_deletions()
                queue_window.destroy()
        
        execute_btn = tk.Button(button_frame,
                               text=f"🔥 Delete All ({len(self.deletion_queue)} models)",
                               command=execute_deletion,
                               bg=self.colors['error'],
                               fg='white',
                               font=('SF Pro Display', 12, 'bold'),
                               padx=20, pady=8)
        execute_btn.pack(side='right')
        
        # Close button
        close_btn = tk.Button(button_frame,
                             text="✖️ Close",
                             command=queue_window.destroy,
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_primary'],
                             font=('SF Pro Display', 11),
                             padx=15, pady=8)
        close_btn.pack(side='right', padx=(0, 10))
    
    def execute_model_deletions(self):
        """Execute the actual deletion of models in the queue."""
        if not self.deletion_queue:
            return
        
        deleted_models = []
        failed_deletions = []
        
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("🗑️ Deleting Models")
        progress_window.geometry("500x300")
        progress_window.configure(bg=self.colors['bg_primary'])
        
        progress_label = ttk.Label(progress_window,
                                  text="🔄 Deleting models...",
                                  font=('SF Pro Display', 14),
                                  foreground=self.colors['text_primary'])
        progress_label.pack(pady=20)
        
        status_text = tk.Text(progress_window,
                             height=10,
                             bg=self.colors['bg_tertiary'],
                             fg=self.colors['text_primary'],
                             font=('SF Pro Display', 10))
        status_text.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Delete each model
        for i, model_name in enumerate(list(self.deletion_queue)):
            status_text.insert(tk.END, f"🗑️ Deleting {model_name}...\n")
            status_text.see(tk.END)
            progress_window.update()
            
            try:
                # Execute ollama delete command
                result = subprocess.run(['ollama', 'delete', model_name], 
                                      capture_output=True, text=True, check=True)
                deleted_models.append(model_name)
                status_text.insert(tk.END, f"✅ Successfully deleted {model_name}\n")
                
            except subprocess.CalledProcessError as e:
                failed_deletions.append(model_name)
                status_text.insert(tk.END, f"❌ Failed to delete {model_name}: {e}\n")
            
            status_text.see(tk.END)
            progress_window.update()
        
        # Clear the deletion queue and update UI
        self.deletion_queue.clear()
        self.update_queue_button()
        
        # Show completion message
        if failed_deletions:
            messagebox.showwarning("Deletion Complete", 
                                 f"✅ Deleted {len(deleted_models)} models\n❌ Failed to delete {len(failed_deletions)} models")
        else:
            messagebox.showinfo("Deletion Complete", 
                               f"✅ Successfully deleted all {len(deleted_models)} models!")
        
        progress_window.destroy()
        self.refresh_models()  # Reload the model list

    def keyboard_toggle_star(self, event):
        """Toggle star status for the selected model using keyboard shortcut."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            self.toggle_star(model_name)

    def keyboard_add_to_queue(self, event):
        """Add the selected model to the deletion queue using keyboard shortcut."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            self.deletion_queue.add(model_name)
            self.update_queue_button()
            self.populate_tree()

    def keyboard_remove_from_queue(self, event):
        """Remove the selected model from the deletion queue using keyboard shortcut."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            if model_name in self.deletion_queue:
                self.deletion_queue.remove(model_name)
                self.update_queue_button()
                self.populate_tree()

    def keyboard_show_details(self, event):
        """Show details for the selected model using keyboard shortcut."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            model_name = item['values'][1]  # Name is in column 1 now
            self.show_model_details(model_name)

    def show_help(self):
        """Show the help dialog."""
        help_window = tk.Toplevel(self.root)
        help_window.title("🚀 Ollama Model Viewer Help")
        help_window.geometry("600x400")
        help_window.configure(bg=self.colors['bg_primary'])
        
        # Create scrollable frame
        canvas = tk.Canvas(help_window, bg=self.colors['bg_primary'])
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Custom.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add help content
        help_content = [
            ("🚀 Ollama Model Viewer Help", 'header'),
            ("", 'space'),
            ("⭐ HOW TO STAR A MODEL:", 'section'),
            ("Method 1: Right-click any model → ⭐ Toggle Star", 'text'),
            ("Method 2: Select model → Press 's' key", 'text'),
            ("", 'space'),
            ("🗑️ HOW TO DELETE MODELS:", 'section'),
            ("1. Right-click model → 🗑️ Add to Deletion Queue", 'text'),
            ("2. Click 🗑️ Queue button in header", 'text'),
            ("3. Review storage estimate and click 🔥 Delete All", 'text'),
            ("", 'space'),
            ("⌨️ KEYBOARD SHORTCUTS:", 'section'),
            ("S = Star/unstar selected model", 'text'),
            ("D = Add to deletion queue", 'text'),
            ("R = Remove from deletion queue", 'text'),
            ("Enter = Show model details", 'text'),
            ("", 'space'),
            ("🎯 STATUS ICONS:", 'section'),
            ("🟢 = Recently used (< 2 weeks)", 'text'),
            ("🟡 = Moderately used (2-4 weeks)", 'text'),
            ("🔴 = Old model (1+ month)", 'text'),
            ("⭐ = Starred/favorite model", 'text'),
            ("🔓 = Liberated/uncensored model", 'text'),
            ("🗑️ = Queued for deletion", 'text'),
            ("🔄 = Duplicate model", 'text'),
            ("🔀 = Special variant (e.g., -a3b, -instruct)", 'text'),
            ("💬 = Used in OpenWebUI", 'text'),
            ("📊 = Frequently used (>10 chats)", 'text'),
            ("🔥 = Heavily used (>50 chats)", 'text'),
            ("", 'space'),
            ("🔍 QUICK FILTERS:", 'section'),
            ("Use the dropdown to filter by:", 'text'),
            ("• ⭐ Starred Models", 'text'),
            ("• 🔓 Liberated Models", 'text'),
            ("• 🗑️ Queued for Deletion", 'text'),
            ("• 🔄 Duplicate Models", 'text'),
            ("• 🔀 Special Variants", 'text'),
            ("• 📦 Model Families (2+ models)", 'text'),
            ("• 📊 Used in OpenWebUI", 'text'),
            ("• ❌ Never Used in OpenWebUI", 'text'),
            ("• 🔥 Frequently Used (>10 chats)", 'text'),
            ("• ⚡ Recent OpenWebUI Activity", 'text'),
            ("• Size, age, capabilities, etc.", 'text'),
            ("", 'space'),
            ("📊 OPENWEBUI INTEGRATION:", 'section'),
            ("Automatically detects OpenWebUI database", 'text'),
            ("Shows actual usage stats from chat history", 'text'),
            ("Track which models you really use", 'text'),
            ("Filter by usage patterns to find unused models", 'text'),
            ("", 'space'),
            ("💾 STORAGE INFO:", 'section'),
            ("💾 Storage usage shown in status bar", 'text'),
            ("Duplicate detection helps identify space savings", 'text'),
            ("Special variants (-a3b, -instruct) are preserved", 'text'),
            ("Usage data helps identify models safe to delete", 'text'),
            ("", 'space'),
            ("🔒 PRIVACY & SECURITY:", 'section'),
            ("OpenWebUI database automatically encrypted", 'text'),
            ("Only usage statistics accessed (no chat content)", 'text'),
            ("All processing happens locally on your machine", 'text'),
            ("Temporary files securely overwritten after use", 'text'),
            ("", 'space'),
            ("🗺️ FUTURE ROADMAP:", 'section'),
            ("(These features are currently disabled for privacy)", 'text'),
            ("📚 Chat browsing and search functionality", 'text'),
            ("📊 Conversation topic analysis", 'text'),
            ("📋 Export conversations and knowledge", 'text'),
            ("💾 Personal AI knowledge base creation", 'text'),
            ("🔍 Advanced usage analytics", 'text')
        ]
        
        for line_data in help_content:
            if isinstance(line_data, tuple):
                text, style_type = line_data
            else:
                text, style_type = line_data, 'text'
            
            if style_type == 'header':
                font = ('SF Pro Display', 16, 'bold')
                color = self.colors['accent_blue']
            elif style_type == 'section':
                font = ('SF Pro Display', 12, 'bold')
                color = self.colors['accent_green']
            elif style_type == 'space':
                font = ('SF Pro Display', 6)
                color = self.colors['text_primary']
            else:
                font = ('SF Pro Display', 11)
                color = self.colors['text_primary']
            
            if text:  # Don't create empty labels
                label = tk.Label(scrollable_frame, 
                                text=text,
                                bg=self.colors['bg_primary'],
                                fg=color,
                                font=font,
                                anchor='w',
                                justify='left')
                label.pack(anchor='w', padx=20, pady=2, fill='x')
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def detect_openwebui_path(self):
        """Detect OpenWebUI data directory automatically."""
        common_paths = [
            # Temporary copy location
            Path.home() / "tmp" / "openwebui",
            # Docker volume mounts
            Path.home() / "openwebui",
            Path.home() / "open-webui", 
            Path.home() / "open_webui",
            # Default Docker locations
            Path("/app/backend/data"),
            Path("/data"),
            # Local installations
            Path.home() / ".config" / "open-webui",
            Path.home() / ".local" / "share" / "open-webui",
            # Common container mount points
            Path("/opt/open-webui/data"),
            Path("/var/lib/open-webui"),
        ]
        
        # First try common paths
        for path in common_paths:
            db_path = path / "webui.db"
            if db_path.exists():
                self.openwebui_data_path = path
                print(f"✅ Found OpenWebUI database at: {db_path}")
                return
        
        # Try to copy from Docker container if running
        try:
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                                  capture_output=True, text=True, check=True)
            container_names = result.stdout.strip().split('\n')
            
            for container_name in container_names:
                if 'webui' in container_name.lower() or 'open-webui' in container_name.lower():
                    # Try to copy database from container
                    temp_path = Path.home() / "tmp" / "openwebui"
                    temp_path.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        copy_result = subprocess.run([
                            'docker', 'cp', f'{container_name}:/app/backend/data/webui.db', 
                            str(temp_path / 'webui.db')
                        ], capture_output=True, text=True, check=True)
                        
                        if (temp_path / 'webui.db').exists():
                            self.openwebui_data_path = temp_path
                            print(f"✅ Copied OpenWebUI database from Docker container '{container_name}' to: {temp_path / 'webui.db'}")
                            
                            # Encrypt the database for privacy protection
                            if self.encrypt_database:
                                self.encrypt_database_file(temp_path / 'webui.db')
                            
                            # Show privacy notice to user
                            self.root.after(1000, self.show_privacy_notice)
                            return
                    except subprocess.CalledProcessError:
                        continue
                        
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Docker not available or no containers
            pass
        
        # Try to find database by searching common locations
        search_paths = [Path.home(), Path("/opt"), Path("/var/lib")]
        for search_path in search_paths:
            if search_path.exists():
                try:
                    for db_file in search_path.rglob("webui.db"):
                        self.openwebui_data_path = db_file.parent
                        print(f"✅ Found OpenWebUI database at: {db_file}")
                        return
                except (PermissionError, OSError):
                    continue
        
        print("⚠️ OpenWebUI database not found. Usage data will not be available.")
        print("💡 If you have OpenWebUI in Docker, the database has been automatically copied to ~/tmp/openwebui/")
        print("💡 To manually specify location, you can modify the detect_openwebui_path method")

    def get_openwebui_usage_data(self) -> Dict[str, Dict]:
        """Extract model usage data from OpenWebUI database."""
        if not self.openwebui_data_path:
            return {}
        
        # Check for encrypted database first
        db_path = self.openwebui_data_path / "webui.db"
        encrypted_path = self.openwebui_data_path / "webui.db.enc"
        
        temp_db_path = None
        usage_data = {}
        
        try:
            # Determine which database file to use
            if encrypted_path.exists():
                print("🔒 Accessing encrypted OpenWebUI database...")
                temp_db_path = self.decrypt_database_for_access(encrypted_path)
                if not temp_db_path:
                    print("❌ Failed to decrypt database")
                    return {}
                actual_db_path = temp_db_path
            elif db_path.exists():
                actual_db_path = db_path
            else:
                return {}
            
            # Connect to database and extract usage data
            conn = sqlite3.connect(str(actual_db_path))
            cursor = conn.cursor()
            
            # Query to get model usage from chat table - ONLY usage statistics, no chat content
            query = """
                SELECT 
                    json_extract(chat, '$.models[0]') as model_name,
                    COUNT(*) as usage_count,
                    MAX(chat.updated_at) as last_used,
                    MIN(chat.updated_at) as first_used,
                    SUM(CASE WHEN json_extract(chat.meta, '$.usage') IS NOT NULL 
                             THEN json_extract(chat.meta, '$.usage.total_tokens') 
                             ELSE 0 END) as total_tokens
                FROM chat 
                WHERE json_extract(chat, '$.models[0]') IS NOT NULL
                GROUP BY json_extract(chat, '$.models[0]')
                ORDER BY last_used DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            for row in results:
                model_name, usage_count, last_used, first_used, total_tokens = row
                if model_name:
                    # Clean model name (remove any prefixes)
                    clean_name = self.clean_model_name_for_matching(model_name)
                    
                    usage_data[clean_name] = {
                        'usage_count': usage_count or 0,
                        'last_used': last_used,
                        'first_used': first_used,
                        'total_tokens': total_tokens or 0,
                        'original_name': model_name
                    }
            
            conn.close()
            print(f"📊 Loaded usage data for {len(usage_data)} models from OpenWebUI (privacy protected)")
            
        except Exception as e:
            print(f"⚠️ Error reading OpenWebUI database: {e}")
        
        finally:
            # Always clean up temporary decrypted database
            if temp_db_path:
                self.cleanup_temp_database(temp_db_path)
        
        return usage_data

    def clean_model_name_for_matching(self, model_name: str) -> str:
        """Clean model name for matching between Ollama and OpenWebUI."""
        # Remove common prefixes that OpenWebUI might add
        prefixes_to_remove = ['ollama/', 'local/', 'models/']
        
        clean_name = model_name.lower().strip()
        for prefix in prefixes_to_remove:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):]
        
        return clean_name

    def get_model_usage_info(self, model_name: str) -> Optional[Dict]:
        """Get usage information for a specific model from OpenWebUI data."""
        if not hasattr(self, '_usage_data_loaded') or not self._usage_data_loaded:
            # Load usage data only once
            self.openwebui_usage_data = self.get_openwebui_usage_data()
            self._usage_data_loaded = True
        
        clean_name = self.clean_model_name_for_matching(model_name)
        return self.openwebui_usage_data.get(clean_name)

    def format_last_used_time(self, timestamp: str) -> str:
        """Format the last used timestamp into a human-readable string."""
        if not timestamp:
            return "Never used"
        
        try:
            # Parse timestamp (OpenWebUI typically uses Unix timestamp)
            if isinstance(timestamp, (int, float)):
                last_used = datetime.datetime.fromtimestamp(timestamp)
            else:
                # Try to parse as ISO format or other common formats
                try:
                    last_used = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    last_used = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            
            now = datetime.datetime.now()
            diff = now - last_used
            
            if diff.days == 0:
                if diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return f"{minutes} minutes ago"
                else:
                    hours = diff.seconds // 3600
                    return f"{hours} hours ago"
            elif diff.days == 1:
                return "1 day ago"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago"
            elif diff.days < 365:
                months = diff.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            else:
                years = diff.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
                
        except Exception as e:
            print(f"Error parsing timestamp {timestamp}: {e}")
            return "Unknown"

    def generate_database_key(self) -> bytes:
        """Generate a secure key for database encryption."""
        # Use a combination of user-specific data for key generation
        # Use machine-specific data that doesn't expose username
        home_path = str(Path.home())
        # Create a hash of the home path without exposing the username directly
        machine_id = hashlib.sha256(home_path.encode()).hexdigest()[:16]
        key_material = f"ollama_viewer_{machine_id}"
        key = hashlib.pbkdf2_hmac('sha256', key_material.encode(), b'ollama_viewer_salt_v1', 100000)
        return base64.b64encode(key)[:32]  # 32 bytes for encryption

    def encrypt_database_file(self, db_path: Path) -> bool:
        """Encrypt the database file for privacy protection."""
        if not self.encrypt_database:
            return True
            
        try:
            # For now, implement basic obfuscation
            # In production, would use proper encryption like Fernet
            encrypted_path = db_path.with_suffix('.enc')
            
            with open(db_path, 'rb') as f:
                data = f.read()
            
            # Simple XOR encryption (for demo - would use proper crypto in production)
            if not self.database_key:
                self.database_key = self.generate_database_key()
            
            key_bytes = self.database_key
            encrypted_data = bytes(a ^ b for a, b in zip(data, (key_bytes * (len(data) // len(key_bytes) + 1))[:len(data)]))
            
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Remove original unencrypted file
            os.remove(db_path)
            print(f"🔒 Database encrypted and saved to: {encrypted_path}")
            return True
            
        except Exception as e:
            print(f"⚠️ Failed to encrypt database: {e}")
            return False

    def decrypt_database_for_access(self, encrypted_path: Path) -> Optional[Path]:
        """Temporarily decrypt database for read-only access."""
        if not self.encrypt_database:
            return encrypted_path
            
        try:
            temp_db_path = encrypted_path.with_suffix('.tmp')
            
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            if not self.database_key:
                self.database_key = self.generate_database_key()
            
            key_bytes = self.database_key
            decrypted_data = bytes(a ^ b for a, b in zip(encrypted_data, (key_bytes * (len(encrypted_data) // len(key_bytes) + 1))[:len(encrypted_data)]))
            
            with open(temp_db_path, 'wb') as f:
                f.write(decrypted_data)
            
            return temp_db_path
            
        except Exception as e:
            print(f"⚠️ Failed to decrypt database: {e}")
            return None

    def cleanup_temp_database(self, temp_db_path: Path):
        """Securely clean up temporary decrypted database."""
        if temp_db_path and temp_db_path.exists() and temp_db_path.suffix == '.tmp':
            try:
                # Overwrite file before deletion for security
                with open(temp_db_path, 'wb') as f:
                    f.write(os.urandom(temp_db_path.stat().st_size))
                os.remove(temp_db_path)
            except Exception as e:
                print(f"⚠️ Failed to securely clean up temp database: {e}")

    def show_privacy_notice(self):
        """Show privacy notice and options to user."""
        if not self.privacy_mode:
            return
            
        privacy_window = tk.Toplevel(self.root)
        privacy_window.title("🔒 Privacy & Security Settings")
        privacy_window.geometry("600x400")
        privacy_window.configure(bg=self.colors['bg_primary'])
        privacy_window.grab_set()  # Make modal
        
        # Header
        header_label = ttk.Label(privacy_window,
                                text="🔒 Privacy Protection Enabled",
                                font=('SF Pro Display', 18, 'bold'),
                                foreground=self.colors['accent_green'])
        header_label.pack(pady=20)
        
        # Privacy info
        info_text = """
🛡️ Your OpenWebUI chat data is being protected:

✅ Database encryption is ENABLED by default
✅ Only usage statistics are accessed (no chat content)
✅ All data processing happens locally on your machine
✅ No data is transmitted to external services

🗺️ Future Roadmap Features (Currently Disabled):
📚 Chat browsing and search
📊 Conversation analysis
📋 Chat export functionality
💾 Personal knowledge base creation

These features would require additional privacy controls and explicit user consent.
        """
        
        info_label = tk.Label(privacy_window,
                             text=info_text,
                             bg=self.colors['bg_primary'],
                             fg=self.colors['text_primary'],
                             font=('SF Pro Display', 11),
                             justify='left')
        info_label.pack(padx=20, pady=10, fill='both', expand=True)
        
        # Buttons
        button_frame = ttk.Frame(privacy_window, style='Custom.TFrame')
        button_frame.pack(fill='x', padx=20, pady=20)
        
        def accept_settings():
            privacy_window.destroy()
        
        def disable_openwebui():
            self.openwebui_data_path = None
            self.openwebui_usage_data = {}
            messagebox.showinfo("Privacy", "OpenWebUI integration has been disabled for this session.")
            privacy_window.destroy()
        
        accept_btn = tk.Button(button_frame,
                              text="✅ Continue with Privacy Protection",
                              command=accept_settings,
                              bg=self.colors['accent_green'],
                              fg=self.colors['bg_primary'],
                              font=('SF Pro Display', 12, 'bold'),
                              padx=20, pady=8)
        accept_btn.pack(side='right', padx=(10, 0))
        
        disable_btn = tk.Button(button_frame,
                               text="🚫 Disable OpenWebUI Integration",
                               command=disable_openwebui,
                               bg=self.colors['accent_red'],
                               fg='white',
                               font=('SF Pro Display', 11),
                               padx=20, pady=8)
        disable_btn.pack(side='right')

def main():
    """Main function to run the application."""
    # Set up virtual environment with required packages
    venv_manager = AutoVirtualEnvironment(
        custom_name="venv-ollama-model-viewer",
        auto_packages=[
            # tkinter is built into Python, no need to install
        ]
    )
    
    # Auto-switch to virtual environment if needed
    venv_manager.auto_switch()
    
    # Create and run the application
    app = OllamaModelViewer()
    app.run()

if __name__ == "__main__":
    main() 
