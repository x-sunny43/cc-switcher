import customtkinter as ctk
import os
import shutil
import json
from pathlib import Path
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Modern card-style color schemes
DARK_COLORS = {
    "bg_primary": "#1a1a1a",      # Dark background
    "bg_secondary": "#2b2b2b",    # Card background
    "bg_tertiary": "#333333",     # Elevated card background
    "card_hover": "#3a3a3a",      # Card hover state
    "border": "#404040",          # Subtle border
    "shadow": "#000000",          # Card shadow
    "text_primary": "#ffffff",    # Primary text
    "text_secondary": "#b3b3b3",  # Secondary text
    "text_muted": "#666666",      # Muted text
    "accent_primary": "#007acc",  # Primary accent (blue)
    "accent_hover": "#005a9e",    # Primary accent hover
    "accent_red": "#ff6b6b",      # Error/active state
    "accent_red_hover": "#ff5252", # Error hover
    "success_green": "#4caf50",   # Success state
    "warning_orange": "#ff9800"   # Warning state
}

LIGHT_COLORS = {
    "bg_primary": "#f8f8f6",      # Warm, eye-friendly background
    "bg_secondary": "#fefffe",    # Soft white with warm undertone
    "bg_tertiary": "#f3f4f2",     # Elevated background with subtle contrast
    "card_hover": "#eef1ee",      # Gentle hover effect
    "border": "#d0d7de",          # Professional border color
    "shadow": "#eaeef2",          # Soft shadow color
    "text_primary": "#24292f",    # High contrast primary text
    "text_secondary": "#57606a",  # Well-balanced secondary text
    "text_muted": "#8c959f",      # Properly muted text
    "accent_primary": "#0969da",  # Modern, accessible blue
    "accent_hover": "#0860ca",    # Corresponding hover state
    "accent_red": "#d1242f",      # Professional red for errors/active
    "accent_red_hover": "#cf222e", # Corresponding hover state
    "success_green": "#1a7f37",   # Professional success green
    "warning_orange": "#d97916"   # Balanced warning orange
}

# Default to dark theme
COLORS = DARK_COLORS


