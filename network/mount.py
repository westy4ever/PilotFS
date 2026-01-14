import subprocess
import os
import time
import tempfile
import shlex
import socket
import threading
from ..constants import DEFAULT_CIFS_VERSION, DEFAULT_TIMEOUT
from ..exceptions import NetworkError, RemoteConnectionError
from ..utils.validators import validate_ip, validate_hostname, sanitize_string
import re

class MountManager:
    def __init__(self, config):
        self.config = config
        self.timeout = DEFAULT_TIMEOUT
        self.mount_points = {}
        self.ping_cache = {}
        self.scan_results = {}
    
    # ============================================================================
    # AJPanel-STYLE NETWORK FEATURES
    # ============================================================================
    
    def quick_ping(self, host, count=1, timeout=None):
        """AJPanel-style quick ping with caching"""
        try:
            if timeout is None:
                timeout = self.config.plugins.pilotfs.ping_timeout.value
            
            # Check cache first (5 minute cache)
            cache_key = f"{host}_{count}_{timeout}"
            if cache_key in self.ping_cache:
                cache_time, result = self.ping_cache[cache_key]
                if time.time() - cache_time < 300:  # 5 minutes
                    return result
            
            cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout + 2
            )
            
            is_reachable = result.returncode == 0
            
            # Parse latency if available
            latency = None
            if is_reachable and result.stdout:
                import re
                match = re.search(r'time=([\d.]+)\s*ms', result.stdout)
                if match:
                    latency = float(match.group(1))
            
            result_data = {
                'reachable': is_reachable,
                'latency': latency,
                'output': result.stdout[:200] + result.stderr[:200],
                'timestamp': time.time()
            }
            
            # Cache result
            self.ping_cache[cache_key] = (time.time(), result_data)
            
            return result_data
            
        except subprocess.TimeoutExpired:
            return {
                'reachable': False,
                'latency': None,
                'output': 'Ping timeout',
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'reachable': False,
                'latency': None,
                'output': str(e),
                'timestamp': time.time()
            }
    
    def check_port(self, host, port, timeout=None):
        """Check if a port is open"""
        try:
            if timeout is None:
                timeout = self.config.plugins.pilotfs.port_scan_timeout.value
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = time.time()
            result = sock.connect_ex((host, port))
            elapsed = (time.time() - start_time) * 1000
            
            sock.close()
            
            return {
                'open': result == 0,
                'response_time': elapsed,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'open': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def network_discovery_async(self, subnet=None, callback=None):
        """Asynchronous network discovery like AJPanel"""
        try:
            if subnet is None:
                subnet = self.config.plugins.pilotfs.network_scan_range.value
            
            base_ip = subnet.rstrip('.') + '.'
            active_hosts = []
            results = {}
            threads = []
            
            def scan_host(ip):
                try:
                    result = self.quick_ping(ip, count=1, timeout=1)
                    results[ip] = result
                    if result['reachable']:
                        active_hosts.append(ip)
                    
                    # Call callback if provided
                    if callback:
                        callback(ip, result)
                        
                except Exception:
                    results[ip] = {'reachable': False, 'error': 'Scan error'}
            
            # Create threads for scanning
            for i in range(1, 255):
                ip = f"{base_ip}{i}"
                thread = threading.Thread(target=scan_host, args=(ip,))
                thread.daemon = True
                threads.append(thread)
                thread.start()
            
            # Wait for completion with timeout
            for thread in threads:
                thread.join(timeout=0.1)
            
            # Store results
            self.scan_results[subnet] = {
                'active_hosts': active_hosts,
                'results': results,
                'timestamp': time.time(),
                'total_scanned': 254
            }
            
            return active_hosts
            
        except Exception as e:
            return []
    
    def get_network_interfaces(self):
        """Get network interface information"""
        try:
            result = subprocess.run(
                ["ifconfig"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            interfaces = []
            current_interface = None
            
            for line in result.stdout.split('\n'):
                if line and not line.startswith(' '):
                    # New interface
                    if current_interface:
                        interfaces.append(current_interface)
                    
                    interface_name = line.split(':')[0]
                    current_interface = {
                        'name': interface_name,
                        'lines': [line.strip()]
                    }
                elif current_interface:
                    current_interface['lines'].append(line.strip())
            
            if current_interface:
                interfaces.append(current_interface)
            
            return interfaces
            
        except Exception as e:
            return []
    
    def get_dns_info(self):
        """Get DNS configuration information"""
        try:
            dns_info = {}
            
            # Read /etc/resolv.conf
            if os.path.exists("/etc/resolv.conf"):
                with open("/etc/resolv.conf", "r") as f:
                    dns_info['resolv_conf'] = f.read()
            
            # Try to get DNS servers via nslookup
            try:
                result = subprocess.run(
                    ["nslookup", "google.com"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                dns_info['nslookup'] = result.stdout
            except:
                dns_info['nslookup'] = "nslookup not available"
            
            return dns_info
            
        except Exception as e:
            return {'error': str(e)}
    
    def run_network_command(self, command, timeout=10):
        """Run a network diagnostic command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'command': command
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out',
                'command': command
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
    
    # ============================================================================
    # ORIGINAL MOUNT METHODS (Enhanced with network checks)
    # ============================================================================
    
    def mount_cifs(self, server, share, mount_point, username="", password="", domain="", options=None):
        """Mount CIFS/SMB share with pre-flight network check"""
        # First check if server is reachable
        if self.config.plugins.pilotfs.connection_check.value:
            ping_result = self.quick_ping(server)
            if not ping_result['reachable']:
                return False, f"Server unreachable: {server}. Please check network connection."
        
        creds_file = None
        try:
            # Validate inputs
            if not validate_ip(server) and not validate_hostname(server):
                return False, f"Invalid server address: {server}"
            
            # SECURITY FIX: Validate share name
            if not re.match(r'^[a-zA-Z0-9_\-.$]+$', share):
                return False, f"Invalid share name: {share}"
            
            # Validate mount point
            if not os.path.isabs(mount_point):
                return False, "Mount point must be absolute path"
            
            # Create mount point if it doesn't exist
            if not os.path.exists(mount_point):
                os.makedirs(mount_point, exist_ok=True)
            
            # Unmount first if already mounted
            self.umount(mount_point, force=True)
            
            # Build mount options
            mount_options = []
            
            # SECURITY FIX: Use credentials file instead of command line
            if username:
                creds_fd, creds_file = tempfile.mkstemp(prefix='pilotfs_', suffix='.creds', dir='/tmp')
                try:
                    with os.fdopen(creds_fd, 'w') as f:
                        f.write(f"username={username}\n")
                        if password:
                            f.write(f"password={password}\n")
                        if domain:
                            f.write(f"domain={domain}\n")
                    # Secure permissions (owner read/write only)
                    os.chmod(creds_file, 0o600)
                    mount_options.append(f"credentials={creds_file}")
                except Exception:
                    if creds_file and os.path.exists(creds_file):
                        os.unlink(creds_file)
                    raise
            else:
                mount_options.append("guest")
            
            mount_options.append(f"vers={DEFAULT_CIFS_VERSION}")
            mount_options.append("rw")
            mount_options.append("iocharset=utf8")
            
            # Add custom options
            if options:
                if isinstance(options, list):
                    mount_options.extend(options)
                elif isinstance(options, str):
                    mount_options.append(options)
            
            # Build mount command with proper quoting
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
            
            # Clean up credentials file
            if creds_file and os.path.exists(creds_file):
                os.unlink(creds_file)
                creds_file = None
            
            if result.returncode == 0:
                self.mount_points[mount_point] = {
                    'type': 'cifs',
                    'server': server,
                    'share': share,
                    'options': mount_options,
                    'mounted_at': time.time()
                }
                return True, f"Mounted //{server}/{share} to {mount_point}"
            else:
                error = result.stderr.strip() or result.stdout.strip()
                
                # Try different CIFS versions
                for version in ["2.0", "1.0"]:
                    # Recreate credentials file if needed
                    if username:
                        creds_fd, creds_file = tempfile.mkstemp(prefix='pilotfs_', suffix='.creds', dir='/tmp')
                        with os.fdopen(creds_fd, 'w') as f:
                            f.write(f"username={username}\n")
                            if password:
                                f.write(f"password={password}\n")
                            if domain:
                                f.write(f"domain={domain}\n")
                        os.chmod(creds_file, 0o600)
                    
                    # Update version in options
                    new_options = [opt if not opt.startswith('vers=') else f'vers={version}' for opt in mount_options]
                    mount_cmd = [
                        "mount", "-t", "cifs",
                        f"//{server}/{share}",
                        mount_point,
                        "-o", ",".join(new_options)
                    ]
                    
                    result = subprocess.run(
                        mount_cmd,
                        capture_output=True,
                        timeout=self.timeout,
                        text=True
                    )
                    
                    # Clean up credentials file
                    if creds_file and os.path.exists(creds_file):
                        os.unlink(creds_file)
                        creds_file = None
                    
                    if result.returncode == 0:
                        self.mount_points[mount_point] = {
                            'type': 'cifs',
                            'server': server,
                            'share': share,
                            'options': new_options,
                            'mounted_at': time.time()
                        }
                        return True, f"Mounted with vers={version}"
                
                return False, f"Mount failed: {error[:200]}"
                
        except subprocess.TimeoutExpired:
            if creds_file and os.path.exists(creds_file):
                os.unlink(creds_file)
            return False, "Mount operation timed out"
        except Exception as e:
            if creds_file and os.path.exists(creds_file):
                os.unlink(creds_file)
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
                return False, "Invalid server address: %s" % server
            
            # First test if server is reachable with enhanced ping
            ping_result = self.quick_ping(server)
            if not ping_result['reachable']:
                return False, f"Server unreachable: {server}. Ping output: {ping_result.get('output', 'No output')}"
            
            # Check if smbclient is available
            smb_check = subprocess.run(
                ["which", "smbclient"],
                capture_output=True,
                timeout=5
            )
            if smb_check.returncode != 0:
                return False, "smbclient not installed. Install: opkg install samba-client"
            
            # Try anonymous listing first
            result = subprocess.run(
                ["smbclient", "-L", server, "-N", "-g"],
                capture_output=True,
                timeout=15,
                text=True
            )
            
            if result.returncode != 0:
                # Try with guest
                result = subprocess.run(
                    ["smbclient", "-L", server, "-U", "guest%", "-g"],
                    capture_output=True,
                    timeout=15,
                    text=True
                )
            
            if result.returncode == 0:
                shares = []
                lines = result.stdout.split("\n")
                
                for line in lines:
                    if '|Disk|' in line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            share_name = parts[1]
                            if share_name and not share_name.endswith('$'):
                                shares.append({
                                    'name': share_name,
                                    'type': 'Disk',
                                    'description': parts[2] if len(parts) > 2 else ''
                                })
                
                if shares:
                    return True, shares
                else:
                    return False, "No shares found on %s. Server may require authentication." % server
            else:
                error = result.stderr[:200] if result.stderr else "Connection refused"
                return False, "Scan failed: %s. Try: Check IP, firewall, SMB enabled on server." % error
                
        except subprocess.TimeoutExpired:
            return False, "Scan timed out. Server may be slow or unreachable."
        except Exception as e:
            return False, "Scan error: %s" % str(e)
    
    def test_ping(self, host):
        """Ping host to test connectivity"""
        try:
            if not validate_ip(host) and not validate_hostname(host):
                return False, f"Invalid host: {host}"
            
            result = self.quick_ping(host)
            
            if result['reachable']:
                latency_msg = f" (latency: {result['latency']}ms)" if result['latency'] else ""
                return True, f"Host reachable{latency_msg}"
            else:
                return False, f"Host unreachable: {result.get('output', 'No output')}"
                
        except Exception as e:
            return False, f"Ping error: {e}"
    
    def get_available_mount_points(self):
        """Get list of available mount points"""
        mount_points = []
        
        common_locations = [
            "/media/net", "/media/usb", "/media/usb1", "/media/usb2",
            "/media/hdd", "/media/mmc", "/media/sdcard", "/tmp/mnt"
        ]
        
        for location in common_locations:
            if os.path.isdir(location):
                mount_points.append(location)
                try:
                    for item in os.listdir(location):
                        item_path = os.path.join(location, item)
                        if os.path.isdir(item_path):
                            mount_points.append(item_path)
                except:
                    pass
        
        if os.path.isdir("/mnt"):
            mount_points.append("/mnt")
            try:
                for item in os.listdir("/mnt"):
                    item_path = os.path.join("/mnt", item)
                    if os.path.isdir(item_path):
                        mount_points.append(item_path)
            except:
                pass
        
        return list(set(mount_points))
    
    def cleanup_mounts(self):
        """Cleanup stale mounts"""
        try:
            success, mounts = self.list_mounts()
            if not success:
                return False, "Failed to list mounts"
            
            cleaned = 0
            for mount in mounts:
                if "//" in mount or ":" in mount:
                    parts = mount.split()
                    if len(parts) >= 3:
                        mount_point = parts[2]
                        try:
                            os.listdir(mount_point)
                        except:
                            self.umount(mount_point, force=True, lazy=True)
                            cleaned += 1
            
            return True, f"Cleaned {cleaned} stale mounts"
            
        except Exception as e:
            return False, f"Cleanup mounts error: {e}"
    
    def get_network_stats(self):
        """Get network statistics"""
        stats = {
            'ping_cache_size': len(self.ping_cache),
            'scan_results': len(self.scan_results),
            'mount_points': len(self.mount_points),
            'timestamp': time.time()
        }
        
        # Get some recent ping results
        recent_pings = []
        for host, result in list(self.ping_cache.values())[-5:]:
            if isinstance(result, tuple):  # Handle cached tuples
                result = result[1]
            recent_pings.append({
                'host': host.split('_')[0],  # Extract host from cache key
                'reachable': result.get('reachable', False),
                'latency': result.get('latency'),
                'age': int(time.time() - result.get('timestamp', 0))
            })
        
        stats['recent_pings'] = recent_pings
        return stats