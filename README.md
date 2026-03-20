<div style="text-align:center">
    <img src ="https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Screenshot.png" />
</div>

# About
zgSFTP is an SFTP client written in python using the tkinter GUI toolkit. Can upload, download, create, rename, copy, move and search files/folders. This is a vibe-coded project.

## ⚠️ Alpha Status - Not for Production Use ⚠️
**This software is in ALPHA development and should NOT be used for production workloads.** 
- Features may be incomplete or unstable
- Bugs are expected and may cause data loss
- No warranty or support is provided
- Use at your own risk
- Always have backups before testing with important files

#### Currently supported platforms:
+ Linux - tested with Python 3.14.
+ Windows 11 (Untested)
+ MacOS (Untested)

# Getting zgSFTP
The only option currently is to run from source. Simpler options are on the radar.

#### Linux:
+ Use git to clone this repo.
+ Create a python virtual environment - `python -m venv .venv`
+ Enter the venv: `source .venv/bin/activate`
+ Install the dependencies: `pip install -r requirements.txt`
+ Run: `python zgSFTP.py`
+ Leave venv: `deactivate`

#### Windows:
+ Untested.
+ Install Python 3.14.x from https://www.python.org/downloads/windows/
+ Install git and clone this repo, or download the zip and unzip to a folder of your choice.
+ Open a command prompt or terminal and navigate to your zgSFTP source folder.
+ Run: `pip install -r requirements.txt` and wait for it to finish. (Optional: Create a venv first)
+ Run: `python zgSFTP.py` 

#### MacOS:
+ Untested.
+ Install Python 3.14.x from homebrew (https://brew.sh).
+ Install git and clone this repo, or download the zip and unzip to a folder of your choice.
+ Open a terminal and navigate to your zgSFTP source folder.
+ Create a python virtual environment: `python3 -m venv .venv`
+ Run: `pip3 install -r requirements.txt` and wait for it to finish.
+ Run: `python3 zgSFTP.py`
+ Run: `deactivate` to leave the venv.

# Controls (TODO: Massive UI cleanup)
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/connect_big.png)
*Start connection*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/upload_big.png)
*Upload files or folders*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/download_big.png)
*Save/Download files or folders*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/newfolder_big.png)
*Create a new directory*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/delete_big.png)
*Delete files or folders*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/properties_big.png)
*Edit/View properties*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/cut_big.png)
*Cut*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/copy_big.png)
*Copy*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/paste_big.png)
*Paste*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/info_big.png)
*About/Help*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/gotopath_big.png)
*Goto a path*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/search_big.png)
*Search/Find files or folders*
+ ![](https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Icons/up_big.png)
*Goto parent directory*

# License
+ MIT License. See: https://github.com/unloaded-nodule215/zgSFTP/blob/master/LICENSE.md

# Bugs
+ Vibe coded AI slop :)
+ Known issues are tracked and fixed in development

# Recent Updates
+ Transfer queue for multi-file transfers (alpha)
+ Queue can be paused/resumed during transfers
+ Queue persists to disk for recovery
+ Stop Transfer now stops entire queue
+ Failed transfers can be retried

# TODO
+ Look into HiDPI stuff.
+ Modernize icons and add text to make functions more obvious.
+ Improve queue stability and error handling

# Note
This project was forked from: https://github.com/RainingComputers/whipFTP as a way to test local vibe-coding with Qwen models and OpenCode.
