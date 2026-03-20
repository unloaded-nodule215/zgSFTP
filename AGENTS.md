# zgSFTP - Agent Guidelines

## Project Overview
zgSFTP is a Python 3 SFTP client GUI application built with tkinter. It supports file operations (upload, download, copy, move, search, delete) on Linux, Windows, and macOS.

**Version**: 0.1.0  
**Copyright**: zgSFTP (2026), Vishnu Shankar (2018-2019)  
**Supported Platforms**: Linux, Windows 11, macOS

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
- `tkinterdnd2` - Drag and drop support

## Build/Lint/Test Commands

**No formal test suite exists.** The project has no automated tests, linters, or type checkers configured.

### Testing
Since there are no formal tests, manual testing is required:

1. Run the application: `python3 zgSFTP.py`
2. Test SFTP connections to a test server
3. Verify file operations (upload, download, copy, move, delete, search)
4. Test transfer cancellation functionality

### Build Commands
The project does not use a build system. Run directly with Python 3.

### Lint/Type Check Commands
No linters or type checkers are configured. The codebase uses:
- Python 3 (Python 3.14 compatible)
- No type hints (maintains consistency with existing codebase)

## Code Style Guidelines

### Imports
Order imports as follows:
1. Standard library imports (alphabetically grouped)
2. Third-party imports (alphabetically grouped)
3. Local imports (relative to project root, alphabetically)

```python
import os
from os.path import isfile, join
import threading
import queue
import configparser
from urllib.parse import unquote
from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from SFTP_controller import *
import zgSFTP_ToolbarButton as ToolbarButton
import zgSFTP_FileDialogs as Filedialogs
import platform
```

### Formatting
- **Indentation**: 4 spaces (no tabs)
- **Line length**: Flexible, but prefer ~80-100 characters
- **Blank lines**: Use to separate logical sections within functions
- **Spacing**: Space around operators (`=`, `+`, `-`, `==`)

```python
# Good
if self.hidden_files is True or line.split()[8][0] != '.':
    files.append(line)

# Method calls with spaces around operators in arguments
master.minsize(width = 860, height = 560)
```

### Naming Conventions
- **Classes**: `snake_case` (e.g., `sftp_controller`, `app`, `console_dialog`)
- **Methods/Functions**: `snake_case` (e.g., `connect_to`, `get_file_list`, `toggle_hidden_files`)
- **Instance variables**: `snake_case` (e.g., `self.file_list`, `self.max_width`)
- **Constants**: Not commonly used in this codebase
- **Files**: `snake_case.py` (e.g., `SFTP_controller.py`, `zgSFTP_FileDialogs.py`)

### Type Hints
- **Not used** in this codebase
- Do not add type hints to maintain consistency

### Error Handling (Python 3.14 Compatible)
- Use `except Exception:` instead of bare `except:`
- Use `==` for value comparisons, not `is`
- Use `len(data)` for bytes length, not `sys.getsizeof(data)`
- Use `messagebox` for user-facing errors in GUI context

```python
# Good (Python 3.14 compatible)
def is_there(self, path):
    try:
        self.sftp.stat(path)
        return True
    except Exception:
        return False

# Good comparisons
if self.hidden_files == True:
    pass
if line.split()[8][0] != '.':
    pass
```

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
- Use lambda bindings for widget callbacks that need to ignore event args:
```python
self.entry.bind('<Return>', lambda e: callback())
```

### Threading
- Use `threading.Thread` for network operations
- Protect shared state with `threading.Lock()`:
```python
self.thread_lock = threading.Lock()
```
- Queue-based communication for thread-safe data passing
- Use daemon threads for background operations

### Platform-Specific Code
- Use `platform.system()` for conditional imports:
```python
if platform.system() == 'Windows':
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
- `SFTP_controller.py` - SFTP protocol implementation (paramiko)
- `zgSFTP_FileDialogs.py` - Custom dialogs (connect, search, properties, etc.)
- `TkDND_wrapper.py` - Drag-and-drop support
- `zgSFTP_ToolbarButton.py` / `zgSFTP_PaneButton.py` - Custom button widgets
- `drive_detect.py` - Mount point detection

### Controller Pattern
The `sftp_controller` class provides the SFTP interface:
- `connect_to(host, username, password, port)`
- `get_file_list()`, `get_detailed_file_list()`
- `upload_file()`, `download_file()`
- `create_dir()`, `delete_dir()`, `rename_dir()`
- `search()`, `chmod()`

### Progress Dialog Pattern
File transfers use a `console_dialog` class that shows progress:
- Created via `create_progress_window()` in main app
- Progress updates via `progress(file_name, status)` method
- Supports transfer cancellation with "Stop Transfer" button

## Common Tasks

### Adding a New Dialog
1. Create class in `zgSFTP_FileDialogs.py`
2. Use `Toplevel()` for the window
3. Center with `center_window(master, dialog)`
4. Use `ttk` widgets for consistent styling

### Adding a File Operation
1. Implement in `SFTP_controller`
2. Add GUI callback in `zgSFTP.py`
3. Use threading for long-running operations
4. Update status bar for user feedback
5. Consider adding cancellation support

### Icon Management
- Icons stored in `Icons/` directory
- Use `.png` format with consistent naming
- Load with `PhotoImage(file='Icons/name.png')`
- Store references to prevent garbage collection

## Known Issues
- Application appears blurry with DPI scaling enabled
- Root directory search does not work
