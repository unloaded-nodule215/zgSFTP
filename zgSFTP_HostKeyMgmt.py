#!/usr/bin/env python3
#
#    zgSFTP - Host Key Manager
#

import os
from os.path import isfile, expanduser, join
import paramiko
import cryptography.hazmat.primitives.asymmetric.ed25519 as ed25519
import cryptography.hazmat.primitives.serialization as serialization
from tkinter import *
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox
from tkinter import filedialog
import host_keys
import zgSFTP_FileDialogs as Filedialogs

ZGSFTP_DIR = os.path.join(expanduser('~'), '.zgSFTP')
KEYS_DIR = os.path.join(ZGSFTP_DIR, 'keys')


def ensure_keys_dir():
    """Ensure the keys directory exists."""
    if not os.path.exists(ZGSFTP_DIR):
        os.makedirs(ZGSFTP_DIR, mode=0o700)
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR, mode=0o700)


def list_local_keys():
    """List all local SSH keys in ~/.zgSFTP/keys/."""
    keys = []
    if not os.path.exists(KEYS_DIR):
        return keys
    
    for filename in os.listdir(KEYS_DIR):
        if filename.endswith('.pub'):
            key_name = filename[:-4]
            private_key_path = os.path.join(KEYS_DIR, key_name)
            public_key_path = os.path.join(KEYS_DIR, key_name + '.pub')
            
            if isfile(private_key_path) and isfile(public_key_path):
                with open(public_key_path, 'r') as f:
                    public_key_content = f.read().strip()
                keys.append({
                    'name': key_name,
                    'private_path': private_key_path,
                    'public_path': public_key_path,
                    'public_key': public_key_content
                })
    
    return keys


def generate_key_pair(name, passphrase=None):
    """Generate a new ED25519 key pair."""
    ensure_keys_dir()
    
    private_key_path = os.path.join(KEYS_DIR, name)
    public_key_path = os.path.join(KEYS_DIR, name + '.pub')
    
    if isfile(private_key_path):
        return False, 'Key already exists'
    
    # Generate key using cryptography
    crypto_key = ed25519.Ed25519PrivateKey.generate()
    
    # Serialize to OPENSSH format
    if passphrase:
        pem = crypto_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(passphrase.encode())
        )
    else:
        pem = crypto_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.OpenSSH,
            serialization.NoEncryption()
        )
    
    # Write private key
    with open(private_key_path, 'wb') as f:
        f.write(pem)
        os.chmod(private_key_path, 0o600)
    
    # Load into paramiko to get public key
    try:
        if passphrase:
            paramiko_key = paramiko.PKey.from_private_key_file(private_key_path, password=passphrase.encode())
        else:
            paramiko_key = paramiko.Ed25519Key.from_private_key_file(private_key_path)
    except Exception as e:
        return False, f'Failed to load generated key: {str(e)}'
    
    # Write public key
    with open(public_key_path, 'w') as f:
        f.write(f"ssh-ed25519 {paramiko_key.get_base64()} zgSFTP\n")
        os.chmod(public_key_path, 0o644)
    
    return True, 'Key generated successfully'


def import_key(name, private_key_path, passphrase=None):
    """Import an existing private key."""
    ensure_keys_dir()
    
    dest_private_path = os.path.join(KEYS_DIR, name)
    dest_public_path = os.path.join(KEYS_DIR, name + '.pub')
    
    if isfile(dest_private_path):
        return False, 'Key already exists'
    
    try:
        # Read the original key file
        with open(private_key_path, 'rb') as f:
            key_data = f.read()
        
        # Detect key type from file content
        key_data_str = key_data.decode('utf-8', errors='ignore')
        detected_type = 'UNKNOWN'
        if 'ssh-ed25519' in key_data_str:
            detected_type = 'ED25519'
        elif 'ssh-rsa' in key_data_str:
            detected_type = 'RSA'
        elif 'ssh-dss' in key_data_str:
            detected_type = 'DSA'
        elif 'ssh-ec' in key_data_str or 'ecdsa' in key_data_str.lower():
            detected_type = 'ECDSA'
        
        # Try to load key using specific key types
        key = None
        password = passphrase.encode() if passphrase else None
        
        for key_class in [paramiko.Ed25519Key, paramiko.RSAKey, paramiko.ECDSAKey]:
            try:
                key = key_class.from_private_key_file(private_key_path, password=password)
                break
            except Exception:
                continue
        
        if key is None:
            return False, 'Failed to load key'
        
        # Write the key data directly (preserve original format)
        with open(dest_private_path, 'wb') as f:
            f.write(key_data)
            os.chmod(dest_private_path, 0o600)
        
        # Write public key
        with open(dest_public_path, 'w') as f:
            f.write(f"{key.get_name()} {key.get_base64()} zgSFTP\n")
            os.chmod(dest_public_path, 0o644)
        
        return True, 'Key imported successfully'
    except Exception as e:
        return False, f'Import failed: {str(e)}'