class ClaudeConfigSwitcher:
    def __init__(self):
        self.root = ctk.CTk()
        # Configure window properties
        self.root.configure(fg_color=COLORS["bg_primary"])
        self.root.title("cc switcher")
        
        # Keep system window but make it resizable and with proper taskbar behavior
        self.root.resizable(True, True)
        
        # Set initial size
        window_width = 900
        window_height = 430

        # Get screen dimensions and center the window
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - window_width) // 2)
        center_y = int((screen_height - window_height) // 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.claude_dir = Path.home() / ".claude"
        self.settings_file = self.claude_dir / "settings.json"
        self.backup_dir = self.claude_dir / "backups"
        self.app_state_file = self.claude_dir / ".cc-cache"

        self.config_files = []
        self.current_config = None

        # Initialize UI after all variables are set
        self.setup_ui()
        
        # Use after_idle to ensure UI is ready before refreshing
        self.root.after_idle(lambda: self.refresh_config_list(is_initial=True))

    def load_app_state(self):
        """Load the last selected file from app state"""
        try:
            if self.app_state_file.exists():
                with open(self.app_state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    return state.get('last_selected_file')
        except (json.JSONDecodeError, IOError):
            pass
        return None

    def save_app_state(self, selected_file_name):
        """Save the current selected file to app state"""
        try:
            self.claude_dir.mkdir(exist_ok=True)
            state = {'last_selected_file': selected_file_name}
            with open(self.app_state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except (IOError, OSError):
            pass  # Silently ignore save failures

    def setup_ui(self):
        # --- Main Content Area ---
        content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=3, pady=3)

        # --- Toolbar (leftmost panel) ---
        self.toolbar = ctk.CTkFrame(content_frame, width=30, corner_radius=0, fg_color=COLORS["bg_secondary"])
        self.toolbar.pack(side="left", fill="y", pady=0, padx=(0, 0.5))
        self.toolbar.pack_propagate(False)

        # --- Toolbar Content ---
        toolbar_container = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        toolbar_container.pack(fill="both", expand=True, padx=2, pady=8)

        # Top button container for sync button
        top_container = ctk.CTkFrame(toolbar_container, fg_color="transparent")
        top_container.pack(side="top")

        # WebDAV sync button (sun behind cloud icon) - at the very top
        self.sync_btn = ctk.CTkButton(
            top_container,
            text="🌥",
            command=self.webdav_sync,
            width=26,
            height=26,
            corner_radius=0,
            fg_color="transparent",
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
            border_width=0
        )
        self.sync_btn.pack(pady=(0, 8))

        # Bottom button container to push buttons to bottom
        button_container = ctk.CTkFrame(toolbar_container, fg_color="transparent")
        button_container.pack(side="bottom")

        # Settings button (gear icon) - at the very bottom
        self.settings_btn = ctk.CTkButton(
            button_container,
            text="⚙",
            command=self.open_settings,
            width=26,
            height=26,
            corner_radius=0,
            fg_color="transparent",
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
            border_width=0
        )
        self.settings_btn.pack(side="bottom", pady=(4, 0))

        # Theme toggle button (sun/moon icon) - above settings
        self.theme_btn = ctk.CTkButton(
            button_container,
            text="🌙",
            command=self.toggle_theme,
            width=26,
            height=26,
            corner_radius=0,
            fg_color="transparent",
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=14),
            border_width=0
        )
        self.theme_btn.pack(side="bottom", pady=(0, 4))

        # --- Left Panel ---
        self.left_panel = ctk.CTkFrame(content_frame, width=260, corner_radius=0, fg_color=COLORS["bg_secondary"])
        self.left_panel.pack(side="left", fill="y", pady=0, padx=(1, 1))
        self.left_panel.pack_propagate(False)

        # --- Bottom Controls Container ---
        bottom_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        bottom_container.pack(side="bottom", fill="x", padx=8, pady=(4, 8))

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(
            bottom_container, 
            text="", 
            font=ctk.CTkFont(family="Segoe UI", size=14), 
            height=20,
            text_color=COLORS["text_muted"]
        )
        self.status_label.pack(pady=(0, 4), padx=0, fill="x")

        # --- Action Buttons ---
        self.switch_btn = ctk.CTkButton(
            bottom_container,
            text="Switch Config",
            command=self.switch_config,
            height=30,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            corner_radius=0,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.switch_btn.pack(pady=(0, 4), padx=0, fill="x")

        # Button row for secondary actions
        button_row = ctk.CTkFrame(bottom_container, fg_color="transparent")
        button_row.pack(fill="x", pady=0)

        self.refresh_btn = ctk.CTkButton(
            button_row,
            text="Refresh",
            command=self.refresh_config_list,
            height=30,
            corner_radius=0,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            border_width=1,
            border_color=COLORS["border"]
        )
        self.refresh_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))

        self.open_dir_btn = ctk.CTkButton(
            button_row,
            text="Open",
            command=self.open_config_directory,
            height=30,
            corner_radius=0,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            border_width=1,
            border_color=COLORS["border"]
        )
        self.open_dir_btn.pack(side="right", fill="x", expand=True, padx=(2, 0))

        # --- Config List (takes all remaining space) ---
        list_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Use a regular frame for the config list to avoid always-visible scrollbar
        self.config_listbox = ctk.CTkFrame(
            list_container, 
            corner_radius=0, 
            fg_color="transparent"
        )
        self.config_listbox.pack(fill="both", expand=True)

        # --- Right Panel (Preview) ---
        self.right_panel = ctk.CTkFrame(content_frame, corner_radius=0, fg_color=COLORS["bg_secondary"])
        self.right_panel.pack(side="left", fill="both", expand=True, padx=(1, 0), pady=0)

        # Preview content
        preview_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        preview_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.preview_textbox = ctk.CTkTextbox(
            preview_container,
            corner_radius=0,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            wrap="word",
            fg_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"]
        )
        self.preview_textbox.pack(fill="both", expand=True)

        self.selected_config = None

    def create_config_button(self, config_file, settings_content):
        # Card container with modern styling
        card = ctk.CTkFrame(
            self.config_listbox,
            height=30,
            corner_radius=0,
            fg_color=COLORS["bg_tertiary"],
            border_width=1,
            border_color=COLORS["border"]
        )
        card.pack(fill="x", pady=(0, 1), padx=0)
        card.pack_propagate(False)

        # Main content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=8, pady=4)

        # File name with compact typography
        name_label = ctk.CTkLabel(
            content_frame,
            text=config_file.name,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            anchor="w",
            text_color=COLORS["text_primary"]
        )
        name_label.pack(side="left", fill="x", expand=True, anchor="w")

        # Status indicator with modern styling
        is_active = config_file.name == "settings.json"
        is_synced = False

        if not is_active and settings_content is not None:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    current_content = json.load(f)
                if current_content == settings_content:
                    is_synced = True
            except (json.JSONDecodeError, IOError):
                pass

        if is_active:
            status_label = ctk.CTkLabel(
                content_frame,
                text="●",
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=COLORS["accent_red"]
            )
            status_label.pack(side="right", padx=(6, 0))
        elif is_synced:
            status_label = ctk.CTkLabel(
                content_frame,
                text="●",
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=COLORS["success_green"]
            )
            status_label.pack(side="right", padx=(6, 0))

        # Add hover effect data
        card._config_file = config_file
        card._is_selected = False
        
        # Bind click and hover events to all components
        def on_click(e):
            self.select_config(config_file)
        
        def on_enter(e):
            if not card._is_selected:
                card.configure(fg_color=COLORS["card_hover"])
        
        def on_leave(e):
            if not card._is_selected:
                card.configure(fg_color=COLORS["bg_tertiary"])
        
        # Bind events to all widgets to prevent flickering
        widgets_to_bind = [card, content_frame, name_label]
        if 'status_label' in locals():
            widgets_to_bind.append(status_label)
            
        for widget in widgets_to_bind:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def select_config(self, config_file):
        self.selected_config = config_file
        
        # Save the selected file to app state
        self.save_app_state(config_file.name)

        # Update UI selection highlight
        for child in self.config_listbox.winfo_children():
            if hasattr(child, '_config_file'):
                if child._config_file.name == config_file.name:
                    # Selected card - no border for clean look
                    child.configure(fg_color=COLORS["accent_primary"], border_width=0)
                    child._is_selected = True
                    # Update text color for better contrast on blue background
                    for widget in child.winfo_children():
                        if isinstance(widget, ctk.CTkFrame):  # content_frame
                            for label in widget.winfo_children():
                                if isinstance(label, ctk.CTkLabel) and "settings" in label.cget("text"):
                                    label.configure(text_color="white")
                else:
                    # Unselected cards - restore border
                    child.configure(fg_color=COLORS["bg_tertiary"], border_width=1, border_color=COLORS["border"])
                    child._is_selected = False
                    # Restore original text color
                    for widget in child.winfo_children():
                        if isinstance(widget, ctk.CTkFrame):  # content_frame
                            for label in widget.winfo_children():
                                if isinstance(label, ctk.CTkLabel) and "settings" in label.cget("text"):
                                    label.configure(text_color=COLORS["text_primary"])

        self.update_preview(config_file)

    def update_preview(self, config_file):
        try:
            self.preview_textbox.delete("1.0", "end")

            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                try:
                    json_data = json.loads(content)
                    formatted_content = json.dumps(json_data, indent=2, ensure_ascii=False)
                    self.insert_json_with_highlighting(formatted_content)
                except json.JSONDecodeError:
                    self.preview_textbox.insert("1.0", content)

        except Exception:
            self.update_status("Error reading file", COLORS["accent_red"])

    def insert_json_with_highlighting(self, json_content):
        """Insert JSON content with syntax highlighting"""
        import re
        
        # Define color scheme for JSON syntax highlighting based on current theme
        self.update_json_highlighting_colors()
        
        # Insert the content
        self.preview_textbox.insert("1.0", json_content)
        
        # Apply highlighting using regex patterns
        content = json_content
        
        # Keep track of string positions to avoid re-highlighting them
        string_ranges = []
        
        # First pass: Highlight strings (including keys and values)
        for match in re.finditer(r'"([^"\\\\]|\\\\.)*"', content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            string_ranges.append((match.start(), match.end()))
            
            # Check if this string is a key (followed by colon)
            rest_content = content[match.end():].lstrip()
            if rest_content.startswith(':'):
                self.preview_textbox.tag_add("key", start_idx, end_idx)
            else:
                self.preview_textbox.tag_add("string", start_idx, end_idx)
        
        # Helper function to check if position is inside a string
        def is_in_string(pos):
            for start, end in string_ranges:
                if start <= pos < end:
                    return True
            return False
        
        # Highlight numbers (only outside strings)
        for match in re.finditer(r'-?\d+\.?\d*([eE][+-]?\d+)?', content):
            if not is_in_string(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.preview_textbox.tag_add("number", start_idx, end_idx)
        
        # Highlight booleans and null (only outside strings)
        for match in re.finditer(r'\b(true|false|null)\b', content):
            if not is_in_string(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                if match.group(1) in ['true', 'false']:
                    self.preview_textbox.tag_add("boolean", start_idx, end_idx)
                else:
                    self.preview_textbox.tag_add("null", start_idx, end_idx)
        
        # Highlight braces and brackets (only outside strings)
        for match in re.finditer(r'[{}]', content):
            if not is_in_string(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.preview_textbox.tag_add("brace", start_idx, end_idx)
            
        for match in re.finditer(r'[\[\]]', content):
            if not is_in_string(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.preview_textbox.tag_add("bracket", start_idx, end_idx)
        
        # Highlight colons and commas (only outside strings)
        for match in re.finditer(r':', content):
            if not is_in_string(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.preview_textbox.tag_add("colon", start_idx, end_idx)
            
        for match in re.finditer(r',', content):
            if not is_in_string(match.start()):
                start_idx = f"1.0+{match.start()}c"
                end_idx = f"1.0+{match.end()}c"
                self.preview_textbox.tag_add("comma", start_idx, end_idx)

    def switch_config(self):
        if not self.selected_config:
            self.update_status("Please select a config first", COLORS["accent_red"])
            return

        if self.selected_config.name == "settings.json":
            self.update_status("Already the active config", COLORS["text_muted"])
            return

        if not self.selected_config.exists():
            self.update_status("File not found", COLORS["accent_red"])
            return

        try:
            # Backup is now implicit when switching
            if self.settings_file.exists():
                self.backup_dir.mkdir(exist_ok=True)
                backup_name = f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.backup_dir / backup_name
                shutil.copy2(self.settings_file, backup_path)

            shutil.copy2(self.selected_config, self.settings_file)

            self.update_status(f"Switched to {self.selected_config.name}", COLORS["success_green"])
            self.refresh_config_list()

        except Exception:
            self.update_status("Switch failed", COLORS["accent_red"])

    def open_config_directory(self):
        try:
            os.startfile(self.claude_dir)
        except Exception:
            self.update_status("Failed to open directory", COLORS["accent_red"])

    def update_status(self, message, color=None):
        if color is None:
            color = COLORS["text_muted"]
        self.status_label.configure(text=message, text_color=color)
        # Clear the message after 4 seconds
        self.root.after(4000, lambda: self.status_label.configure(text=""))

    def refresh_config_list(self, is_initial=False):
        try:
            # Remember current selection (only for non-initial refresh)
            current_selection = self.selected_config if not is_initial else None
            
            # Clear existing list
            for widget in self.config_listbox.winfo_children():
                widget.destroy()

            self.config_files = []
            self.selected_config = None

            if not self.claude_dir.exists():
                self.update_status("Directory not found", COLORS["accent_red"])
                return

            # Get content of settings.json for comparison
            settings_content = None
            if self.settings_file.exists():
                try:
                    with open(self.settings_file, 'r', encoding='utf-8') as f:
                        settings_content = json.load(f)
                except (json.JSONDecodeError, IOError):
                    settings_content = None  # Mark as not readable

            # Scan for settings-related config files and sort them with settings.json on top
            other_files = []
            settings_file_path = None
            for file_path in self.claude_dir.glob("*.json"):
                file_name = file_path.name.lower()
                # Filter to only include settings-related files
                if (file_name == "settings.json" or 
                    "settings" in file_name or 
                    file_name.startswith("settings_") or
                    file_name.endswith("_settings.json")):
                    
                    if file_path.name == "settings.json":
                        settings_file_path = file_path
                    else:
                        other_files.append(file_path)

            other_files.sort()

            if settings_file_path:
                self.config_files.append(settings_file_path)
            self.config_files.extend(other_files)

            # Create config buttons
            for config_file in self.config_files:
                self.create_config_button(config_file, settings_content)

            if is_initial:
                # Initial load: Restore last selection or default to settings.json
                last_selected = self.load_app_state()
                target_file = None
                
                # Try to find the last selected file
                if last_selected:
                    for config_file in self.config_files:
                        if config_file.name == last_selected:
                            target_file = config_file
                            break
                
                # If no last selection or file not found, default to settings.json
                if not target_file and settings_file_path:
                    target_file = settings_file_path
                
                # Select the target file if found
                if target_file:
                    self.select_config(target_file)
            else:
                # Regular refresh: Restore selection if the file still exists
                if current_selection and current_selection.exists():
                    # Find the corresponding file in the new list
                    for config_file in self.config_files:
                        if config_file.name == current_selection.name:
                            self.select_config(config_file)
                            break
                
        except Exception as e:
            self.update_status(f"Error loading configs: {str(e)}", COLORS["accent_red"])

    def run(self):
        self.root.mainloop()

    def open_settings(self):
        """Open settings dialog or configuration"""
        self.update_status("Settings feature coming soon", COLORS["text_muted"])

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        global COLORS
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("light")
            COLORS = LIGHT_COLORS
            self.theme_btn.configure(text="☀")
            self.update_status("Switched to light theme", COLORS["success_green"])
        else:
            ctk.set_appearance_mode("dark")
            COLORS = DARK_COLORS
            self.theme_btn.configure(text="🌙")
            self.update_status("Switched to dark theme", COLORS["success_green"])
        
        # Refresh the UI with new colors
        self.apply_theme_colors()

    def apply_theme_colors(self):
        """Apply current theme colors to all UI components"""
        # Update main window
        self.root.configure(fg_color=COLORS["bg_primary"])
        
        # Update toolbar
        self.toolbar.configure(fg_color=COLORS["bg_secondary"])
        
        # Update toolbar buttons
        toolbar_buttons = [self.sync_btn, self.theme_btn, self.settings_btn]
        for btn in toolbar_buttons:
            btn.configure(
                hover_color=COLORS["card_hover"],
                text_color=COLORS["text_primary"]
            )
        
        # Update left panel
        self.left_panel.configure(fg_color=COLORS["bg_secondary"])
        
        # Update status label
        self.status_label.configure(text_color=COLORS["text_muted"])
        
        # Update action buttons
        action_buttons = [self.switch_btn, self.refresh_btn, self.open_dir_btn]
        for btn in action_buttons:
            btn.configure(
                fg_color=COLORS["bg_tertiary"],
                hover_color=COLORS["card_hover"],
                text_color=COLORS["text_primary"],
                border_color=COLORS["border"]
            )
        
        # Update right panel
        self.right_panel.configure(fg_color=COLORS["bg_secondary"])
        
        # Update preview textbox
        self.preview_textbox.configure(
            fg_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border"]
        )
        
        # Update JSON syntax highlighting colors for current theme
        if hasattr(self, 'preview_textbox'):
            self.update_json_highlighting_colors()
        
        # Refresh config list to apply new colors
        self.refresh_config_list()

    def update_json_highlighting_colors(self):
        """Update JSON syntax highlighting colors based on current theme"""
        if ctk.get_appearance_mode() == "Light":
            # Light theme colors
            colors = {
                "string": "#d14",         # Red for strings
                "number": "#099",         # Teal for numbers  
                "boolean": "#0086b3",     # Blue for booleans
                "null": "#0086b3",        # Blue for null
                "key": "#0086b3",         # Blue for keys
                "brace": "#333",          # Dark gray for braces
                "bracket": "#333",        # Dark gray for brackets
                "colon": "#333",          # Dark gray for colons
                "comma": "#333"           # Dark gray for commas
            }
        else:
            # Dark theme colors (original)
            colors = {
                "string": "#ce9178",      # Orange for strings
                "number": "#b5cea8",      # Light green for numbers
                "boolean": "#569cd6",     # Blue for booleans
                "null": "#569cd6",        # Blue for null
                "key": "#9cdcfe",         # Light blue for keys
                "brace": "#ffd700",       # Gold for braces
                "bracket": "#ffd700",     # Gold for brackets
                "colon": "#ffffff",       # White for colons
                "comma": "#ffffff"        # White for commas
            }
        
        # Configure text tags for highlighting
        for tag, color in colors.items():
            self.preview_textbox.tag_config(tag, foreground=color)

    def webdav_sync(self):
        """WebDAV synchronization functionality"""
        self.update_status("WebDAV sync feature coming soon", COLORS["text_muted"])


def main():
    app = ClaudeConfigSwitcher()
    app.run()


if __name__ == "__main__":
    main()