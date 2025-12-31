from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry
from enigma import getDesktop

from ..core import PilotFSConfig
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class PilotFSSetup(ConfigListScreen, Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        
        # Get screen dimensions
        w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
        
        # Setup skin
        self.skin = f"""
        <screen name="PilotFSSetup" position="center,center" size="800,600" title="PilotFS Configuration">
            <widget name="config" position="20,50" size="760,480" scrollbarMode="showOnDemand" />
            <ePixmap pixmap="buttons/red.png" position="20,550" size="140,40" alphatest="on" />
            <ePixmap pixmap="buttons/green.png" position="180,550" size="140,40" alphatest="on" />
            <ePixmap pixmap="buttons/yellow.png" position="340,550" size="140,40" alphatest="on" />
            <ePixmap pixmap="buttons/blue.png" position="500,550" size="140,40" alphatest="on" />
            <widget name="key_red" position="20,550" size="140,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
            <widget name="key_green" position="180,550" size="140,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
            <widget name="key_yellow" position="340,550" size="140,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
            <widget name="key_blue" position="500,550" size="140,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
        </screen>"""
        
        # Initialize labels
        self["key_red"] = Label("Cancel")
        self["key_green"] = Label("OK")
        self["key_yellow"] = Label("Defaults")
        self["key_blue"] = Label("Save")
        
        # Initialize config list
        ConfigListScreen.__init__(self, [], session=session)
        
        # Setup config
        self.config_manager = PilotFSConfig()
        self.setup_title = "PilotFS Configuration"
        
        # Setup actions
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "green": self.key_save,
            "red": self.key_cancel,
            "yellow": self.load_defaults,
            "blue": self.key_save,
            "cancel": self.key_cancel,
            "ok": self.key_save,
        }, -2)
        
        # Initialize config list
        self.init_config_list()
    
    def init_config_list(self):
        """Initialize configuration list"""
        self.list = []
        
        # === GENERAL SETTINGS ===
        self.list.append(getConfigListEntry("=== General Settings ===", 
                     config.plugins.pilotfs.left_path))  # Dummy entry for header
        
        self.list.append(getConfigListEntry("Default Left Path:", 
                     config.plugins.pilotfs.left_path))
        self.list.append(getConfigListEntry("Default Right Path:", 
                     config.plugins.pilotfs.right_path))
        self.list.append(getConfigListEntry("Starting Pane:", 
                     config.plugins.pilotfs.starting_pane))
        self.list.append(getConfigListEntry("Show Directories First:", 
                     config.plugins.pilotfs.show_dirs_first))
        self.list.append(getConfigListEntry("Left Pane Sort Mode:", 
                     config.plugins.pilotfs.left_sort_mode))
        self.list.append(getConfigListEntry("Right Pane Sort Mode:", 
                     config.plugins.pilotfs.right_sort_mode))
        
        # === CONTEXT MENU SETTINGS ===
        self.list.append(getConfigListEntry("=== Context Menu Settings ===", 
                     config.plugins.pilotfs.left_path))  # Dummy entry
        
        self.list.append(getConfigListEntry("Enable Smart Context Menus:", 
                     config.plugins.pilotfs.enable_smart_context))
        self.list.append(getConfigListEntry("OK Long Press Time (ms):", 
                     config.plugins.pilotfs.ok_long_press_time))
        self.list.append(getConfigListEntry("Group Tools Menu:", 
                     config.plugins.pilotfs.group_tools_menu))
        
        # === FILE OPERATIONS ===
        self.list.append(getConfigListEntry("=== File Operations ===", 
                     config.plugins.pilotfs.left_path))  # Dummy entry
        
        self.list.append(getConfigListEntry("Enable Trash:", 
                     config.plugins.pilotfs.trash_enabled))
        self.list.append(getConfigListEntry("Enable Cache:", 
                     config.plugins.pilotfs.cache_enabled))
        self.list.append(getConfigListEntry("Preview Size Limit:", 
                     config.plugins.pilotfs.preview_size))
        
        # === EXIT BEHAVIOR ===
        self.list.append(getConfigListEntry("=== Exit Behavior ===", 
                     config.plugins.pilotfs.left_path))  # Dummy entry
        
        self.list.append(getConfigListEntry("Save Left Path on Exit:", 
                     config.plugins.pilotfs.save_left_on_exit))
        self.list.append(getConfigListEntry("Save Right Path on Exit:", 
                     config.plugins.pilotfs.save_right_on_exit))
        
        # === MEDIA PLAYER ===
        self.list.append(getConfigListEntry("=== Media Player ===", 
                     config.plugins.pilotfs.left_path))  # Dummy entry
        
        self.list.append(getConfigListEntry("Use Internal Player:", 
                     config.plugins.pilotfs.use_internal_player))
        self.list.append(getConfigListEntry("Fallback to External:", 
                     config.plugins.pilotfs.fallback_to_external))
        
        # === REMOTE ACCESS ===
        self.list.append(getConfigListEntry("=== Remote Access ===", 
                     config.plugins.pilotfs.left_path))  # Dummy entry
        
        self.list.append(getConfigListEntry("Remote IP for Mount:", 
                     config.plugins.pilotfs.remote_ip))
        
        # FTP settings
        self.list.append(getConfigListEntry("FTP Host:", 
                     config.plugins.pilotfs.ftp_host))
        self.list.append(getConfigListEntry("FTP Port:", 
                     config.plugins.pilotfs.ftp_port))
        self.list.append(getConfigListEntry("FTP User:", 
                     config.plugins.pilotfs.ftp_user))
        self.list.append(getConfigListEntry("FTP Password:", 
                     config.plugins.pilotfs.ftp_pass))
        
        # SFTP settings
        self.list.append(getConfigListEntry("SFTP Host:", 
                     config.plugins.pilotfs.sftp_host))
        self.list.append(getConfigListEntry("SFTP Port:", 
                     config.plugins.pilotfs.sftp_port))
        self.list.append(getConfigListEntry("SFTP User:", 
                     config.plugins.pilotfs.sftp_user))
        self.list.append(getConfigListEntry("SFTP Password:", 
                     config.plugins.pilotfs.sftp_pass))
        
        # WebDAV settings
        self.list.append(getConfigListEntry("WebDAV URL:", 
                     config.plugins.pilotfs.webdav_url))
        self.list.append(getConfigListEntry("WebDAV User:", 
                     config.plugins.pilotfs.webdav_user))
        self.list.append(getConfigListEntry("WebDAV Password:", 
                     config.plugins.pilotfs.webdav_pass))
        
        # Set the list
        self["config"].list = self.list
        self["config"].l.setList(self.list)
    
    def load_defaults(self):
        """Load default configuration"""
        self.session.openWithCallback(
            self.confirm_defaults,
            MessageBox,
            "Reset all settings to defaults?",
            MessageBox.TYPE_YESNO
        )
    
    def confirm_defaults(self, result):
        """Confirm and apply defaults"""
        if not result:
            return
        
        # General settings
        config.plugins.pilotfs.left_path.value = "/media/hdd/"
        config.plugins.pilotfs.right_path.value = "/"
        config.plugins.pilotfs.starting_pane.value = "left"
        config.plugins.pilotfs.show_dirs_first.value = "yes"
        config.plugins.pilotfs.left_sort_mode.value = "name"
        config.plugins.pilotfs.right_sort_mode.value = "name"
        
        # Context menu settings
        config.plugins.pilotfs.enable_smart_context.value = True
        config.plugins.pilotfs.ok_long_press_time.value = 400
        config.plugins.pilotfs.group_tools_menu.value = True
        
        # File operations
        config.plugins.pilotfs.trash_enabled.value = "yes"
        config.plugins.pilotfs.cache_enabled.value = True
        config.plugins.pilotfs.preview_size.value = "1024"
        
        # Exit behavior
        config.plugins.pilotfs.save_left_on_exit.value = "yes"
        config.plugins.pilotfs.save_right_on_exit.value = "yes"
        
        # Media player
        config.plugins.pilotfs.use_internal_player.value = True
        config.plugins.pilotfs.fallback_to_external.value = True
        
        # Remote access
        config.plugins.pilotfs.remote_ip.value = "192.168.1.10"
        config.plugins.pilotfs.ftp_host.value = ""
        config.plugins.pilotfs.ftp_port.value = 21
        config.plugins.pilotfs.ftp_user.value = "anonymous"
        config.plugins.pilotfs.ftp_pass.value = ""
        config.plugins.pilotfs.sftp_host.value = ""
        config.plugins.pilotfs.sftp_port.value = 22
        config.plugins.pilotfs.sftp_user.value = "root"
        config.plugins.pilotfs.sftp_pass.value = ""
        config.plugins.pilotfs.webdav_url.value = ""
        config.plugins.pilotfs.webdav_user.value = ""
        config.plugins.pilotfs.webdav_pass.value = ""
        
        # Save all
        for item in self.list:
            if hasattr(item[1], 'save'):
                item[1].save()
        
        # Reinitialize the list
        self.init_config_list()
        
        self.session.open(
            MessageBox,
            "Defaults loaded successfully!",
            MessageBox.TYPE_INFO,
            timeout=2
        )
        
        logger.info("Configuration reset to defaults")
    
    def key_save(self):
        """Save configuration"""
        for item in self.list:
            if hasattr(item[1], 'save'):
                item[1].save()
        
        logger.info("Configuration saved")
        self.close(True, self.session)
    
    def key_cancel(self):
        """Cancel configuration changes"""
        for item in self.list:
            if hasattr(item[1], 'cancel'):
                item[1].cancel()
        
        logger.info("Configuration changes cancelled")
        self.close(False, self.session)
    
    def keyLeft(self):
        """Handle left key"""
        ConfigListScreen.keyLeft(self)
        self.update_help_text()
    
    def keyRight(self):
        """Handle right key"""
        ConfigListScreen.keyRight(self)
        self.update_help_text()
    
    def update_help_text(self):
        """Update help text based on selected item"""
        current = self.getCurrent()
        if current:
            # Could add context-sensitive help here
            pass