def delete_key(name):
    """Delete a key pair."""
    private_key_path = os.path.join(KEYS_DIR, name)
    public_key_path = os.path.join(KEYS_DIR, name + '.pub')
    
    try:
        if isfile(private_key_path):
            os.remove(private_key_path)
        if isfile(public_key_path):
            os.remove(public_key_path)
        return True, 'Key deleted successfully'
    except Exception as e:
        return False, f'Delete failed: {str(e)}'


def load_key(name):
    """Load a private key for authentication."""
    private_key_path = os.path.join(KEYS_DIR, name)
    
    if not isfile(private_key_path):
        return None
    
    try:
        # Try Ed25519 first
        try:
            return paramiko.Ed25519Key.from_private_key_file(private_key_path)
        except Exception:
            # Fall back to generic PKey
            return paramiko.PKey.from_private_key_file(private_key_path)
    except paramiko.PasswordRequiredException:
        return 'PASSWORD_REQUIRED'
    except Exception:
        return None


class HostKeyManager:
    """Dialog for managing SSH host keys and client key pairs."""

    def __init__(self, master, icon, use_host_keys_var, selected_key_var):
        self.master = master
        self.use_host_keys_var = use_host_keys_var
        self.selected_key_var = selected_key_var
        self.result = None

        self.window = Toplevel(master)
        self.window.resizable(True, False)
        self.window.title('Host Key Manager')
        self.window.minsize(width=600, height=400)

        self.icon = icon

        self.create_widgets()
        self.load_keys()

        Filedialogs.center_window(master, self.window)
        self.window.transient(master)
        self.window.focus_force()

        max_attempts = 10
        for _ in range(max_attempts):
            try:
                self.window.grab_set()
                break
            except Exception:
                import time
                time.sleep(0.1)

    def create_widgets(self):
        """Create the dialog widgets."""
        top_frame = ttk.Frame(self.window)
        top_frame.pack(fill=X, padx=5, pady=5)

        ttk.Label(top_frame, image=self.icon).pack(side=LEFT, padx=3)
        ttk.Label(top_frame, text='Host Key Manager').pack(side=LEFT, padx=5)

        use_keys_frame = ttk.Frame(self.window)
        use_keys_frame.pack(fill=X, padx=5, pady=5)

        self.use_host_keys_check = ttk.Checkbutton(
            use_keys_frame,
            text='Use Host Keys (disables password authentication)',
            variable=self.use_host_keys_var,
            command=self.on_use_host_keys_change
        )
        self.use_host_keys_check.pack(side=LEFT)

        keys_frame = ttk.LabelFrame(self.window, text='Installed Keys')
        keys_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        list_frame = ttk.Frame(keys_frame)
        list_frame.pack(fill=BOTH, expand=True)

        self.vbar = ttk.Scrollbar(list_frame, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)

        columns = ('name', 'type', 'fingerprint')
        self.key_treeview = ttk.Treeview(list_frame, columns=columns, show='headings', yscrollcommand=self.vbar.set, height=20)
        self.key_treeview.pack(fill=BOTH, expand=True)
        self.vbar.config(command=self.key_treeview.yview)

        self.key_treeview.heading('name', text='Name')
        self.key_treeview.heading('type', text='Type')
        self.key_treeview.heading('fingerprint', text='Fingerprint')
        self.key_treeview.column('name', width=150)
        self.key_treeview.column('type', width=100)
        self.key_treeview.column('fingerprint', width=300)

        style = ttk.Style()
        style.configure('Treeview', rowheight=25)

        self.key_treeview.bind('<<TreeviewSelect>>', self.on_key_select)

        button_frame = ttk.Frame(keys_frame)
        button_frame.pack(fill=X, pady=5)

        self.generate_button = ttk.Button(button_frame, text='Generate', command=self.generate_key)
        self.generate_button.pack(side=LEFT, padx=3)

        self.import_button = ttk.Button(button_frame, text='Import', command=self.import_key)
        self.import_button.pack(side=LEFT, padx=3)

        self.delete_button = ttk.Button(button_frame, text='Delete', command=self.delete_key, state=DISABLED)
        self.delete_button.pack(side=RIGHT, padx=3)

        self.close_button = ttk.Button(button_frame, text='Close', command=self.window.destroy)
        self.close_button.pack(side=RIGHT, padx=3)

    def on_use_host_keys_change(self):
        """Handle use host keys checkbox change."""
        pass

    def on_key_select(self, event):
        """Handle key selection in treeview."""
        selection = self.key_treeview.selection()
        if selection:
            self.delete_button.config(state=NORMAL)
            item = self.key_treeview.item(selection[0])
            key_name = item['values'][0]
            self.selected_key_var.set(key_name)
        else:
            self.delete_button.config(state=DISABLED)

    def load_keys(self):
        """Load and display all local keys."""
        for item in self.key_treeview.get_children():
            self.key_treeview.delete(item)

        keys = list_local_keys()
        for key_info in keys:
            key_type = 'UNKNOWN'
            fingerprint = 'N/A'
            
            # Detect key type from public key file
            try:
                with open(key_info['public_path'], 'r') as f:
                    public_key_content = f.read().strip()
                    parts = public_key_content.split()
                    if len(parts) >= 1:
                        key_type = parts[0].upper().replace('SSH-', '')
            except Exception:
                pass
            
            # Try to load private key to get fingerprint
            password_required = False
            try:
                # Try specific key types first
                key = None
                for key_class in [paramiko.Ed25519Key, paramiko.RSAKey, paramiko.ECDSAKey]:
                    try:
                        key = key_class.from_private_key_file(key_info['private_path'])
                        break
                    except paramiko.PasswordRequiredException:
                        password_required = True
                        break
                    except Exception:
                        continue
                
                if password_required:
                    key_type = key_type + '*' if key_type != 'UNKNOWN' else 'KEY*'
                    fingerprint = '(protected)'
                elif key is None:
                    pass  # Keep UNKNOWN/N/A
                else:
                    fingerprint = key.get_fingerprint().hex()
                    if key_type == 'UNKNOWN':
                        key_type = key.get_name().upper().replace('SSH-', '')
            except Exception:
                pass

            self.key_treeview.insert('', END, values=(key_info['name'], key_type, fingerprint))

    def generate_key(self):
        """Generate a new key pair."""
        dialog = GenerateKeyDialog(self.window, self.icon)
        self.window.wait_window(dialog.window)

        if dialog.result:
            name = dialog.name_var.get().strip()
            passphrase = dialog.passphrase_var.get()

            if not name:
                messagebox.showerror('Error', 'Key name is required')
                return

            success, message = generate_key_pair(name, passphrase)
            messagebox.showinfo('Generate Key', message)

            if success:
                self.load_keys()

    def import_key(self):
        """Import an existing key."""
        file_path = filedialog.askopenfilename(
            title='Select Private Key File',
            filetypes=[('All Files', '*.*')]
        )

        if not file_path:
            return

        dialog = ImportKeyDialog(self.window, self.icon, file_path)
        self.window.wait_window(dialog.window)

        if dialog.result:
            name = dialog.name_var.get().strip()
            passphrase = dialog.passphrase_var.get()

            if not name:
                messagebox.showerror('Error', 'Key name is required')
                return

            success, message = import_key(name, file_path, passphrase)
            messagebox.showinfo('Import Key', message)

            if success:
                self.load_keys()

    def delete_key(self):
        """Delete the selected key."""
        selection = self.key_treeview.selection()
        if not selection:
            return

        item = self.key_treeview.item(selection[0])
        key_name = item['values'][0]

        result = messagebox.askyesno(
            'Delete Key',
            f'Delete key "{key_name}"?\n\nThis will remove both the private and public key files.\n\nAlso remove from known_hosts?'
        )

        if result:
            success, message = delete_key(key_name)

            if success:
                known_hosts = host_keys.list_known_hosts()
                for host, port, key_type, fingerprint in known_hosts:
                    if key_name in host or key_name in port:
                        host_keys.remove_known_host(host, port)

                messagebox.showinfo('Delete Key', message)
                self.load_keys()
                self.delete_button.config(state=DISABLED)
                self.selected_key_var.set('')


