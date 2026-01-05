from Components.config import config, ConfigSubsection, ConfigText, ConfigSelection, ConfigInteger, ConfigYesNo
import json
import os
from ..constants import BOOKMARKS_FILE, REMOTE_CONNECTIONS_FILE

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
    
    def load_bookmarks(self):
        """Load bookmarks from file"""
        try:
            if os.path.exists(BOOKMARKS_FILE):
                with open(BOOKMARKS_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_bookmarks(self, bookmarks):
        """Save bookmarks to file"""
        try:
            # Ensure directory exists
            bookmark_dir = os.path.dirname(BOOKMARKS_FILE)
            if bookmark_dir and not os.path.exists(bookmark_dir):
                os.makedirs(bookmark_dir, exist_ok=True)
            
            with open(BOOKMARKS_FILE, 'w') as f:
                json.dump(bookmarks, f, indent=2)
            return True
        except Exception:
            return False
    
    def load_remote_connections(self):
        """Load remote connections from file"""
        try:
            if os.path.exists(REMOTE_CONNECTIONS_FILE):
                with open(REMOTE_CONNECTIONS_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_remote_connections(self, connections):
        """Save remote connections to file"""
        try:
            # Ensure directory exists
            remote_dir = os.path.dirname(REMOTE_CONNECTIONS_FILE)
            if remote_dir and not os.path.exists(remote_dir):
                os.makedirs(remote_dir, exist_ok=True)
            
            with open(REMOTE_CONNECTIONS_FILE, 'w') as f:
                json.dump(connections, f, indent=2)
            return True
        except Exception:
            return False
