# zgSFTP - Agent Guidelines

## Project Overview
zgSFTP is a Python 3 FTP/SFTP client GUI application built with tkinter. It supports file operations (upload, download, copy, move, search, delete) on Linux, Windows, and macOS.

## Running the Application

```bash
# Linux/macOS
python3 zgSFTP.py

# Windows (after installing dependencies)
python zgSFTP.pyw
```

## Installing Dependencies

```bash
python3 install_dependencies.py
```

Required packages:
- `paramiko` - SFTP connections
- `psutil` - System utilities
- `pypiwin32` - Windows-specific features

## Build/Lint/Test Commands

**No formal test suite exists.** The project has no automated tests, linters, or type checkers configured.

Manual testing approach:
1. Run the application: `python3 zgSFTP.py`
2. Test FTP/SFTP connections to a test server
3. Verify file operations (upload, download, copy, move, delete, search)

## Code Style Guidelines

### Imports
- Standard library imports first (alphabetically grouped)
- Third-party imports after standard library
- Local imports last (relative to project root)

```python
import os
from os.path import isfile, join
import threading
import queue
from tkinter import *
from tkinter import font
from tkinter import ttk
import platform
from FTP_controller import *
from SFTP_controller import *
```

### Formatting
- **Indentation**: 4 spaces (no tabs)
- **Line length**: Flexible, but prefer ~80-100 characters
- **Blank lines**: Use to separate logical sections within functions
- **Spacing**: Space around operators (`=` `+` `-` `==` `is`)

```python
# Good
if(self.hidden_files is True or line.split()[8][0] is not '.'):
    files.append(line)

# Method calls with spaces around operators in arguments
master.minsize(width = 860, height = 560)
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `ftp_controller`, `sftp_controller`, `app`, `TkDND`)
- **Methods/Functions**: `snake_case` (e.g., `connect_to`, `get_file_list`, `toggle_hidden_files`)
- **Instance variables**: `snake_case` (e.g., `self.file_list`, `self.max_width`)
- **Constants**: Not commonly used in this codebase
- **Files**: `snake_case.py` (e.g., `FTP_controller.py`, `zgSFTP_FileDialogs.py`)

### Type Hints
- **Not used** in this codebase
- Do not add type hints to maintain consistency

### Error Handling
- **Bare except clauses** are used for simple boolean checks:
```python
def is_there(self, path):
    try:
        self.ftp.stat(path)
        return True
    except:
        return False
```

- **Comments indicate** where exception handling is deferred:
```python
#/!\ Some functions in this class has no exception handling, it has to be done outside
```

- Use `messagebox` for user-facing errors in GUI context

### Comments
- Use `#/!\` for important warnings in docstrings
- Inline comments explain non-obvious logic
- File headers include copyright notices

```python
#/!\ Although the comments and variable names say 'file_list', or 'items' it includes folders also
```

### GUI Patterns (tkinter)
- Use `ttk` widgets for themed appearance
- Store image references to prevent garbage collection:
```python
self.icon = PhotoImage(file='Icons/connect.png')
```
- Center dialogs using `center_window()` utility
- Use lambda bindings for widget callbacks

### Threading
- Use `threading.Thread` for network operations
- Protect shared state with `threading.Lock()`:
```python
self.thread_lock = threading.Lock()
```
- Queue-based communication for thread-safe data passing

### Platform-Specific Code
- Use `platform.system()` for conditional imports:
```python
if(platform.system() is 'Windows'):
    import ctypes
    import win32api
```

### File Operations
- Use `os.path` utilities for path manipulation
- Change to script directory for relative paths:
```python
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
```

## Architecture

### Main Components
- `zgSFTP.py` - Main application window and GUI logic
- `FTP_controller.py` - FTP protocol implementation
- `SFTP_controller.py` - SFTP protocol implementation (paramiko)
- `zgSFTP_FileDialogs.py` - Custom dialogs (connect, search, properties, etc.)
- `TkDND_wrapper.py` - Drag-and-drop support
- `zgSFTP_ToolbarButton.py` / `zgSFTP_PaneButton.py` - Custom button widgets
- `drive_detect.py` - Mount point detection

### Controller Pattern
Both `ftp_controller` and `sftp_controller` share a common interface:
- `connect_to(host, username, password, port)`
- `get_file_list()`, `get_detailed_file_list()`
- `upload_file()`, `download_file()`
- `create_dir()`, `delete_dir()`, `rename_dir()`
- `search_files()`, `chmod()`

## Common Tasks

### Adding a New Dialog
1. Create class in `zgSFTP_FileDialogs.py`
2. Use `Toplevel()` for the window
3. Center with `center_window(master, dialog)`
4. Use `ttk` widgets for consistent styling

### Adding a File Operation
1. Implement in both `FTP_controller` and `SFTP_controller`
2. Add GUI callback in `zgSFTP.py`
3. Use threading for long-running operations
4. Update status bar for user feedback

### Icon Management
- Icons stored in `Icons/` directory
- Use `.png` format with consistent naming
- Load with `PhotoImage(file='Icons/name.png')`

## Known Issues
- Application appears blurry with DPI scaling enabled
- Root directory search does not work
- Project is being rewritten in wxpython
