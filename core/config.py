from Components.config import config, ConfigSubsection, ConfigText, ConfigSelection, ConfigInteger, ConfigYesNo, getConfigListEntry
import json
import os
from ..constants import BOOKMARKS_FILE, REMOTE_CONNECTIONS_FILE

class PilotFSConfig:
    def __init__(self):
        self.setup_config()
    
    def setup_config(self):
        """Initialize configuration sections"""
        if not hasattr(config.plugins, 'pilotfs'):
            config.plugins.pilotfs = ConfigSubsection()
        
        # Paths
        config.plugins.pilotfs.left_path = ConfigText(default="/media/hdd/", fixed_size=False)
        config.plugins.pilotfs.right_path = ConfigText(default="/", fixed_size=False)
        
        # Sorting
        config.plugins.pilotfs.sort_mode = ConfigSelection(
            default="name", 
            choices=[("name", "Name"), ("size", "Size"), ("date", "Date"), ("type", "Type")]
        )
        config.plugins.pilotfs.left_sort_mode = ConfigSelection(
            default="name", 
            choices=[("name", "Name"), ("size", "Size"), ("date", "Date"), ("type", "Type")]
        )
        config.plugins.pilotfs.right_sort_mode = ConfigSelection(
            default="name", 
            choices=[("name", "Name"), ("size", "Size"), ("date", "Date"), ("type", "Type")]
        )
        
        # Display
        config.plugins.pilotfs.show_hidden = ConfigSelection(
            default="no", 
            choices=[("yes", "Yes"), ("no", "No")]
        )
        config.plugins.pilotfs.show_dirs_first = ConfigSelection(
            default="yes", 
            choices=[("yes", "Yes"), ("no", "No")]
        )
        config.plugins.pilotfs.show_current_dir = ConfigSelection(
            default="yes", 
            choices=[("yes", "Yes"), ("no", "No")]
        )
        
        # Operations
        config.plugins.pilotfs.trash_enabled = ConfigSelection(
            default="yes", 
            choices=[("yes", "Yes"), ("no", "No")]
        )
        config.plugins.pilotfs.cache_enabled = ConfigYesNo(default=True)
        
        # Preview
        config.plugins.pilotfs.preview_size = ConfigSelection(
            default="1024", 
            choices=[("512", "512KB"), ("1024", "1MB"), ("2048", "2MB"), ("5120", "5MB")]
        )
        
        # Navigation
        config.plugins.pilotfs.starting_pane = ConfigSelection(
            default="left", 
            choices=[("left", "Left"), ("right", "Right")]
        )
        config.plugins.pilotfs.save_left_on_exit = ConfigSelection(
            default="yes", 
            choices=[("yes", "Yes"), ("no", "No")]
        )
        config.plugins.pilotfs.save_right_on_exit = ConfigSelection(
            default="yes", 
            choices=[("yes", "Yes"), ("no", "No")]
        )
        
        # Context Menu
        config.plugins.pilotfs.ok_long_press_time = ConfigInteger(default=400, limits=(100, 2000))
        config.plugins.pilotfs.enable_smart_context = ConfigYesNo(default=True)
        config.plugins.pilotfs.group_tools_menu = ConfigYesNo(default=True)
        
        # Media
        config.plugins.pilotfs.use_internal_player = ConfigYesNo(default=True)
        config.plugins.pilotfs.fallback_to_external = ConfigYesNo(default=True)
        
        # Remote
        config.plugins.pilotfs.remote_ip = ConfigText(default="192.168.1.10", fixed_size=False)
        
        # FTP
        config.plugins.pilotfs.ftp_host = ConfigText(default="", fixed_size=False)
        config.plugins.pilotfs.ftp_port = ConfigInteger(default=21)
        config.plugins.pilotfs.ftp_user = ConfigText(default="anonymous", fixed_size=False)
        config.plugins.pilotfs.ftp_pass = ConfigText(default="", fixed_size=False)
        
        # SFTP
        config.plugins.pilotfs.sftp_host = ConfigText(default="", fixed_size=False)
        config.plugins.pilotfs.sftp_port = ConfigInteger(default=22)
        config.plugins.pilotfs.sftp_user = ConfigText(default="root", fixed_size=False)
        config.plugins.pilotfs.sftp_pass = ConfigText(default="", fixed_size=False)
        
        # WebDAV
        config.plugins.pilotfs.webdav_url = ConfigText(default="", fixed_size=False)
        config.plugins.pilotfs.webdav_user = ConfigText(default="", fixed_size=False)
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
            with open(REMOTE_CONNECTIONS_FILE, 'w') as f:
                json.dump(connections, f, indent=2)
            return True
        except Exception:
            return False