class GenerateKeyDialog:
    """Dialog for generating a new key pair."""

    def __init__(self, master, icon):
        self.result = False
        self.name_var = StringVar()
        self.passphrase_var = StringVar()

        self.window = Toplevel(master)
        self.window.resizable(False, False)
        self.window.title('Generate ED25519 Key')

        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill=BOTH)

        ttk.Label(frame, text='Key Name:').grid(row=0, column=0, sticky=W, pady=5)
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)

        ttk.Label(frame, text='Passphrase (optional):').grid(row=1, column=0, sticky=W, pady=5)
        ttk.Entry(frame, textvariable=self.passphrase_var, show='*', width=30).grid(row=1, column=1, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text='Generate', command=self.on_generate).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text='Cancel', command=self.window.destroy).pack(side=LEFT, padx=5)

        Filedialogs.center_window(master, self.window)
        self.window.transient(master)
        self.window.focus_force()

        max_attempts = 10
        for _ in range(max_attempts):
            try:
                self.window.grab_set()
                break
            except Exception:
                import time
                time.sleep(0.1)

    def on_generate(self):
        self.result = True
        self.window.destroy()


class ImportKeyDialog:
    """Dialog for importing an existing key."""

    def __init__(self, master, icon, file_path):
        self.result = False
        self.name_var = StringVar()
        self.passphrase_var = StringVar()
        self.file_path = file_path

        self.window = Toplevel(master)
        self.window.resizable(False, False)
        self.window.title('Import SSH Key')

        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill=BOTH)

        ttk.Label(frame, text='File:', anchor=W).grid(row=0, column=0, columnspan=2, sticky=W, pady=5)
        ttk.Label(frame, text=file_path, foreground='blue').grid(row=1, column=0, columnspan=2, sticky=W, pady=5)

        ttk.Label(frame, text='Key Name:').grid(row=2, column=0, sticky=W, pady=5)
        default_name = os.path.basename(file_path).rsplit('.', 1)[0]
        self.name_var.set(default_name)
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=2, column=1, pady=5)

        ttk.Label(frame, text='Passphrase (if protected):').grid(row=3, column=0, sticky=W, pady=5)
        ttk.Entry(frame, textvariable=self.passphrase_var, show='*', width=30).grid(row=3, column=1, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text='Import', command=self.on_import).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text='Cancel', command=self.window.destroy).pack(side=LEFT, padx=5)

        Filedialogs.center_window(master, self.window)
        self.window.transient(master)
        self.window.focus_force()

        max_attempts = 10
        for _ in range(max_attempts):
            try:
                self.window.grab_set()
                break
            except Exception:
                import time
                time.sleep(0.1)

    def on_import(self):
        self.result = True
        self.window.destroy()


