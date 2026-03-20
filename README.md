<div style="text-align:center">
    <img src ="https://raw.githubusercontent.com/unloaded-nodule215/zgSFTP/master/Screenshot.png" />
</div>

# About
zgSFTP is an SFTP client written in python using the tkinter GUI toolkit. Can upload, download, create, rename, copy, move and search files/folders. This is a vibe-coded project.

#### Currently supported platforms:
+ Linux - tested with Python 3.14.
+ Windows 11*
+ MacOS*

# Getting zgSFTP
The only option currently is to run from source. Simpler options are on the radar.

#### Windows:
+ Install Python 3.14.x from https://www.python.org/downloads/windows/
+ Install git and clone this repo, or download the zip and unzip to a folder of your choice.
+ Open a command prompt or terminal and navigate to your zgSFTP source folder.
+ Run: `pip install -r requirements.txt` and wait for it to finish. (Optional: Create a venv first)
+ Run: `python zgSFTP.py` 

#### MacOS:
+ Tested with Python 3.14 on Apple Silicon. Full drag-and-drop support via tkinterdnd2.
+ Install Python 3.14.x from https://www.python.org/downloads/mac-osx/
+ Install git and clone this repo, or download the zip and unzip to a folder of your choice.
+ Open a terminal and navigate to your zgSFTP source folder.
+ Run: `pip3 install -r requirements.txt` and wait for it to finish. (Optional: Create a venv first)
+ Run: `python3 zgSFTP.py`

#### Linux:
+ Use git to clone this repo
+ Install the dependencies: `pip install -r requirements.txt`
+ Run: `python zgSFTP.py`

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
+ Stopping a transfer doesn't stop all transfers. Annoying on many little files.

# TODO
+ Simple method to save and restore last connected site. Not sure if a full bookmark system is in the scope of this simple app.
+ Look into HiDPI stuff.
+ Modernize icons and add text to make functions more obvious.

# Note
This project was forked from: https://github.com/RainingComputers/whipFTP as a way to test local vibe-coding with Qwen models and OpenCode.
