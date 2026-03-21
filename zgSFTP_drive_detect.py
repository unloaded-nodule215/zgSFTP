import platform
import os
if(platform.system() == 'Windows'):
    import win32api
    import win32con

#Function to get all removable mountpoints attached to the computer
def get_mounts():
    mountpoints = []    

    if(platform.system() == 'Linux'):
        dev_types = ['/dev/sda', '/dev/sdc', '/dev/sdb', '/dev/hda', '/dev/hdc', '/dev/hdb', '/dev/nvme']

        try:
            with open('/proc/mounts') as f:
                for line in f:
                    details = line.split()
                    if len(details) >= 2 and details[0][:-1] in dev_types:
                        if details[1] != '/boot/efi':
                            try:
                                details_decoded_string = bytes(details[1], "utf-8").decode("unicode_escape")
                                mountpoints.append(details_decoded_string)
                            except Exception:
                                pass
        except Exception:
            pass
    elif(platform.system() == 'Darwin'):
        for mountpoint in os.listdir('/Volumes/'):
            mountpoints.append('/Volumes/' + mountpoint)

    elif(platform.system() == 'Windows'):
        mountpoints = win32api.GetLogicalDriveStrings()
        mountpoints = mountpoints.split('\000')[:-1]

    return mountpoints