class host_key_dialog:
    """Dialog for accepting new SSH host keys."""

    def __init__(self, master, Title, icon, host, port, key_type, fingerprint):
        self.result = None

        self.host_key_dialog_window = Toplevel(master)
        self.host_key_dialog_window.resizable(False, False)
        self.host_key_dialog_window.title(Title)

        self.icon_frame = ttk.Frame(self.host_key_dialog_window)
        self.icon_frame.pack(side = LEFT, fill = Y)
        self.entry_frame = ttk.Frame(self.host_key_dialog_window)
        self.entry_frame.pack(side = LEFT, fill = Y, expand = True)

        ttk.Label(self.icon_frame, image = icon).pack(padx = 3, pady = 3)

        message = ('New SSH Host\n\n'
                   f'Host: {host}:{port}\n'
                   f'Key Type: {key_type}\n\n'
                   f'Fingerprint:\n{fingerprint}\n\n'
                   'Do you want to accept and continue?')

        ttk.Label(self.entry_frame, text = message, anchor = 'w', justify = LEFT).pack(padx = 5, fill = X, expand = True)

        self.accept_button = ttk.Button(self.entry_frame, text = 'Accept & Save', command = self.accept)
        self.accept_button.pack(side = RIGHT, pady = 3, padx = 3)
        self.reject_button = ttk.Button(self.entry_frame, text = 'Reject', command = self.reject)
        self.reject_button.pack(side = RIGHT, pady = 3, padx = 3)

        Filedialogs.center_window(master, self.host_key_dialog_window)
        self.host_key_dialog_window.transient(master)
        self.host_key_dialog_window.focus_force()

        max_attempts = 10
        for _ in range(max_attempts):
            try:
                self.host_key_dialog_window.grab_set()
                break
            except Exception:
                import time
                time.sleep(0.1)

    def accept(self):
        self.result = True
        self.host_key_dialog_window.destroy()

    def reject(self):
        self.result = False
        self.host_key_dialog_window.destroy()

    def destroy(self):
        self.host_key_dialog_window.destroy()
