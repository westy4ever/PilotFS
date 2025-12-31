import subprocess
import os
import time
from ..constants import DEFAULT_CIFS_VERSION, DEFAULT_TIMEOUT
from ..exceptions import NetworkError, RemoteConnectionError
from ..utils.validators import validate_ip, validate_hostname, sanitize_string

class MountManager:
    def __init__(self, config):
        self.config = config
        self.timeout = DEFAULT_TIMEOUT
        self.mount_points = {}
    
    def mount_cifs(self, server, share, mount_point, username="", password="", domain="", options=None):
        """Mount CIFS/SMB share"""
        try:
            # Validate inputs
            if not validate_ip(server) and not validate_hostname(server):
                return False, f"Invalid server address: {server}"
            
            sanitize_string(share)
            sanitize_string(mount_point)
            
            # Create mount point if it doesn't exist
            if not os.path.exists(mount_point):
                os.makedirs(mount_point, exist_ok=True)
            
            # Unmount first if already mounted
            self.umount(mount_point, force=True)
            
            # Build mount options
            mount_options = []
            
            if username:
                mount_options.append(f"user={username}")
                if password:
                    mount_options.append(f"password={password}")
            else:
                mount_options.append("guest")
            
            if domain:
                mount_options.append(f"domain={domain}")
            
            mount_options.append(f"vers={DEFAULT_CIFS_VERSION}")
            mount_options.append("rw")
            mount_options.append("iocharset=utf8")
            
            # Add custom options
            if options:
                if isinstance(options, list):
                    mount_options.extend(options)
                elif isinstance(options, str):
                    mount_options.append(options)
            
            # Build mount command
            mount_cmd = [
                "mount", "-t", "cifs",
                f"//{server}/{share}",
                mount_point,
                "-o", ",".join(mount_options)
            ]
            
            result = subprocess.run(
                mount_cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            if result.returncode == 0:
                self.mount_points[mount_point] = {
                    'type': 'cifs',
                    'server': server,
                    'share': share,
                    'options': mount_options
                }
                return True, f"Mounted //{server}/{share} to {mount_point}"
            else:
                error = result.stderr.strip() or result.stdout.strip()
                
                # Try different CIFS versions
                for version in ["2.0", "1.0"]:
                    mount_options[-1] = f"vers={version}"  # Replace last option
                    mount_cmd[-1] = ",".join(mount_options)
                    
                    result = subprocess.run(
                        mount_cmd,
                        capture_output=True,
                        timeout=self.timeout,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        self.mount_points[mount_point] = {
                            'type': 'cifs',
                            'server': server,
                            'share': share,
                            'options': mount_options
                        }
                        return True, f"Mounted with vers={version}"
                
                return False, f"Mount failed: {error[:200]}"
                
        except subprocess.TimeoutExpired:
            return False, "Mount operation timed out"
        except Exception as e:
            return False, f"Mount error: {e}"
    
    def umount(self, mount_point, force=False, lazy=False):
        """Unmount filesystem"""
        try:
            sanitize_string(mount_point)
            
            if not os.path.ismount(mount_point):
                return True, f"{mount_point} is not mounted"
            
            # Build umount command
            umount_cmd = ["umount"]
            
            if force:
                umount_cmd.append("-f")
            if lazy:
                umount_cmd.append("-l")
            
            umount_cmd.append(mount_point)
            
            result = subprocess.run(
                umount_cmd,
                capture_output=True,
                timeout=self.timeout,
                text=True
            )
            
            if result.returncode == 0:
                if mount_point in self.mount_points:
                    del self.mount_points[mount_point]
                return True, f"Unmounted {mount_point}"
            else:
                error = result.stderr.strip() or result.stdout.strip()
                return False, f"Unmount failed: {error[:200]}"
                
        except Exception as e:
            return False, f"Unmount error: {e}"
    
    def list_mounts(self):
        """List all mounts"""
        try:
            result = subprocess.run(
                ["mount"],
                capture_output=True,
                timeout=5,
                text=True
            )
            
            if result.returncode == 0:
                mounts = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        mounts.append(line)
                return True, mounts
            else:
                return False, "Failed to list mounts"
                
        except Exception as e:
            return False, f"List mounts error: {e}"
    
    def is_mounted(self, mount_point):
        """Check if path is mounted"""
        try:
            return os.path.ismount(mount_point)
        except:
            return False
    
    def get_mount_info(self, mount_point):
        """Get information about mount"""
        try:
            result = subprocess.run(
                ["findmnt", "-o", "SOURCE,TARGET,FSTYPE,OPTIONS", mount_point],
                capture_output=True,
                timeout=5,
                text=True
            )
            
            if result.returncode == 0 and "TARGET" not in result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        return {
                            'source': parts[0],
                            'target': parts[1],
                            'fstype': parts[2],
                            'options': parts[3] if len(parts) > 3 else ""
                        }
            
            # Fallback to mount command
            success, mounts = self.list_mounts()
            if success:
                for mount in mounts:
                    if mount_point in mount:
                        return {'raw': mount}
            
            return None
            
        except:
            return None
    
    def scan_network_shares(self, server):
        """Scan for available shares on server"""
        try:
            if not validate_ip(server) and not validate_hostname(server):
                return False, f"Invalid server address: {server}"
            
            # Check if smbclient is available
            smb_check = subprocess.run(
                ["which", "smbclient"],
                capture_output=True,
                timeout=5
            )
            if smb_check.returncode != 0:
                return False, "smbclient not installed. Install with: opkg install samba-client"
            
            # Scan for shares
            result = subprocess.run(
                ["smbclient", "-L", server, "-N"],
                capture_output=True,
                timeout=15,
                text=True
            )
            
            if result.returncode == 0:
                shares = []
                lines = result.stdout.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if line and "Disk" in line:
                        # Parse share line
                        parts = line.split()
                        if parts:
                            share_name = parts[0]
                            if share_name and not share_name.startswith('--'):
                                shares.append({
                                    'name': share_name,
                                    'type': 'Disk',
                                    'description': ' '.join(parts[1:]) if len(parts) > 1 else ""
                                })
                    elif line and "Printer" in line:
                        parts = line.split()
                        if parts:
                            share_name = parts[0]
                            if share_name and not share_name.startswith('--'):
                                shares.append({
                                    'name': share_name,
                                    'type': 'Printer',
                                    'description': ' '.join(parts[1:]) if len(parts) > 1 else ""
                                })
                
                return True, shares
            else:
                error = result.stderr[:200] if result.stderr else result.stdout[:200]
                return False, f"Scan failed: {error}"
                
        except subprocess.TimeoutExpired:
            return False, "Scan timed out"
        except Exception as e:
            return False, f"Scan error: {e}"
    
    def test_ping(self, host):
        """Ping host to test connectivity"""
        try:
            if not validate_ip(host) and not validate_hostname(host):
                return False, f"Invalid host: {host}"
            
            result = subprocess.run(
                ["ping", "-c", "2", "-W", "2", host],
                capture_output=True,
                timeout=5,
                text=True
            )
            
            if result.returncode == 0:
                return True, "Ping successful"
            else:
                return False, "Host unreachable"
                
        except subprocess.TimeoutExpired:
            return False, "Ping timeout"
        except Exception as e:
            return False, f"Ping error: {e}"
    
    def get_available_mount_points(self):
        """Get list of available mount points"""
        mount_points = []
        
        # Common mount locations
        common_locations = [
            "/media/net",
            "/media/usb",
            "/media/usb1",
            "/media/usb2",
            "/media/hdd",
            "/media/mmc",
            "/media/sdcard",
            "/tmp/mnt"
        ]
        
        for location in common_locations:
            if os.path.isdir(location):
                mount_points.append(location)
                
                # Check for subdirectories
                try:
                    for item in os.listdir(location):
                        item_path = os.path.join(location, item)
                        if os.path.isdir(item_path):
                            mount_points.append(item_path)
                except:
                    pass
        
        # Also check /mnt
        if os.path.isdir("/mnt"):
            mount_points.append("/mnt")
            try:
                for item in os.listdir("/mnt"):
                    item_path = os.path.join("/mnt", item)
                    if os.path.isdir(item_path):
                        mount_points.append(item_path)
            except:
                pass
        
        return list(set(mount_points))  # Remove duplicates
    
    def cleanup_mounts(self):
        """Cleanup stale mounts"""
        try:
            success, mounts = self.list_mounts()
            if not success:
                return False, "Failed to list mounts"
            
            cleaned = 0
            for mount in mounts:
                if "//" in mount or ":" in mount:  # Network mount
                    parts = mount.split()
                    if len(parts) >= 3:
                        mount_point = parts[2]
                        
                        # Try to unmount if not accessible
                        try:
                            os.listdir(mount_point)
                        except:
                            # Mount appears broken, try to unmount
                            self.umount(mount_point, force=True, lazy=True)
                            cleaned += 1
            
            return True, f"Cleaned {cleaned} stale mounts"
            
        except Exception as e:
            return False, f"Cleanup mounts error: {e}"