#!/usr/bin/env python3
#
#    zgSFTP - SSH Host Key Management
#
#    Provides SSH host key verification and storage
#

import os
import base64
import hashlib
from os.path import isfile, expanduser


def get_known_hosts_path():
    """Get path to known_hosts file."""
    home = expanduser('~')
    zgSFTP_dir = os.path.join(home, '.zgSFTP')
    if not os.path.exists(zgSFTP_dir):
        os.makedirs(zgSFTP_dir, mode=0o700)
    return os.path.join(zgSFTP_dir, 'known_hosts')


def get_host_key_id(host, port):
    """Generate unique identifier for host:port combination."""
    return f"{host}:{port}"


def hash_fingerprint(fingerprint):
    """Hash fingerprint for secure storage."""
    return hashlib.sha256(fingerprint.encode()).hexdigest()


def load_known_hosts():
    """Load known hosts from file.
    
    Returns:
        dict: {host_key_id: {'key_type': str, 'key': str, 'fingerprint': str}}
    """
    known_hosts = {}
    known_hosts_path = get_known_hosts_path()
    
    if not isfile(known_hosts_path):
        return known_hosts
    
    try:
        with open(known_hosts_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(':')
                if len(parts) >= 4:
                    host_key_id = parts[0]
                    key_type = parts[1]
                    key = parts[2]
                    fingerprint = parts[3]
                    
                    known_hosts[host_key_id] = {
                        'key_type': key_type,
                        'key': key,
                        'fingerprint': fingerprint
                    }
    except Exception:
        pass
    
    return known_hosts


def save_known_host(host, port, key_type, key, fingerprint):
    """Save a known host to file."""
    known_hosts_path = get_known_hosts_path()
    host_key_id = get_host_key_id(host, port)
    
    try:
        with open(known_hosts_path, 'a') as f:
            f.write(f"{host_key_id}:{key_type}:{key}:{hash_fingerprint(fingerprint)}\n")
        return True
    except Exception:
        return False


def remove_known_host(host, port):
    """Remove a known host from file."""
    known_hosts_path = get_known_hosts_path()
    host_key_id = get_host_key_id(host, port)
    
    if not isfile(known_hosts_path):
        return False
    
    try:
        lines = []
        with open(known_hosts_path, 'r') as f:
            for line in f:
                if not line.startswith(host_key_id + ':'):
                    lines.append(line)
        
        with open(known_hosts_path, 'w') as f:
            f.writelines(lines)
        return True
    except Exception:
        return False


def is_host_known(host, port, key):
    """Check if host is known and key matches.
    
    Args:
        host: SSH host
        port: SSH port
        key: paramiko.PKey object
    
    Returns:
        tuple: (is_known: bool, key_matches: bool, stored_fingerprint: str)
    """
    known_hosts = load_known_hosts()
    host_key_id = get_host_key_id(host, port)
    
    if host_key_id not in known_hosts:
        return (False, False, '')
    
    stored = known_hosts[host_key_id]
    
    try:
        current_fingerprint = key.get_fingerprint().hex()
        stored_fingerprint = stored['fingerprint']
        
        key_matches = hash_fingerprint(current_fingerprint) == stored_fingerprint
        
        return (True, key_matches, stored_fingerprint)
    except Exception:
        return (True, False, '')


def get_host_key_info(host, port):
    """Get stored host key information.
    
    Returns:
        dict or None: Host key info if found
    """
    known_hosts = load_known_hosts()
    host_key_id = get_host_key_id(host, port)
    
    return known_hosts.get(host_key_id)


def list_known_hosts():
    """List all known hosts.
    
    Returns:
        list: List of (host, port, key_type, fingerprint) tuples
    """
    known_hosts = load_known_hosts()
    result = []
    
    for host_key_id, info in known_hosts.items():
        parts = host_key_id.split(':')
        if len(parts) >= 2:
            host = parts[0]
            port = parts[1]
            result.append((host, port, info['key_type'], info['fingerprint']))
    
    return result


def clear_all_known_hosts():
    """Clear all known hosts."""
    known_hosts_path = get_known_hosts_path()
    
    if isfile(known_hosts_path):
        try:
            os.remove(known_hosts_path)
            return True
        except Exception:
            return False
    
    return True
