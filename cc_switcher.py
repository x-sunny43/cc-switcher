import customtkinter as ctk
import os
import shutil
import json
from pathlib import Path
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Modern card-style color scheme
COLORS = {
    "bg_primary": "#1a1a1a",      # Dark background
    "bg_secondary": "#2b2b2b",    # Card background
    "bg_tertiary": "#333333",     # Elevated card background
    "card_hover": "#3a3a3a",      # Card hover state
    "border": "#404040",  # Subtle border
    "shadow": "#000000",   # Card shadow
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


class ClaudeConfigSwitcher:
    def __init__(self):
        self.root = ctk.CTk()
        # Configure window properties
        self.root.configure(fg_color=COLORS["bg_primary"])
        self.root.title("cc switcher")
        
        # Keep system window but make it resizable and with proper taskbar behavior
        self.root.resizable(True, True)
        
        # Set initial size
        window_width = 820
        window_height = 400  # Reduced since we removed custom title bar

        # Get screen dimensions and center the window
        # Update to get actual screen dimensions after window creation
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width - window_width) // 2)
        center_y = int((screen_height - window_height) // 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Try to minimize system decorations while keeping taskbar functionality
        try:
            # These attributes help on different platforms
            self.root.attributes('-alpha', 1.0)  # Ensure full opacity
        except Exception:
            pass


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

        # --- Left Panel ---
        self.left_panel = ctk.CTkFrame(content_frame, width=260, corner_radius=0, fg_color=COLORS["bg_secondary"])
        self.left_panel.pack(side="left", fill="y", pady=0, padx=(0, 2))
        self.left_panel.pack_propagate(False)

        # --- Bottom Controls Container ---
        bottom_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        bottom_container.pack(side="bottom", fill="x", padx=8, pady=(4, 8))

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(
            bottom_container, 
            text="", 
            font=ctk.CTkFont(size=11), 
            height=20,
            text_color=COLORS["text_muted"]
        )
        self.status_label.pack(pady=(0, 4), padx=0, fill="x")

        # --- Action Buttons ---
        self.switch_btn = ctk.CTkButton(
            bottom_container,
            text="Switch Config",
            command=self.switch_config,
            height=28,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=0,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"]
        )
        self.switch_btn.pack(pady=(0, 4), padx=0, fill="x")

        # Button row for secondary actions
        button_row = ctk.CTkFrame(bottom_container, fg_color="transparent")
        button_row.pack(fill="x", pady=0)

        self.refresh_btn = ctk.CTkButton(
            button_row,
            text="Refresh",
            command=self.refresh_config_list,
            height=28,
            corner_radius=0,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12)
        )
        self.refresh_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))

        self.open_dir_btn = ctk.CTkButton(
            button_row,
            text="Open",
            command=self.open_config_directory,
            height=28,
            corner_radius=0,
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"],
            font=ctk.CTkFont(size=12)
        )
        self.open_dir_btn.pack(side="right", fill="x", expand=True, padx=(2, 0))

        # --- Config List (takes all remaining space) ---
        list_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.config_listbox = ctk.CTkScrollableFrame(
            list_container, 
            corner_radius=0, 
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_tertiary"],
            scrollbar_button_hover_color=COLORS["card_hover"]
        )
        self.config_listbox.pack(fill="both", expand=True)

        # --- Right Panel (Preview) ---
        self.right_panel = ctk.CTkFrame(content_frame, corner_radius=0, fg_color=COLORS["bg_secondary"])
        self.right_panel.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=0)

        # Preview content
        preview_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        preview_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.preview_textbox = ctk.CTkTextbox(
            preview_container,
            corner_radius=0,
            font=ctk.CTkFont(family="JetBrains Mono", size=11),
            wrap="none",
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
            height=24,
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
            font=ctk.CTkFont(size=12, weight="bold"),
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
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["accent_red"]
            )
            status_label.pack(side="right", padx=(6, 0))
        elif is_synced:
            status_label = ctk.CTkLabel(
                content_frame,
                text="●",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["success_green"]
            )
            status_label.pack(side="right", padx=(6, 0))

        # Add hover effect data
        card._config_file = config_file
        card._is_selected = False
        
        # Bind click events
        def on_click(e):
            self.select_config(config_file)
        
        def on_enter(e):
            if not card._is_selected:
                card.configure(fg_color=COLORS["card_hover"])
        
        def on_leave(e):
            if not card._is_selected:
                card.configure(fg_color=COLORS["bg_tertiary"])
        
        card.bind("<Button-1>", on_click)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        content_frame.bind("<Button-1>", on_click)
        name_label.bind("<Button-1>", on_click)

    def select_config(self, config_file):
        self.selected_config = config_file
        
        # Save the selected file to app state
        self.save_app_state(config_file.name)

        # Update UI selection highlight
        for child in self.config_listbox.winfo_children():
            if hasattr(child, '_config_file'):
                if child._config_file.name == config_file.name:
                    # Selected card
                    child.configure(fg_color=COLORS["accent_primary"])
                    child._is_selected = True
                    # Update text color for better contrast on blue background
                    for widget in child.winfo_children():
                        if isinstance(widget, ctk.CTkFrame):  # content_frame
                            for label in widget.winfo_children():
                                if isinstance(label, ctk.CTkLabel) and "settings" in label.cget("text"):
                                    label.configure(text_color="white")
                else:
                    # Unselected cards
                    child.configure(fg_color=COLORS["bg_tertiary"])
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
                    self.preview_textbox.insert("1.0", formatted_content)
                except json.JSONDecodeError:
                    self.preview_textbox.insert("1.0", content)

        except Exception:
            self.update_status("Error reading file", COLORS["accent_red"])

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


def main():
    app = ClaudeConfigSwitcher()
    app.run()


if __name__ == "__main__":
    main()