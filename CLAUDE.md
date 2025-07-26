# Claude Config Switcher - Development Guide

## Project Overview

Claude Config Switcher is a Python desktop application built with CustomTkinter that provides a graphical interface for managing Claude CLI configuration files. The application allows users to easily switch between different Claude configuration profiles stored in the `~/.claude` directory.

### Purpose
- Manage multiple Claude CLI configuration files
- Switch between different Claude profiles with a single click
- Preview configuration content before switching
- Automatic backup of current settings when switching
- Visual indicators for active and synchronized configurations

## Technologies & Dependencies

### Core Technologies
- **Python 3.11+** - Required runtime version
- **CustomTkinter 5.2.2+** - Modern tkinter-based GUI framework
- **PyInstaller 6.14.2+** - For building standalone executables

### Key Libraries Used
- `customtkinter` - Modern GUI components with dark/light theme support
- `pathlib` - Modern path handling
- `json` - Configuration file parsing
- `shutil` - File operations and backups
- `datetime` - Timestamp generation for backups
- `os` - System operations (opening directories)

### Development Tools
- **uv** - Modern Python package manager (lock file present)
- **PyInstaller** - Executable building
- **basedpyright** - Type checking configuration in pyproject.toml

## Project Structure

```
claude-config-switcher/
├── cc_switcher.py  # Main application file
├── build_exe.py              # Python build script
├── build.bat                 # Windows batch build script
├── pyproject.toml            # Project configuration & dependencies
├── uv.lock                   # Dependency lock file
├── README.md                 # Basic project readme (minimal)
├── BUILD_README.md           # Chinese build instructions
├── .python-version           # Python version specification (3.11)
├── .gitignore               # Git ignore rules
└── .env                     # Environment variables (API keys, proxy)
```

## Key Commands & Development Workflow

### Environment Setup
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
# Or install from pyproject.toml
pip install -e .
```

### Running the Application
```bash
# Direct execution
python cc_switcher.py

# Or as module
python -m cc_switcher
```

### Building Executable

#### Method 1: Python Script (Recommended)
```bash
python build_exe.py
```
This script will:
- Check and install PyInstaller if needed
- Verify dependencies (customtkinter)
- Build the executable with proper settings
- Optionally clean up build files

#### Method 2: Batch Script (Windows)
```bash
# Double-click or run
build.bat
```

#### Method 3: Manual PyInstaller
```bash
pyinstaller --onefile --windowed --name ClaudeConfigSwitcher cc_switcher.py
```

### Build Output
- Executable: `dist/ClaudeConfigSwitcher.exe`
- Size: ~20-30MB (includes Python runtime and dependencies)
- Build artifacts: `build/` directory and `.spec` file

## Architecture & Code Structure

### Main Application Class: `ClaudeConfigSwitcher`

#### Key Properties
- `claude_dir`: Path to `~/.claude` directory
- `settings_file`: Path to active `settings.json`
- `backup_dir`: Path to `~/.claude/backups`
- `config_files`: List of available configuration files
- `selected_config`: Currently selected configuration

#### Core Methods

**UI Setup**
- `setup_ui()`: Initializes the two-panel interface (config list + preview)
- `create_config_button()`: Creates clickable config file entries with status indicators

**Configuration Management**
- `refresh_config_list()`: Scans for .json files in ~/.claude directory
- `select_config()`: Handles config selection and preview updates
- `switch_config()`: Performs the actual configuration switching with backup
- `update_preview()`: Shows formatted JSON content in preview pane

**File Operations**
- Automatic backup creation with timestamps
- JSON validation and formatting
- File synchronization detection

### UI Architecture

**Two-Panel Layout**
- **Left Panel** (240px fixed width):
  - Config file list with status indicators
  - Action buttons (Switch, Refresh, Open)
  - Status message area
- **Right Panel** (expandable):
  - JSON preview with syntax formatting
  - Read-only content display

**Status Indicators**
- Green "● Active" - Currently active configuration
- Gray "●" - Configuration matches active settings
- No indicator - Different from active configuration

### File Management Logic

**Configuration Discovery**
- Scans `~/.claude/*.json` files
- Prioritizes `settings.json` at top of list
- Sorts other configurations alphabetically

**Backup Strategy**
- Automatic backup before switching: `settings_backup_YYYYMMDD_HHMMSS.json`
- Stored in `~/.claude/backups/` directory
- No automatic cleanup (manual management required)

**Synchronization Detection**
- Compares JSON content between files
- Uses parsed JSON for accurate comparison
- Handles malformed JSON gracefully

## Important Patterns & Conventions

### Error Handling
- Try-catch blocks around file operations
- Graceful degradation for missing directories
- User-friendly error messages in status bar
- Silent handling of malformed JSON files

### UI Patterns
- CustomTkinter modern styling with light appearance mode
- Responsive layout with pack geometry manager
- Consistent button styling (30px height, no corner radius)
- 4-second auto-clear for status messages

### File Handling
- UTF-8 encoding for all file operations
- Path object usage via pathlib
- Atomic file operations (copy then replace)
- JSON pretty-printing with 2-space indentation

### Configuration
- Window centered on screen at startup (800x430px)
- Resizable interface
- Light theme with dark-blue color scheme
- Consolas font for JSON preview (11pt)

## Key Files & Their Purposes

### Core Application Files
- **`claude_config_switcher.py`** - Main application with GUI and logic
- **`pyproject.toml`** - Project metadata, dependencies, and tool configuration
- **`uv.lock`** - Exact dependency versions for reproducible builds

### Build System
- **`build_exe.py`** - Comprehensive Python build script with dependency checking
- **`build.bat`** - Simple Windows wrapper for the Python build script
- **`.python-version`** - Specifies Python 3.11 requirement

### Documentation
- **`BUILD_README.md`** - Chinese language build instructions and troubleshooting
- **`README.md`** - Minimal project description (mostly empty)

### Configuration Files
- **`.gitignore`** - Comprehensive Python/development ignore patterns
- **`.env`** - Environment variables (contains API keys and proxy settings)

## Development Guidelines

### Code Style
- Modern Python practices (pathlib, f-strings, type hints where beneficial)
- Class-based architecture with clear separation of concerns
- Descriptive method and variable names
- Consistent indentation and formatting

### Error Messages
- User-friendly status messages in the GUI
- Color-coded status (green=success, red=error, orange=warning, gray=info)
- Automatic message clearing after 4 seconds

### File Operations
- Always use UTF-8 encoding
- Create backup before destructive operations
- Validate JSON before processing
- Handle missing directories gracefully

### UI Guidelines
- Consistent spacing and sizing
- Responsive layout design
- Clear visual hierarchy
- Accessible color choices

## Environment Variables

The `.env` file contains:
- `GEMINI_API_KEY` - API key for Google Gemini services
- `HTTP_PROXY`/`HTTPS_PROXY` - Proxy configuration for network requests

## Dependencies Deep Dive

### CustomTkinter (5.2.2+)
- Modern replacement for tkinter with better styling
- Built-in dark/light theme support
- Modern widgets (CTkButton, CTkFrame, CTkTextbox, etc.)
- Cross-platform compatibility

### PyInstaller (6.14.2+)
- Creates standalone executables
- Bundles Python interpreter and dependencies
- Windows-specific optimizations in build script
- Configured for windowed (no console) mode

## Type Checking Configuration

Located in `pyproject.toml`:
- Uses basedpyright with "standard" mode
- Configured for Python 3.11 on Windows
- Excludes build artifacts and caches
- Points to virtual environment for library resolution

This comprehensive guide should help any future Claude Code instance quickly understand the project structure, build process, and development patterns used in this codebase.