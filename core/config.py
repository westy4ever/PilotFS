from Components.config import config, ConfigSubsection, ConfigText, ConfigSelection, ConfigInteger, ConfigYesNo
import json
import os
from ..constants import BOOKMARKS_FILE, REMOTE_CONNECTIONS_FILE
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class PilotFSConfig:
    def __init__(self):
        self.setup_config()
        # Provide access to the global config
        self.plugins = config.plugins
    
    def setup_config(self):
        """Initialize configuration sections"""
        # Ensure config.plugins exists
        if not hasattr(config, 'plugins'):
            config.plugins = ConfigSubsection()
        
        # Ensure config.plugins.pilotfs exists
        if not hasattr(config.plugins, 'pilotfs'):
            config.plugins.pilotfs = ConfigSubsection()
        
        # Paths
        if not hasattr(config.plugins.pilotfs, 'left_path'):
            config.plugins.pilotfs.left_path = ConfigText(default="/media/hdd/", fixed_size=False)
        
        if not hasattr(config.plugins.pilotfs, 'right_path'):
            config.plugins.pilotfs.right_path = ConfigText(default="/", fixed_size=False)
        
        # Sorting
        if not hasattr(config.plugins.pilotfs, 'sort_mode'):
            config.plugins.pilotfs.sort_mode = ConfigSelection(
                default="name", 
                choices=[("name", "Name"), ("size", "Size"), ("date", "Date"), ("type", "Type")]
            )
        
        if not hasattr(config.plugins.pilotfs, 'left_sort_mode'):
            config.plugins.pilotfs.left_sort_mode = ConfigSelection(
                default="name", 
                choices=[("name", "Name"), ("size", "Size"), ("date", "Date"), ("type", "Type")]
            )
        
        if not hasattr(config.plugins.pilotfs, 'right_sort_mode'):
            config.plugins.pilotfs.right_sort_mode = ConfigSelection(
                default="name", 
                choices=[("name", "Name"), ("size", "Size"), ("date", "Date"), ("type", "Type")]
            )
        
        # Display
        if not hasattr(config.plugins.pilotfs, 'show_hidden'):
            config.plugins.pilotfs.show_hidden = ConfigSelection(
                default="no", 
                choices=[("yes", "Yes"), ("no", "No")]
            )
        
        if not hasattr(config.plugins.pilotfs, 'show_dirs_first'):
            config.plugins.pilotfs.show_dirs_first = ConfigSelection(
                default="yes", 
                choices=[("yes", "Yes"), ("no", "No")]
            )
        
        if not hasattr(config.plugins.pilotfs, 'show_current_dir'):
            config.plugins.pilotfs.show_current_dir = ConfigSelection(
                default="yes", 
                choices=[("yes", "Yes"), ("no", "No")]
            )
        
        # Operations
        if not hasattr(config.plugins.pilotfs, 'trash_enabled'):
            config.plugins.pilotfs.trash_enabled = ConfigSelection(
                default="yes", 
                choices=[("yes", "Yes"), ("no", "No")]
            )
        
        if not hasattr(config.plugins.pilotfs, 'cache_enabled'):
            config.plugins.pilotfs.cache_enabled = ConfigYesNo(default=True)
        
        # Preview
        if not hasattr(config.plugins.pilotfs, 'preview_size'):
            config.plugins.pilotfs.preview_size = ConfigSelection(
                default="1024", 
                choices=[("512", "512KB"), ("1024", "1MB"), ("2048", "2MB"), ("5120", "5MB")]
            )
        
        # Navigation
        if not hasattr(config.plugins.pilotfs, 'starting_pane'):
            config.plugins.pilotfs.starting_pane = ConfigSelection(
                default="left", 
                choices=[("left", "Left"), ("right", "Right")]
            )
        
        if not hasattr(config.plugins.pilotfs, 'save_left_on_exit'):
            config.plugins.pilotfs.save_left_on_exit = ConfigSelection(
                default="yes", 
                choices=[("yes", "Yes"), ("no", "No")]
            )
        
        if not hasattr(config.plugins.pilotfs, 'save_right_on_exit'):
            config.plugins.pilotfs.save_right_on_exit = ConfigSelection(
                default="yes", 
                choices=[("yes", "Yes"), ("no", "No")]
            )
        
        # Context Menu
        if not hasattr(config.plugins.pilotfs, 'ok_long_press_time'):
            config.plugins.pilotfs.ok_long_press_time = ConfigInteger(default=400, limits=(100, 2000))
        
        if not hasattr(config.plugins.pilotfs, 'enable_smart_context'):
            config.plugins.pilotfs.enable_smart_context = ConfigYesNo(default=True)
        
        if not hasattr(config.plugins.pilotfs, 'group_tools_menu'):
            config.plugins.pilotfs.group_tools_menu = ConfigYesNo(default=True)
        
        # Media
        if not hasattr(config.plugins.pilotfs, 'use_internal_player'):
            config.plugins.pilotfs.use_internal_player = ConfigYesNo(default=True)
        
        if not hasattr(config.plugins.pilotfs, 'fallback_to_external'):
            config.plugins.pilotfs.fallback_to_external = ConfigYesNo(default=True)
        
        # Remote
        if not hasattr(config.plugins.pilotfs, 'remote_ip'):
            config.plugins.pilotfs.remote_ip = ConfigText(default="192.168.1.10", fixed_size=False)
        
        # FTP
        if not hasattr(config.plugins.pilotfs, 'ftp_host'):
            config.plugins.pilotfs.ftp_host = ConfigText(default="", fixed_size=False)
        
        if not hasattr(config.plugins.pilotfs, 'ftp_port'):
            config.plugins.pilotfs.ftp_port = ConfigInteger(default=21)
        
        if not hasattr(config.plugins.pilotfs, 'ftp_user'):
            config.plugins.pilotfs.ftp_user = ConfigText(default="anonymous", fixed_size=False)
        
        if not hasattr(config.plugins.pilotfs, 'ftp_pass'):
            config.plugins.pilotfs.ftp_pass = ConfigText(default="", fixed_size=False)
        
        # SFTP
        if not hasattr(config.plugins.pilotfs, 'sftp_host'):
            config.plugins.pilotfs.sftp_host = ConfigText(default="", fixed_size=False)
        
        if not hasattr(config.plugins.pilotfs, 'sftp_port'):
            config.plugins.pilotfs.sftp_port = ConfigInteger(default=22)
        
        if not hasattr(config.plugins.pilotfs, 'sftp_user'):
            config.plugins.pilotfs.sftp_user = ConfigText(default="root", fixed_size=False)
        
        if not hasattr(config.plugins.pilotfs, 'sftp_pass'):
            config.plugins.pilotfs.sftp_pass = ConfigText(default="", fixed_size=False)
        
        # WebDAV
        if not hasattr(config.plugins.pilotfs, 'webdav_url'):
            config.plugins.pilotfs.webdav_url = ConfigText(default="", fixed_size=False)
        
        if not hasattr(config.plugins.pilotfs, 'webdav_user'):
            config.plugins.pilotfs.webdav_user = ConfigText(default="", fixed_size=False)
        
        if not hasattr(config.plugins.pilotfs, 'webdav_pass'):
            config.plugins.pilotfs.webdav_pass = ConfigText(default="", fixed_size=False)

        # Root Navigation - ADDED BY FIX SCRIPT
        if not hasattr(config.plugins.pilotfs, 'allow_root_navigation'):
            config.plugins.pilotfs.allow_root_navigation = ConfigYesNo(default=True)
        
        if not hasattr(config.plugins.pilotfs, 'show_parent_dir'):
            config.plugins.pilotfs.show_parent_dir = ConfigYesNo(default=True)
        
        if not hasattr(config.plugins.pilotfs, 'navigation_restriction'):
            config.plugins.pilotfs.navigation_restriction = ConfigSelection(
                default="none", 
                choices=[
                    ("none", "No Restriction - Full Access"),
                    ("media_only", "Media Folders Only (/media)"),
                    ("safe_mode", "Safe Mode (No System Folders)")
                ]
            )

    
    def load_bookmarks(self):
        """Load bookmarks from file with validation"""
        try:
            if os.path.exists(BOOKMARKS_FILE):
                with open(BOOKMARKS_FILE, 'r') as f:
                    bookmarks = json.load(f)
                
                # Validate loaded bookmarks
                if isinstance(bookmarks, dict):
                    # Filter out invalid entries
                    valid_bookmarks = {}
                    for key, path in bookmarks.items():
                        if (isinstance(key, (str, int)) and 
                            isinstance(path, str) and 
                            os.path.isabs(path)):  # Only keep absolute paths
                            valid_bookmarks[str(key)] = path
                    
                    logger.info(f"Loaded {len(valid_bookmarks)} valid bookmarks")
                    return valid_bookmarks
                else:
                    logger.warning(f"Invalid bookmarks format in {BOOKMARKS_FILE}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in bookmarks file: {e}")
        except Exception as e:
            logger.error(f"Error loading bookmarks: {e}")
        
        return {}
    
    def save_bookmarks(self, bookmarks):
        """Save bookmarks to file with validation"""
        try:
            # Ensure bookmarks is a dictionary
            if not isinstance(bookmarks, dict):
                logger.error("Bookmarks is not a dictionary")
                return False
            
            # Validate and filter bookmarks
            validated_bookmarks = {}
            for key, path in bookmarks.items():
                # Convert key to string and validate path
                key_str = str(key)
                if (isinstance(path, str) and 
                    os.path.isabs(path) and  # Only save absolute paths
                    len(key_str) == 1 and  # Single character keys for 1-9
                    key_str.isdigit() and  # Only digit keys
                    1 <= int(key_str) <= 9):  # Only keys 1-9
                    validated_bookmarks[key_str] = path
                else:
                    logger.warning(f"Skipping invalid bookmark: key={key}, path={path}")
            
            # Ensure directory exists
            bookmark_dir = os.path.dirname(BOOKMARKS_FILE)
            if bookmark_dir and not os.path.exists(bookmark_dir):
                os.makedirs(bookmark_dir, exist_ok=True)
            
            # Save validated bookmarks
            with open(BOOKMARKS_FILE, 'w') as f:
                json.dump(validated_bookmarks, f, indent=2)
            
            logger.info(f"Saved {len(validated_bookmarks)} bookmarks to {BOOKMARKS_FILE}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving bookmarks: {e}")
            return False
    
    def load_remote_connections(self):
        """Load remote connections from file with validation"""
        try:
            if os.path.exists(REMOTE_CONNECTIONS_FILE):
                with open(REMOTE_CONNECTIONS_FILE, 'r') as f:
                    connections = json.load(f)
                
                # Validate loaded connections
                if isinstance(connections, dict):
                    # Validate each connection
                    valid_connections = {}
                    for name, conn in connections.items():
                        if (isinstance(name, str) and 
                            isinstance(conn, dict) and
                            'type' in conn and 'host' in conn):
                            # Basic validation
                            valid_connections[name] = conn
                    
                    logger.info(f"Loaded {len(valid_connections)} valid remote connections")
                    return valid_connections
                else:
                    logger.warning(f"Invalid connections format in {REMOTE_CONNECTIONS_FILE}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in connections file: {e}")
        except Exception as e:
            logger.error(f"Error loading remote connections: {e}")
        
        return {}
    
    def save_remote_connections(self, connections):
        """Save remote connections to file with validation"""
        try:
            if not isinstance(connections, dict):
                logger.error("Connections is not a dictionary")
                return False
            
            # Validate connections
            validated_connections = {}
            for name, conn in connections.items():
                if (isinstance(name, str) and 
                    isinstance(conn, dict) and
                    'type' in conn and 'host' in conn):
                    # Basic validation of connection data
                    if conn['type'] in ['ftp', 'sftp', 'webdav', 'cifs']:
                        validated_connections[name] = conn
                    else:
                        logger.warning(f"Skipping connection with invalid type: {name}")
                else:
                    logger.warning(f"Skipping invalid connection: {name}")
            
            # Ensure directory exists
            remote_dir = os.path.dirname(REMOTE_CONNECTIONS_FILE)
            if remote_dir and not os.path.exists(remote_dir):
                os.makedirs(remote_dir, exist_ok=True)
            
            with open(REMOTE_CONNECTIONS_FILE, 'w') as f:
                json.dump(validated_connections, f, indent=2)
            
            logger.info(f"Saved {len(validated_connections)} remote connections to {REMOTE_CONNECTIONS_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error saving remote connections: {e}")
            return False
    
    def validate_config(self):
        """Validate all configuration values"""
        try:
            issues = []
            
            # Validate paths
            left_path = self.plugins.pilotfs.left_path.value
            right_path = self.plugins.pilotfs.right_path.value
            
            if not os.path.isabs(left_path):
                issues.append(f"Left path must be absolute: {left_path}")
            if not os.path.isabs(right_path):
                issues.append(f"Right path must be absolute: {right_path}")
            
            # Validate IP addresses if set
            remote_ip = self.plugins.pilotfs.remote_ip.value
            if remote_ip and remote_ip != "192.168.1.10":
                # Basic IP validation
                import re
                ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
                if not re.match(ip_pattern, remote_ip):
                    issues.append(f"Invalid remote IP format: {remote_ip}")
            
            # Validate ports
            ports = [
                ('FTP', self.plugins.pilotfs.ftp_port.value),
                ('SFTP', self.plugins.pilotfs.sftp_port.value),
            ]
            
            for name, port in ports:
                if port < 1 or port > 65535:
                    issues.append(f"Invalid {name} port: {port}")
            
            # Validate long press time
            long_press = self.plugins.pilotfs.ok_long_press_time.value
            if long_press < 100 or long_press > 2000:
                issues.append(f"Long press time out of range (100-2000ms): {long_press}")
            
            if issues:
                logger.warning(f"Configuration validation issues: {issues}")
                return False, issues
            else:
                logger.info("Configuration validation passed")
                return True, []
                
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False, [f"Validation error: {e}"]
    
    def reset_to_defaults(self):
        """Reset all configuration to defaults"""
        try:
            # General settings
            self.plugins.pilotfs.left_path.value = "/media/hdd/"
            self.plugins.pilotfs.right_path.value = "/"
            self.plugins.pilotfs.starting_pane.value = "left"
            self.plugins.pilotfs.show_dirs_first.value = "yes"
            self.plugins.pilotfs.left_sort_mode.value = "name"
            self.plugins.pilotfs.right_sort_mode.value = "name"
            
            # Context menu settings
            self.plugins.pilotfs.enable_smart_context.value = True
            self.plugins.pilotfs.ok_long_press_time.value = 400
            self.plugins.pilotfs.group_tools_menu.value = True
            
            # File operations
            self.plugins.pilotfs.trash_enabled.value = "yes"
            self.plugins.pilotfs.cache_enabled.value = True
            self.plugins.pilotfs.preview_size.value = "1024"
            
            # Exit behavior
            self.plugins.pilotfs.save_left_on_exit.value = "yes"
            self.plugins.pilotfs.save_right_on_exit.value = "yes"
            
            # Media player
            self.plugins.pilotfs.use_internal_player.value = True
            self.plugins.pilotfs.fallback_to_external.value = True
            
            # Remote access
            self.plugins.pilotfs.remote_ip.value = "192.168.1.10"
            self.plugins.pilotfs.ftp_host.value = ""
            self.plugins.pilotfs.ftp_port.value = 21
            self.plugins.pilotfs.ftp_user.value = "anonymous"
            self.plugins.pilotfs.ftp_pass.value = ""
            self.plugins.pilotfs.sftp_host.value = ""
            self.plugins.pilotfs.sftp_port.value = 22
            self.plugins.pilotfs.sftp_user.value = "root"
            self.plugins.pilotfs.sftp_pass.value = ""
            self.plugins.pilotfs.webdav_url.value = ""
            self.plugins.pilotfs.webdav_user.value = ""
            self.plugins.pilotfs.webdav_pass.value = ""
            
            # Save all
            for attr_name in dir(self.plugins.pilotfs):
                if not attr_name.startswith('_'):
                    item = getattr(self.plugins.pilotfs, attr_name)
                    if hasattr(item, 'save'):
                        item.save()
            
            logger.info("Configuration reset to defaults")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting to defaults: {e}")
            return False