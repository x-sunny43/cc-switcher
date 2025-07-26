import customtkinter as ctk
import os
import shutil
import json
from pathlib import Path
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Refined color scheme - Professional Black, White, Gray, Red
COLORS = {
    "bg_primary": "#2a2a2a",      # Warm deep gray - main background
    "bg_secondary": "#353535",    # Subtle lifted gray - panels
    "bg_tertiary": "#404040",     # Clear contrast gray - elements
    "border": "#4a4a4a",          # Fine divider gray - borders
    "text_primary": "#f5f5f5",    # Soft white - main text
    "text_secondary": "#c8c8c8",  # Elegant gray - secondary text
    "text_muted": "#999999",      # Understated gray - muted text
    "accent_red": "#e74c3c",      # Classic warm red - active/important
    "accent_red_hover": "#c0392b", # Deep red - hover state
    "success_green": "#27ae60",   # Balanced green - success status
    "button_bg": "#4a4a4a",       # Button background - lighter than tertiary
    "button_hover": "#5a5a5a"     # Button hover - even lighter
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

        self.config_files = []
        self.current_config = None

        # Initialize UI after all variables are set
        self.setup_ui()
        
        # Use after_idle to ensure UI is ready before refreshing
        self.root.after_idle(self.refresh_config_list)


    def setup_ui(self):
        # --- Main Content Area ---
        content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Left Panel ---
        self.left_panel = ctk.CTkFrame(content_frame, width=240, corner_radius=0, fg_color=COLORS["bg_secondary"])
        self.left_panel.pack(side="left", fill="y", pady=0, padx=0)
        self.left_panel.pack_propagate(False)

        # --- Bottom Controls Container ---
        bottom_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        bottom_container.pack(side="bottom", fill="x", padx=0, pady=(5, 0))

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(
            bottom_container, 
            text="", 
            font=ctk.CTkFont(size=12), 
            height=28,
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(pady=2, padx=0, fill="x")

        # --- Action Buttons ---
        self.switch_btn = ctk.CTkButton(
            bottom_container,
            text="Switch",
            command=self.switch_config,
            height=30,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=0,
            fg_color=COLORS["button_bg"],
            hover_color=COLORS["accent_red"],
            text_color=COLORS["text_primary"]
        )
        self.switch_btn.pack(pady=2, padx=0, fill="x")

        self.refresh_btn = ctk.CTkButton(
            bottom_container,
            text="Refresh",
            command=self.refresh_config_list,
            height=30,
            corner_radius=0,
            fg_color=COLORS["button_bg"],
            hover_color=COLORS["button_hover"],
            text_color=COLORS["text_primary"]
        )
        self.refresh_btn.pack(pady=2, padx=0, fill="x")

        self.open_dir_btn = ctk.CTkButton(
            bottom_container,
            text="Open",
            command=self.open_config_directory,
            height=30,
            corner_radius=0,
            fg_color=COLORS["button_bg"],
            hover_color=COLORS["button_hover"],
            text_color=COLORS["text_primary"]
        )
        self.open_dir_btn.pack(pady=(2, 0), padx=0, fill="x")

        # --- Config List (takes all remaining space) ---
        self.config_listbox = ctk.CTkFrame(self.left_panel, corner_radius=0, fg_color="transparent")
        self.config_listbox.pack(fill="both", expand=True, padx=0, pady=0)

        # --- Right Panel (Preview) ---
        self.right_panel = ctk.CTkFrame(content_frame, corner_radius=0, fg_color=COLORS["bg_secondary"])
        self.right_panel.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=0)

        self.preview_textbox = ctk.CTkTextbox(
            self.right_panel,
            corner_radius=0,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="none",
            fg_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border"]
        )
        self.preview_textbox.pack(fill="both", expand=True)

        self.selected_config = None

    def create_config_button(self, config_file, settings_content):
        frame = ctk.CTkFrame(
            self.config_listbox,
            height=33,
            corner_radius=0,
            fg_color=COLORS["bg_tertiary"],
            border_color=COLORS["border"]
        )
        frame.pack(fill="x", pady=(0, 1), padx=0)
        frame.pack_propagate(False)

        name_label = ctk.CTkLabel(
            frame,
            text=config_file.name,
            font=ctk.CTkFont(size=14),
            anchor="w",
            text_color=COLORS["text_primary"]
        )
        name_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)

        # Add status label (Active or Synced)
        is_active = config_file.name == "settings.json"
        is_synced = False

        if not is_active and settings_content is not None:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    current_content = json.load(f)
                if current_content == settings_content:
                    is_synced = True
            except (json.JSONDecodeError, IOError):
                pass  # Ignore files that can't be compared

        if is_active:
            status_label = ctk.CTkLabel(
                frame,
                text="● Active",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["accent_red"]
            )
            status_label.pack(side="right", padx=10)
        elif is_synced:
            status_label = ctk.CTkLabel(
                frame,
                text="●",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_muted"]
            )
            status_label.pack(side="right", padx=10)

        frame.bind("<Button-1>", lambda e, f=config_file: self.select_config(f))
        name_label.bind("<Button-1>", lambda e, f=config_file: self.select_config(f))

    def select_config(self, config_file):
        self.selected_config = config_file

        # Update UI selection highlight
        for child in self.config_listbox.winfo_children():
            # Find the label within the frame to get the file name
            label_widget = child.winfo_children()[0]
            if isinstance(label_widget, ctk.CTkLabel) and label_widget.cget("text") == config_file.name:
                child.configure(fg_color=COLORS["accent_red"])
            else:
                child.configure(fg_color=COLORS["bg_tertiary"])

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

    def refresh_config_list(self):
        try:
            # Clear existing list
            for widget in self.config_listbox.winfo_children():
                widget.destroy()

            self.config_files = []
            self.selected_config = None
            self.preview_textbox.delete("1.0", "end")

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

            # Scan for config files and sort them with settings.json on top
            other_files = []
            settings_file_path = None
            for file_path in self.claude_dir.glob("*.json"):
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

            # Default selection and preview to settings.json
            if settings_file_path:
                self.select_config(settings_file_path)
                
        except Exception as e:
            self.update_status(f"Error loading configs: {str(e)}", COLORS["accent_red"])

    def run(self):
        self.root.mainloop()


def main():
    app = ClaudeConfigSwitcher()
    app.run()


if __name__ == "__main__":
    main()