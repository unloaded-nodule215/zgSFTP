# zgSFTP - Agent Guidelines

## Project Overview
zgSFTP is a Python 3 SFTP client GUI application built with tkinter. Supports file operations (upload, download, copy, move, search, delete) on Linux, Windows, and macOS.

**Version**: 0.1.3
**Copyright**: zgSFTP (2026), Vishnu Shankar (2018-2019)
**Platforms**: Linux, Windows 11, macOS

## Build / Lint / Test Commands
- **Build**: No build system; run directly with Python 3.
- **Lint**: No linter configured. Use `flake8` if added.
- **Test**: No test suite. Run manual tests (see below). Add pytest later.

### Running a Single Test (placeholder)
```bash
# If a test file `tests/test_sftp.py` is added:
python -m pytest tests/test_sftp.py::TestSFTP::test_connect -v
```

## Manual Testing Procedure
1. Start app: `python3 zgSFTP.py`
2. Connect to a test SFTP server.
3. Perform file upload, download, copy, move, delete.
4. Test transfer cancellation.
5. Drag‑and‑drop file selection.
6. Verify host key storage and warning.
7. Resize windows; note DPI scaling blur.

## Code Style Guidelines
### Imports
Order: stdlib → third‑party → local. Alphabetical within groups.

```python
import os
from os.path import isfile, join
import threading
import queue
import configparser
from urllib.parse import unquote
from tkinter import *
from tkinter import font, ttk, PhotoImage, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from zgSFTP_SFTP_controller import *
import zgSFTP_ToolbarButton as ToolbarButton
import zgSFTP_FileDialogs as Filedialogs
import platform
```

### Formatting
- 4 spaces indentation, no tabs.
- Line length ~80‑100 chars; flexible.
- Blank lines separate logical sections.
- Space around operators (`=`, `+`, `-`, `==`).

### Naming Conventions
- Classes: `snake_case` (e.g., `sftp_controller`)
- Functions/methods: `snake_case` (e.g., `connect_to`)
- Variables: `snake_case` (e.g., `self.file_list`)
- Files: `zgSFTP_*.py`
- Icons: `Icons/*.png`

### Types
- No type hints; keep consistency.

### Error Handling
- `except Exception:` for broad catches.
- Use `==` for value checks, not `is`.
- Use `len(data)` for byte length.
- GUI errors via `messagebox`.

### Comments
- `#/!` for important warnings in docstrings.
- Inline comments for non‑obvious logic.
- Keep copyright header.

### GUI Patterns
- Prefer `ttk` widgets.
- Keep image references (`self.icon = PhotoImage(...)`).
- Center dialogs with `center_window()`.
- Bind with lambda to ignore event: `widget.bind('<Return>', lambda e: callback())`.

### Threading
- `threading.Thread` for network work.
- Protect shared state with `threading.Lock()`.
- Use `queue.Queue` for communication; daemon threads for background jobs.

### Platform Specific
```python
if platform.system() == 'Windows':
    import ctypes, win32api
```

### File Ops
- Use `os.path` for paths.
- Change to script dir for relative paths:
```python
abspath = os.path.abspath(__file__)
os.chdir(os.path.dirname(abspath))
```

## Known Issues
- DPI scaling results in blurry UI.
- No formal test suite; bugs may exist.

## Cursor / Copilot Rules
No `.cursor/rules/` or `.cursorrules` directory. No `.github/copilot-instructions.md`. No rules to load.
