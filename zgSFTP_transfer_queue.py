#!/usr/bin/env python3
#
#    zgSFTP - Transfer Queue Module
#
#    Provides persistent file transfer queue management
#

import os
import configparser
import threading
from os.path import isfile, join, abspath, dirname

MAX_QUEUE_SIZE = 10000


def escape_config_value(value):
    """Escape special characters for configparser values."""
    if value is None:
        return ''
    return value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def unescape_config_value(value):
    """Unescape special characters from configparser values."""
    if value is None:
        return ''
    value = value.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
    return value


class TransferQueue:
    """
    Persistent file transfer queue with retry handling.
    
    Queue file format (queue.ini):
    [Queue]
    pending_count = 3
    completed_count = 5
    failed_count = 2
    failed_retry_available = True
    failed_retry_attempted = False
    
    [PendingFile_0]
    path = /path/to/file1.txt
    type = file
    priority = 1
    
    [PendingFile_1]
    path = /path/to/file2.txt
    type = folder
    priority = 1
    
    [FailedFile_0]
    path = /path/to/file3.txt
    type = file
    retry_available = True
    retry_count = 0
    """
    
    def __init__(self, queue_file=None):
        """Initialize transfer queue with file persistence."""
        # Use script directory for queue file, not current working directory
        if queue_file is None:
            # Get the directory where the script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.queue_file = os.path.join(script_dir, 'queue.ini')
        else:
            self.queue_file = queue_file
        self.lock = threading.Lock()
        self._queue_items = []
        self._failed_items = []
        self._stats = {
            'pending': 0,
            'completed': 0,
            'failed': 0
        }
        self._retry_available = True
        self._retry_attempted = False
        
    def load_from_file(self):
        """Load queue state from disk."""
        if not isfile(self.queue_file):
            return
        
        try:
            config = configparser.ConfigParser()
            config.read(self.queue_file)
            
            # Load stats
            if 'Queue' in config:
                self._stats['pending'] = int(config['Queue'].get('pending_count', 0))
                self._stats['completed'] = int(config['Queue'].get('completed_count', 0))
                self._stats['failed'] = int(config['Queue'].get('failed_count', 0))
                self._retry_available = config['Queue'].getboolean('failed_retry_available', True)
                self._retry_attempted = config['Queue'].getboolean('failed_retry_attempted', False)
            
            # Load pending files
            self._queue_items = []
            for i in range(self._stats['pending']):
                item = self._load_queue_item(config, f'PendingFile_{i}')
                if item:
                    self._queue_items.append(item)
            
            # Load failed files
            self._failed_items = []
            for i in range(self._stats['failed']):
                item = self._load_failed_item(config, f'FailedFile_{i}')
                if item:
                    self._failed_items.append(item)
                    
        except Exception:
            # If load fails, start fresh
            self._queue_items = []
            self._failed_items = []
            self._stats = {'pending': 0, 'completed': 0, 'failed': 0}
            self._retry_available = True
            self._retry_attempted = False
            
    def _load_queue_item(self, config, section):
        """Load a single queue item."""
        try:
            if section not in config:
                return None
            
            item = {
                'id': section,
                'path': config[section].get('path', ''),
                'type': config[section].get('type', 'file'),
                'priority': int(config[section].get('priority', 1))
            }
            return item
        except Exception:
            return None
            
    def _load_failed_item(self, config, section):
        """Load a single failed item."""
        try:
            if section not in config:
                return None
            
            item = {
                'id': section,
                'path': config[section].get('path', ''),
                'type': config[section].get('type', 'file'),
                'retry_available': config[section].getboolean('retry_available', True),
                'retry_count': int(config[section].get('retry_count', 0))
            }
            return item
        except Exception:
            return None
            
    def save_to_file(self):
        """Save queue state to disk."""
        try:
            config = configparser.ConfigParser()
            
            # Save queue stats
            config['Queue'] = {
                'pending_count': str(len(self._queue_items)),
                'completed_count': str(self._stats['completed']),
                'failed_count': str(len(self._failed_items)),
                'failed_retry_available': 'True' if self._retry_available else 'False',
                'failed_retry_attempted': 'True' if self._retry_attempted else 'False'
            }
            
            # Save pending files
            for i, item in enumerate(self._queue_items):
                config[f'PendingFile_{i}'] = {
                    'path': escape_config_value(item['path']),
                    'type': item['type'],
                    'priority': str(item['priority'])
                }
            
            # Save failed files
            for i, item in enumerate(self._failed_items):
                config[f'FailedFile_{i}'] = {
                    'path': escape_config_value(item['path']),
                    'type': item['type'],
                    'retry_available': 'True' if item['retry_available'] else 'False',
                    'retry_count': str(item['retry_count'])
                }
            
            # Write to file
            with open(self.queue_file, 'w') as f:
                config.write(f)
                
        except Exception:
            # Log error but don't fail transfer
            pass
            
    def enqueue(self, path, file_type='file'):
        """Add a file/folder to the queue."""
        with self.lock:
            # Check queue size limit
            if len(self._queue_items) >= MAX_QUEUE_SIZE:
                return False
            
            # Validate path
            if not self._validate_path(path):
                return False
            
            item = {
                'id': f'PendingFile_{len(self._queue_items)}',
                'path': path,
                'type': file_type,
                'priority': 1
            }
            
            self._queue_items.append(item)
            self._stats['pending'] = len(self._queue_items)
            
            # Save to disk
            self.save_to_file()
            return True
            
    def enqueue_to_front(self, path, file_type='file'):
        """Add a file/folder to the front of the queue."""
        with self.lock:
            # Check queue size limit
            if len(self._queue_items) >= MAX_QUEUE_SIZE:
                return False
            
            # Validate path
            if not self._validate_path(path):
                return False
            
            item = {
                'id': f'PendingFile_{len(self._queue_items)}',
                'path': path,
                'type': file_type,
                'priority': 1
            }
            
            # Insert at the beginning
            self._queue_items.insert(0, item)
            self._stats['pending'] = len(self._queue_items)
            
            # Save to disk
            self.save_to_file()
            return True
            
    def dequeue(self):
        """Remove and return next item from queue."""
        with self.lock:
            if not self._queue_items:
                return None
            
            # Get next item (sorted by type then path alphabetically)
            # Folders first, then files, both alphabetically by path
            self._queue_items.sort(key=lambda x: (0 if x['type'] == 'folder' else 1, x['path']))
            item = self._queue_items.pop(0)
            
            # Update stats
            self._stats['pending'] = len(self._queue_items)
            
            # Save to disk
            self.save_to_file()
            return item
            
    def add_failed_file(self, path, file_type='file'):
        """Add a failed file to the retry queue."""
        with self.lock:
            # Check if retry already attempted
            if self._retry_attempted:
                return None  # Can't add more failed files after retry
            
            # Check if already in failed queue
            for item in self._failed_items:
                if item['path'] == path:
                    # Update retry count
                    item['retry_count'] += 1
                    return item
                    
            item = {
                'id': f'FailedFile_{len(self._failed_items)}',
                'path': path,
                'type': file_type,
                'retry_available': True,
                'retry_count': 1
            }
            
            self._failed_items.append(item)
            self._stats['failed'] = len(self._failed_items)
            
            # Save to disk
            self.save_to_file()
            return item
            
    def retry_failed_files(self):
        """Mark failed files for retry and move to pending queue."""
        with self.lock:
            if not self._failed_items:
                return False
                
            if not self._retry_available:
                return False
            
            # Mark retry as attempted
            self._retry_available = False
            self._retry_attempted = True
            
            # Move failed files to pending (add to end)
            for failed_item in self._failed_items:
                if failed_item['retry_available']:
                    # Remove from failed
                    self._failed_items.remove(failed_item)
                    # Add to pending
                    failed_item['id'] = f'PendingFile_{len(self._queue_items)}'
                    self._queue_items.append(failed_item)
                    self._stats['failed'] -= 1
                    self._stats['pending'] += 1
            
            # Save to disk
            self.save_to_file()
            return True
            
    def clear_pending(self):
        """Clear all pending items from queue."""
        with self.lock:
            self._queue_items = []
            self._stats['pending'] = 0
            self.save_to_file()
            return True
            
    def increment_completed(self):
        """Increment completed counter."""
        with self.lock:
            self._stats['completed'] += 1
            self.save_to_file()
            
    def get_stats(self):
        """Get current queue statistics."""
        with self.lock:
            return self._stats.copy()
            
    def is_complete(self):
        """Check if queue is complete."""
        with self.lock:
            return len(self._queue_items) == 0 and len(self._failed_items) == 0
            
    def get_queue_items(self):
        """Get all pending queue items."""
        with self.lock:
            return self._queue_items.copy()
            
    def get_failed_items(self):
        """Get all failed queue items."""
        with self.lock:
            return self._failed_items.copy()
            
    def validate_queue_item(self, item):
        """Validate a queue item path exists and is accessible."""
        path = item['path']
        
        # Check if path exists
        if not isfile(path) and not os.path.isdir(path):
            return False, f"Path does not exist: {path}"
            
        # Check if path is accessible
        try:
            if os.path.isdir(path):
                os.listdir(path)
            else:
                open(path, 'r').close()
        except Exception as e:
            return False, f"Cannot access path: {e}"
            
        return True, None
        
    def _validate_path(self, path):
        """Validate a path can be used in queue."""
        # Path cannot be empty
        if not path:
            return False
        
        # Allow both absolute and relative paths
        # Normalize path to prevent traversal
        normalized = os.path.normpath(path)
        
        # Check for path traversal attempts
        if normalized.startswith('..'):
            return False
        
        return True
        
    def get_total_files(self):
        """Get total number of files to transfer."""
        with self.lock:
            return len(self._queue_items) + len(self._failed_items)
            
    def get_pending_count(self):
        """Get number of pending files."""
        with self.lock:
            return self._stats['pending']
            
    def get_failed_count(self):
        """Get number of failed files."""
        with self.lock:
            return self._stats['failed']
            
    def get_completed_count(self):
        """Get number of completed files."""
        with self.lock:
            return self._stats['completed']
            
    def reset(self):
        """Reset queue (remove queue.ini file)."""
        if isfile(self.queue_file):
            os.remove(self.queue_file)
        self._queue_items = []
        self._failed_items = []
        self._stats = {'pending': 0, 'completed': 0, 'failed': 0}
        self._retry_available = True
        self._retry_attempted = False
