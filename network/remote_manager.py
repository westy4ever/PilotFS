import json
import os
import socket
import subprocess
import threading
import time
from datetime import datetime
from ..constants import REMOTE_CONNECTIONS_FILE
from ..exceptions import RemoteConnectionError, NetworkError
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class RemoteConnectionManager:
    def __init__(self, config):
        self.config = config
        self.connections_file = REMOTE_CONNECTIONS_FILE
        self.connections = self.load_connections()
        self.active_connections = {}
        self.ping_results = {}
        self.port_scan_results = {}
        self.network_log = []
    
    def load_connections(self):
        """Load saved remote connections"""
        try:
            if os.path.exists(self.connections_file):
                with open(self.connections_file, 'r') as f:
                    connections = json.load(f)
                    # Validate connections structure
                    valid_connections = {}
                    for name, conn in connections.items():
                        if self._validate_connection(conn):
                            valid_connections[name] = conn
                    return valid_connections
        except Exception:
            pass
        return {}
    
    def save_connections(self):
        """Save remote connections"""
        try:
            with open(self.connections_file, 'w') as f:
                json.dump(self.connections, f, indent=2)
            return True
        except Exception as e:
            raise RemoteConnectionError(f"Failed to save connections: {e}")
    
    def add_connection(self, name, connection_type, host, port, username, password, path="/", options=None):
        """Add a new remote connection"""
        try:
            connection = {
                'type': connection_type,
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'path': path,
                'options': options or {},
                'last_used': datetime.now().isoformat(),
                'created': datetime.now().isoformat(),
                'status': 'unknown',
                'last_check': None,
                'latency': None
            }
            
            if not self._validate_connection(connection):
                raise RemoteConnectionError("Invalid connection parameters")
            
            self.connections[name] = connection
            self.save_connections()
            return True
            
        except Exception as e:
            raise RemoteConnectionError(f"Failed to add connection: {e}")
    
    def update_connection(self, name, **kwargs):
        """Update existing connection"""
        try:
            if name not in self.connections:
                raise RemoteConnectionError(f"Connection not found: {name}")
            
            connection = self.connections[name]
            connection.update(kwargs)
            connection['last_used'] = datetime.now().isoformat()
            
            if not self._validate_connection(connection):
                raise RemoteConnectionError("Invalid connection parameters after update")
            
            self.connections[name] = connection
            self.save_connections()
            return True
            
        except Exception as e:
            raise RemoteConnectionError(f"Failed to update connection: {e}")
    
    def remove_connection(self, name):
        """Remove a remote connection"""
        try:
            if name in self.connections:
                del self.connections[name]
                self.save_connections()
                return True
            return False
        except Exception as e:
            raise RemoteConnectionError(f"Failed to remove connection: {e}")
    
    def get_connection(self, name):
        """Get connection by name"""
        return self.connections.get(name)
    
    def list_connections(self, connection_type=None):
        """List all connections, optionally filtered by type"""
        if connection_type:
            return {k: v for k, v in self.connections.items() if v.get('type') == connection_type}
        return self.connections.copy()
    
    # ============================================================================
    # AJPanel-STYLE NETWORK DIAGNOSTICS
    # ============================================================================
    
    def check_host_status(self, host, timeout=None):
        """AJPanel-style quick ping check with timeout"""
        try:
            if timeout is None:
                timeout = self.config.plugins.pilotfs.ping_timeout.value
            
            # Use ping with count=1 and custom timeout
            cmd = ["ping", "-c", "1", "-W", str(timeout), host]
            
            # Log the command
            self._add_to_network_log(f"PING {host} (timeout: {timeout}s)")
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            is_reachable = result.returncode == 0
            
            # Parse ping time if available
            latency = None
            if is_reachable and result.stdout:
                # Extract time from ping output (time=12.3 ms)
                import re
                match = re.search(r'time=([\d.]+)\s*ms', result.stdout)
                if match:
                    latency = float(match.group(1))
            
            self.ping_results[host] = {
                'reachable': is_reachable,
                'latency': latency,
                'timestamp': time.time(),
                'output': result.stdout[:500] + result.stderr[:500]
            }
            
            return is_reachable, latency
            
        except Exception as e:
            logger.error(f"Ping error for {host}: {e}")
            self._add_to_network_log(f"PING ERROR {host}: {str(e)}")
            return False, None
    
    def port_scan(self, host, ports=None, timeout=None):
        """Scan for open ports on a host"""
        try:
            if ports is None:
                # Common service ports
                ports = [21, 22, 80, 443, 139, 445, 8080, 9090]
            
            if timeout is None:
                timeout = self.config.plugins.pilotfs.port_scan_timeout.value
            
            open_ports = []
            results = {}
            
            self._add_to_network_log(f"PORT SCAN {host} (ports: {ports})")
            
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    
                    start_time = time.time()
                    result = sock.connect_ex((host, port))
                    elapsed = (time.time() - start_time) * 1000  # ms
                    
                    is_open = result == 0
                    status = "OPEN" if is_open else "CLOSED"
                    
                    results[port] = {
                        'open': is_open,
                        'response_time': elapsed,
                        'status': status
                    }
                    
                    if is_open:
                        open_ports.append(port)
                        # Try to identify service
                        service = self._identify_service(port)
                        results[port]['service'] = service
                    
                    sock.close()
                    
                except Exception as e:
                    results[port] = {
                        'open': False,
                        'error': str(e),
                        'status': 'ERROR'
                    }
            
            self.port_scan_results[host] = {
                'open_ports': open_ports,
                'results': results,
                'timestamp': time.time()
            }
            
            return open_ports, results
            
        except Exception as e:
            logger.error(f"Port scan error for {host}: {e}")
            self._add_to_network_log(f"PORT SCAN ERROR {host}: {str(e)}")
            return [], {}
    
    def _identify_service(self, port):
        """Identify common service by port number"""
        common_services = {
            21: "FTP",
            22: "SSH/SFTP",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            139: "NetBIOS",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB/CIFS",
            993: "IMAPS",
            995: "POP3S",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            8080: "HTTP-Proxy",
            9090: "Enigma2 WebIf"
        }
        return common_services.get(port, "Unknown")
    
    def check_dns_resolution(self, hostname):
        """Check DNS resolution for a hostname"""
        try:
            self._add_to_network_log(f"DNS RESOLVE {hostname}")
            
            start_time = time.time()
            ip_address = socket.gethostbyname(hostname)
            elapsed = (time.time() - start_time) * 1000  # ms
            
            # Also get reverse DNS
            try:
                reverse_dns = socket.gethostbyaddr(ip_address)[0]
            except:
                reverse_dns = None
            
            return {
                'success': True,
                'ip_address': ip_address,
                'reverse_dns': reverse_dns,
                'response_time': elapsed,
                'timestamp': time.time()
            }
            
        except socket.gaierror as e:
            self._add_to_network_log(f"DNS ERROR {hostname}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"DNS check error: {e}")
            self._add_to_network_log(f"DNS CHECK ERROR {hostname}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def network_discovery(self, subnet=None):
        """Discover active hosts on network (similar to AJPanel)"""
        try:
            if subnet is None:
                subnet = self.config.plugins.pilotfs.network_scan_range.value
            
            base_ip = subnet.rstrip('.') + '.'
            active_hosts = []
            
            self._add_to_network_log(f"NETWORK DISCOVERY {base_ip}1-254")
            
            # Create threads for concurrent scanning
            threads = []
            results = {}
            
            def scan_ip(ip):
                try:
                    reachable, _ = self.check_host_status(ip, timeout=1)
                    results[ip] = reachable
                    if reachable:
                        active_hosts.append(ip)
                except:
                    results[ip] = False
            
            # Scan IP range 1-254
            for i in range(1, 255):
                ip = f"{base_ip}{i}"
                thread = threading.Thread(target=scan_ip, args=(ip,))
                thread.daemon = True
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete (with timeout)
            for thread in threads:
                thread.join(timeout=2)
            
            return active_hosts
            
        except Exception as e:
            logger.error(f"Network discovery error: {e}")
            self._add_to_network_log(f"NETWORK DISCOVERY ERROR: {str(e)}")
            return []
    
    def test_connection_with_diagnostics(self, name):
        """Test connection with full diagnostics"""
        try:
            connection = self.get_connection(name)
            if not connection:
                raise RemoteConnectionError(f"Connection not found: {name}")
            
            host = connection['host']
            port = connection['port']
            conn_type = connection['type']
            
            diagnostics = {
                'connection_name': name,
                'host': host,
                'port': port,
                'type': conn_type,
                'timestamp': datetime.now().isoformat(),
                'steps': []
            }
            
            # Step 1: DNS Resolution
            dns_result = self.check_dns_resolution(host)
            diagnostics['dns'] = dns_result
            diagnostics['steps'].append({
                'step': 'DNS Resolution',
                'success': dns_result['success'],
                'result': dns_result.get('ip_address', 'Failed')
            })
            
            if not dns_result['success']:
                return False, "DNS resolution failed", diagnostics
            
            # Step 2: Ping Check
            reachable, latency = self.check_host_status(host)
            diagnostics['ping'] = {
                'reachable': reachable,
                'latency': latency
            }
            diagnostics['steps'].append({
                'step': 'Ping Check',
                'success': reachable,
                'result': f"{'Reachable' if reachable else 'Unreachable'}" + 
                         (f" (latency: {latency}ms)" if latency else "")
            })
            
            if not reachable:
                return False, "Host is unreachable", diagnostics
            
            # Step 3: Port Scan
            open_ports, port_results = self.port_scan(host, [port])
            diagnostics['port_scan'] = port_results
            port_open = port in open_ports
            diagnostics['steps'].append({
                'step': f'Port {port} Check',
                'success': port_open,
                'result': f"{'Open' if port_open else 'Closed'}"
            })
            
            if not port_open:
                return False, f"Port {port} is closed", diagnostics
            
            # Step 4: Protocol-specific test
            if conn_type == 'ftp':
                success, message = self._test_ftp_connection(connection)
            elif conn_type == 'sftp':
                success, message = self._test_sftp_connection(connection)
            elif conn_type == 'webdav':
                success, message = self._test_webdav_connection(connection)
            elif conn_type == 'cifs':
                success, message = self._test_cifs_connection(connection)
            else:
                success, message = False, f"Unsupported type: {conn_type}"
            
            diagnostics['steps'].append({
                'step': 'Protocol Connection',
                'success': success,
                'result': message
            })
            
            if success:
                # Update connection status
                connection['status'] = 'online'
                connection['last_check'] = datetime.now().isoformat()
                connection['latency'] = latency
                self.update_connection(name)
            
            return success, message, diagnostics
            
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            self._add_to_network_log(f"CONNECTION TEST ERROR {name}: {str(e)}")
            return False, f"Test failed: {str(e)}", {}
    
    def _test_ftp_connection(self, connection):
        """Test FTP connection"""
        try:
            from .ftp_client import FTPClient
            client = FTPClient(self.config)
            success, message = client.test_connection(
                connection['host'],
                connection['port'],
                connection['username'],
                connection['password']
            )
            return success, message
        except Exception as e:
            return False, str(e)
    
    def _test_sftp_connection(self, connection):
        """Test SFTP connection"""
        try:
            from .sftp_client import SFTPClient
            client = SFTPClient(self.config)
            success, message = client.test_connection(
                connection['host'],
                connection['port'],
                connection['username'],
                connection['password']
            )
            return success, message
        except Exception as e:
            return False, str(e)
    
    def _test_webdav_connection(self, connection):
        """Test WebDAV connection"""
        try:
            from .webdav_client import WebDAVClient
            client = WebDAVClient(self.config)
            url = f"http://{connection['host']}:{connection['port']}"
            if 'path' in connection and connection['path']:
                url += connection['path']
            success, message = client.test_connection(
                url,
                connection['username'],
                connection['password']
            )
            return success, message
        except Exception as e:
            return False, str(e)
    
    def _test_cifs_connection(self, connection):
        """Test CIFS/SMB connection"""
        try:
            from .mount import MountManager
            mount_mgr = MountManager(self.config)
            
            # Test ping first
            reachable, _ = self.check_host_status(connection['host'])
            if not reachable:
                return False, "Host unreachable"
            
            # Test SMB ports
            port_445 = self.check_port(connection['host'], 445)
            if not port_445['open']:
                return False, "SMB port 445 closed"
            
            return True, "CIFS/SMB server accessible"
        except Exception as e:
            return False, str(e)
    
    def check_port(self, host, port, timeout=None):
        """Check if a specific port is open"""
        try:
            if timeout is None:
                timeout = self.config.plugins.pilotfs.port_scan_timeout.value
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((host, port))
            sock.close()
            
            return {
                'open': result == 0,
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'open': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def test_connection(self, name):
        """Test a saved connection (backward compatible)"""
        success, message, _ = self.test_connection_with_diagnostics(name)
        return success, message
    
    def get_network_log(self, limit=50):
        """Get network activity log"""
        if limit:
            return self.network_log[-limit:]
        return self.network_log
    
    def clear_network_log(self):
        """Clear network log"""
        self.network_log = []
        return True
    
    def _add_to_network_log(self, entry):
        """Add entry to network log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.network_log.append(f"[{timestamp}] {entry}")
        # Keep log size manageable
        if len(self.network_log) > 1000:
            self.network_log = self.network_log[-500:]
    
    def get_connection_stats(self):
        """Get statistics about connections"""
        total = len(self.connections)
        online = 0
        offline = 0
        unknown = 0
        
        for conn in self.connections.values():
            status = conn.get('status', 'unknown')
            if status == 'online':
                online += 1
            elif status == 'offline':
                offline += 1
            else:
                unknown += 1
        
        return {
            'total': total,
            'online': online,
            'offline': offline,
            'unknown': unknown,
            'last_updated': datetime.now().isoformat()
        }
    
    def auto_reconnect(self, name):
        """Attempt to automatically reconnect a connection"""
        if not self.config.plugins.pilotfs.auto_reconnect.value:
            return False, "Auto-reconnect disabled"
        
        connection = self.get_connection(name)
        if not connection:
            return False, "Connection not found"
        
        max_attempts = self.config.plugins.pilotfs.max_reconnect_attempts.value
        
        for attempt in range(1, max_attempts + 1):
            self._add_to_network_log(f"Reconnect attempt {attempt}/{max_attempts} for {name}")
            
            success, message = self.test_connection(name)
            
            if success:
                self._add_to_network_log(f"Reconnect successful for {name}")
                return True, f"Reconnected on attempt {attempt}"
            
            time.sleep(1)  # Wait before next attempt
        
        return False, f"Failed to reconnect after {max_attempts} attempts"
    
    def batch_test_connections(self, connection_names=None):
        """Test multiple connections in batch"""
        if connection_names is None:
            connection_names = list(self.connections.keys())
        
        results = {}
        
        for name in connection_names:
            if name in self.connections:
                success, message, _ = self.test_connection_with_diagnostics(name)
                results[name] = {
                    'success': success,
                    'message': message,
                    'host': self.connections[name]['host'],
                    'type': self.connections[name]['type']
                }
        
        return results
    
    def get_quick_stats(self):
        """Get quick statistics for display"""
        stats = self.get_connection_stats()
        
        # Get recent network log
        recent_log = self.get_network_log(limit=5)
        
        # Get last ping results
        last_pings = []
        for host, result in list(self.ping_results.items())[-3:]:
            age = int(time.time() - result['timestamp'])
            status = "✓" if result['reachable'] else "✗"
            latency = f" ({result.get('latency', 0)}ms)" if result.get('latency') else ""
            last_pings.append(f"{status} {host}{latency} ({age}s ago)")
        
        return {
            'connections': stats,
            'recent_log': recent_log,
            'last_pings': last_pings,
            'total_network_ops': len(self.network_log)
        }
    
    def _validate_connection(self, connection):
        """Validate connection parameters"""
        required_fields = ['type', 'host', 'port', 'username']
        
        for field in required_fields:
            if field not in connection:
                return False
        
        # Validate type
        if connection['type'] not in ['ftp', 'sftp', 'webdav', 'cifs']:
            return False
        
        # Validate host
        if not connection['host'] or len(connection['host']) > 255:
            return False
        
        # Validate port
        try:
            port = int(connection['port'])
            if port < 1 or port > 65535:
                return False
        except (ValueError, TypeError):
            return False
        
        return True
    
    def clear_connections(self):
        """Clear all connections"""
        try:
            self.connections = {}
            self.save_connections()
            return True
        except Exception as e:
            raise RemoteConnectionError(f"Failed to clear connections: {e}")