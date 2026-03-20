#zgSFTP, Copyrights Vishnu Shankar B,

import os
from os import listdir
from os.path import isfile, join, normpath, abspath
import shutil
import paramiko
import tempfile
import secrets
import threading
import host_keys
import base64

class paramiko_sftp_client(paramiko.SFTPClient):
    def cwd(self, path):
        self.chdir(path)

    def go_to_home(self, username):
        try:
            self.cwd('/home/' + username)
        except Exception:    
            self.cwd('/')



class sftp_controller:  
    #/!\ Although the comments and variable names say 'file_name'/'file_anything' it inculdes folders also
    #Some functions in this class has no exception handling, it has to be done outside

    def __init__(self):
        #List to store file search and search keywords
        self.search_file_list = []
        self.detailed_search_file_list = []
        self.keyword_list = []

        #Variable to hold the max no character name in file list (used for padding in GUIs)
        self.max_len = 0   
        self.max_len_name = ''     

        #Variable to tell weather hidden files are enabled
        self.hidden_files = False

        #Variable to track transfer cancellation
        self.cancel_transfer = False
        self.cancel_lock = threading.Lock()

    def cancel_current_transfer(self):
        with self.cancel_lock:
            self.cancel_transfer = True

    def reset_cancel_flag(self):
        with self.cancel_lock:
            self.cancel_transfer = False

    def _validate_path(self, path):
        normalized = normpath(path)
        if normalized.startswith('..'):
            return False
        if normalized.startswith('/') and path.count('..') > 0:
            return False
        return True

    def connect_to(self, Host, Username = ' ', Password = ' ', Port = 22, host_key_callback = None): 
        self.transport = paramiko.Transport((Host, Port))
        
        server_key = self.transport.get_remote_server_key()
        fingerprint = server_key.get_fingerprint().hex()
        key_type = server_key.get_name()
        key_blob = base64.b64encode(server_key.asbytes()).decode()
        
        is_known, key_matches, stored_fingerprint = host_keys.is_host_known(Host, Port, server_key)
        
        if is_known and not key_matches:
            raise Exception('Host key verification failed: Key has changed! Possible man-in-the-middle attack.')
        
        if not is_known and host_key_callback is not None:
            accepted = host_key_callback(Host, Port, key_type, fingerprint)
            if not accepted:
                raise Exception('Host key not accepted by user')
            host_keys.save_known_host(Host, Port, key_type, key_blob, fingerprint)
        
        self.transport.connect(username = Username, password = Password)
        self.ftp = paramiko_sftp_client.from_transport(self.transport)
        self.ftp.go_to_home(Username)

    def toggle_hidden_files(self):
        self.hidden_files = not self.hidden_files 

    def get_detailed_file_list(self, ignore_hidden_files_flag = False):
        files = []
        for attr in self.ftp.listdir_attr():
            if(self.hidden_files == True or str(attr).split()[8][0] != '.') or ignore_hidden_files_flag == True:
                files.append(str(attr))
        return files

    def get_file_list(self, detailed_file_list):
        self.max_len = 0
        self.max_len_name = ''
        file_list = []
        for x in detailed_file_list:
            #Remove details and append only the file name
            name = ' '.join(x.split()[8:])
            file_list.append(name)
            if(len(name) > self.max_len):
                self.max_len = len(name)
                self.max_len_name = name
        return file_list

    def get_detailed_search_file_list(self):
        return self.detailed_search_file_list

    def get_search_file_list(self):
        self.max_len = 0
        self.max_len_name = ''
        for name in self.search_file_list:
            if(len(name) > self.max_len):
                self.max_len = len(name)
                self.max_len_name = name
        return self.search_file_list

    def chmod(self, filename, permissions):
        self.ftp.chmod(filename, permissions)

    def is_there(self, path):
        try:
            self.ftp.stat(path)
            return True
        except Exception:
            return False

    def rename_dir(self, rename_from, rename_to):
        self.ftp.rename(rename_from, rename_to)    

    def move_dir(self, rename_from, rename_to, status_command, replace_command):
        if(self.is_there(rename_to) == True):
            if(replace_command(rename_from, 'File/Folder exists in destination folder') == True):
                self.delete_dir(rename_to, status_command)
            else:
                return
        try:
            self.ftp.rename(rename_from, rename_to) 
            status_command(rename_from, 'Moved')
        except Exception:
            status_command(rename_from, 'Failed to move')

    def copy_file(self, file_dir, copy_from, file_size, status_command, replace_command):
        if not self._validate_path(file_dir) or not self._validate_path(copy_from):
            status_command(copy_from, 'Invalid path')
            return
        
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix='sftp_copy_')
            temp_file = os.path.join(temp_dir, os.path.basename(copy_from))
            
            dir_path_to_copy = self.ftp.getcwd()
            self.ftp.cwd(file_dir)
            
            def download_status(name, msg):
                status_command(name, msg)
            def download_replace(name, msg):
                return replace_command(name, msg)
            
            self.ftp.get(copy_from, temp_file)
            status_command(copy_from, 'Downloaded to temp')
            
            self.ftp.cwd(dir_path_to_copy)
            
            def upload_status(name, msg):
                status_command(name, msg)
            def upload_replace(name, msg):
                return replace_command(name, msg)
            
            self.ftp.put(temp_file, copy_from)
            status_command(copy_from, 'Upload complete')
        except Exception as e:
            status_command(copy_from, 'Copy failed: ' + str(e))
        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass

    def copy_dir(self, file_dir, copy_from, status_command, replace_command):
        if not self._validate_path(file_dir) or not self._validate_path(copy_from):
            status_command(copy_from, 'Invalid path')
            return
        
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix='sftp_copy_')
            temp_path = os.path.join(temp_dir, os.path.basename(copy_from))
            
            dir_path_to_copy = self.ftp.getcwd()
            self.ftp.cwd(file_dir)
            
            def download_status(name, msg):
                status_command(name, msg)
            def download_replace(name, msg):
                return replace_command(name, msg)
            
            self._download_dir_recursive(copy_from, temp_path, download_status, download_replace)
            status_command(copy_from, 'Downloaded to temp')
            
            self.ftp.cwd(dir_path_to_copy)
            
            def upload_status(name, msg):
                status_command(name, msg)
            def upload_replace(name, msg):
                return replace_command(name, msg)
            
            self._upload_dir_recursive(temp_path, copy_from, upload_status, upload_replace)
            status_command(copy_from, 'Upload complete')
        except Exception as e:
            status_command(copy_from, 'Copy failed: ' + str(e))
        finally:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass

    def delete_file(self, file_name, status_command):
        try:
            self.ftp.remove(file_name)
            status_command(file_name, 'Deleted')
        except Exception:
            status_command(file_name, 'Failed to delete')

    def delete_dir(self, dir_name, status_command):
        #Go into the directory
        self.ftp.cwd(dir_name)
        #Get file lists
        try:
            detailed_file_list = self.get_detailed_file_list(True)
        except Exception:
            status_command(dir_name, 'Failed to delete directory')
            return
        file_list = self.get_file_list(detailed_file_list)
        for file_name, file_details in zip(file_list, detailed_file_list):
            #If directory
            if(self.is_dir(file_details)):
                self.delete_dir(file_name, status_command)
            #If file
            else:
                self.delete_file(file_name, status_command)
        #Go back to parent directory and delete it
        try:
            self.ftp.cwd('..')
            status_command(dir_name, 'Deleting directory')
            self.ftp.rmdir(dir_name)
        except Exception:
            status_command(dir_name, 'Failed to delete directory')

    def upload_file(self, file_name, file_size, status_command, replace_command):
        #Function to update status
        def upload_progress(transferred, remaining):
            with self.cancel_lock:
                cancelled = self.cancel_transfer
            if cancelled:
                raise Exception('Transfer cancelled')
            if not cancelled:
                status_command(file_name, str(min(round((transferred/file_size) * 100, 2), 100))+'%')
        #Check if the file is already present in ftp server
        if(self.is_there(file_name)):
            if(replace_command(file_name, 'File exists in destination folder') == False):
                return
        #Try to upload file
        try:
            status_command(file_name, 'Uploading')
            self.ftp.put(file_name, file_name, callback = upload_progress)
            status_command(file_name, 'Upload complete')
            status_command(None, 'newline')
        except Exception as e:
            if 'Transfer cancelled' in str(e):
                status_command(None, 'newline')
                status_command(file_name, 'Upload cancelled')
            else:
                status_command(file_name, 'Upload failed')
            return

    def upload_dir(self, dir_name, status_command, replace_command):
        #Change to directory
        os.chdir(dir_name)
        #Create directory in server and go inside
        try:
            if(not self.is_there(dir_name)):
                self.ftp.mkdir(dir_name)
                status_command(dir_name, 'Creating directory')
            else:
                status_command(dir_name, 'Directory exists')
            self.ftp.cwd(dir_name)
        except Exception:
            status_command(dir_name, 'Failed to create directory')
            return
        #Cycle through items
        for filename in os.listdir():
            #If file upload
            if(isfile(filename)):
                self.upload_file(filename, os.path.getsize(filename), status_command, replace_command)
            #If directory, recursive upload it
            else:
                self.upload_dir(filename, status_command, replace_command)
                
        #Got to parent directory
        self.ftp.cwd('..')
        os.chdir('..')

    def download_file(self, ftp_file_name, file_size, status_command, replace_command):
        #Function to update progress
        def download_progress(transferred, remaining):
            with self.cancel_lock:
                cancelled = self.cancel_transfer
            if cancelled:
                raise Exception('Transfer cancelled')
            if not cancelled:
                status_command(ftp_file_name, str(min(round((transferred/file_size) * 100, 2), 100))+'%')
        #Check if the file is already present in local directory
        if(isfile(ftp_file_name)):
            if(replace_command(ftp_file_name, 'File exists in destination folder') == False):
                return
        #Try to download file
        try:
            status_command(ftp_file_name, 'Downloading')
            self.ftp.get(ftp_file_name, ftp_file_name, callback = download_progress)
            status_command(ftp_file_name, 'Download complete')
            status_command(None, 'newline')
        except Exception as e:
            if 'Transfer cancelled' in str(e):
                status_command(None, 'newline')
                status_command(ftp_file_name, 'Download cancelled')
            else:
                status_command(ftp_file_name, 'Download failed')

    def download_dir(self, ftp_dir_name, status_command, replace_command):
        #Create local directory        
        try:
            if(not os.path.isdir(ftp_dir_name)):
                os.makedirs(ftp_dir_name)
                status_command(ftp_dir_name, 'Created local directory')
            else:
                status_command(ftp_dir_name, 'Local directory exists')
            os.chdir(ftp_dir_name)
        except Exception:
            status_command(ftp_dir_name, 'Failed to create local directory')
            return
        #Go into the ftp directory
        self.ftp.cwd(ftp_dir_name)
        #Get file lists
        detailed_file_list = self.get_detailed_file_list(True)
        file_list = self.get_file_list(detailed_file_list)
        for file_name, file_details in zip(file_list, detailed_file_list):
            #If directory
            if(self.is_dir(file_details)):
                self.download_dir(file_name, status_command, replace_command)
            #If file
            else:
                self.download_file(file_name, int(self.get_properties(file_details)[3]), status_command, replace_command)
        #Got to parent directory
        self.ftp.cwd('..')
        os.chdir('..')

    def search(self, dir_name, status_command, search_file_name):
        #Go into the ftp directory
        self.ftp.cwd(dir_name)
        #Get file lists
        detailed_file_list = self.get_detailed_file_list()
        file_list = self.get_file_list(detailed_file_list)
        for file_name, file_details in zip(file_list, detailed_file_list):
            #If file_name matches the keyword, append it to search list
            if search_file_name.lower() in file_name.lower():
                if(self.ftp.getcwd() == '/'):
                    dir = ''
                else:
                    dir = self.ftp.getcwd()
                self.search_file_list.append(dir+'/'+file_name)
                self.detailed_search_file_list.append(file_details)
                status_command(dir+'/'+file_name, 'Found')           
            #If directory, search it 
            if(self.is_dir(file_details)):
                status_command(file_name, 'Searching directory')
                self.search(file_name, status_command, search_file_name)
        #Goto to parent directory
        if(self.ftp.getcwd() != '/'):        
            self.ftp.cwd('..')

    def clear_search_list(self):
        del self.search_file_list[:]
        del self.detailed_search_file_list[:]

    def get_dir_size(self, dir_name):
        size = 0;
        #Go into the ftp directory
        self.ftp.cwd(dir_name)
        #Get file lists
        detailed_file_list = self.get_detailed_file_list()
        file_list = self.get_file_list(detailed_file_list)
        for file_name, file_details in zip(file_list, detailed_file_list):
            if(self.is_dir(file_details)):
                size+=self.get_dir_size(file_name)
            else:
                size+=int(self.get_properties(file_details)[3])
        #Goto to parent directory
        self.ftp.cwd('..')
        #return size
        return size

    def cwd_parent(self, name):
        if('/' not in name): return name
        parent_name = '/'.join(name.split('/')[:-1])
        if (parent_name == ''): parent_name = '/'
        self.ftp.cwd(parent_name)
        return ''.join(name.split('/')[-1:])

    def mkd(self, name):
        self.ftp.mkdir(name)

    def pwd(self):
        return(self.ftp.getcwd())

    def get_properties(self, file_details):
        details_list = file_details.split()
        #Get file attributes
        file_attribs = details_list[0]
        #Get date modified
        date_modified = ' '.join(details_list[5:8])
        #Remove the path from the name
        file_name = ' '.join(details_list[8:])
        #Get size if it is not a directory
        if('d' not in file_details[0]):
            file_size = details_list[4]
            return [file_name, file_attribs, date_modified, file_size]
        else:
            return [file_name, file_attribs, date_modified]

    def is_dir(self, file_details):
        return 'd' in file_details[0]

    def _download_dir_recursive(self, remote_path, local_path, status_command, replace_command):
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        
        self.ftp.cwd(remote_path)
        detailed_file_list = self.get_detailed_file_list(True)
        file_list = self.get_file_list(detailed_file_list)
        
        for file_name, file_details in zip(file_list, detailed_file_list):
            if self.is_dir(file_details):
                self._download_dir_recursive(file_name, os.path.join(local_path, file_name), status_command, replace_command)
            else:
                file_size = int(self.get_properties(file_details)[3])
                self.download_file(file_name, file_size, status_command, replace_command)
        
        if remote_path != '/':
            self.ftp.cwd('..')

    def _upload_dir_recursive(self, local_path, remote_path, status_command, replace_command):
        try:
            if not self.is_there(remote_path):
                self.ftp.mkdir(remote_path)
                status_command(remote_path, 'Creating directory')
            else:
                status_command(remote_path, 'Directory exists')
            self.ftp.cwd(remote_path)
        except Exception:
            status_command(remote_path, 'Failed to create directory')
            return
        
        for filename in os.listdir(local_path):
            local_file_path = os.path.join(local_path, filename)
            if os.path.isfile(local_file_path):
                self.upload_file(filename, os.path.getsize(local_file_path), status_command, replace_command)
            else:
                self._upload_dir_recursive(local_file_path, filename, status_command, replace_command)
        
        self.ftp.cwd('..')

    def disconnect(self):
        try:
            if hasattr(self, 'ftp') and self.ftp:
                self.ftp.close()
        except Exception:
            pass
        try:
            if hasattr(self, 'transport') and self.transport:
                self.transport.close()
        except Exception:
            pass