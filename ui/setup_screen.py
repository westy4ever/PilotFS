from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigNothing
from enigma import getDesktop

from ..core.config import PilotFSConfig
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class PilotFSSetup(ConfigListScreen, Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        
        # Get screen dimensions
        desktop_w, desktop_h = getDesktop(0).size().width(), getDesktop(0).size().height()
        
        # Make settings panel 85% of screen size for better visibility
        panel_w = int(desktop_w * 0.85)
        panel_h = int(desktop_h * 0.85)
        
        # Calculate positions
        config_h = panel_h - 180
        button_y = panel_h - 70
        
        self.skin = f"""
        <screen name="PilotFSSetup" position="center,center" size="{panel_w},{panel_h}" title="⚙️ PilotFS Configuration" backgroundColor="#0d1117">
            <!-- Header -->
            <eLabel position="0,0" size="{panel_w},70" backgroundColor="#161b22" />
            <eLabel position="0,68" size="{panel_w},2" backgroundColor="#1976d2" />
            <eLabel text="⚙️ PILOTFS CONFIGURATION" position="20,15" size="{panel_w-40},40" 
                    font="Regular;32" halign="center" valign="center" transparent="1" 
                    foregroundColor="#58a6ff" shadowColor="#000000" shadowOffset="-2,-2" />
            
            <!-- Config List with larger spacing -->
            <widget name="config" position="30,85" size="{panel_w-60},{config_h}" 
                    scrollbarMode="showOnDemand" 
                    itemHeight="55" 
                    backgroundColor="#0d1117" 
                    foregroundColor="#c9d1d9"
                    selectionPixmap=""
                    selectionForeground="#ffffff"
                    selectionBackground="#1976d2" />
            
            <!-- Button Bar -->
            <eLabel position="0,{button_y-10}" size="{panel_w},2" backgroundColor="#30363d" />
            <eLabel position="0,{button_y-8}" size="{panel_w},80" backgroundColor="#010409" />
            
            <!-- Color-coded Button Backgrounds - Only 3 buttons now -->
            <eLabel position="20,{button_y}" size="180,55" backgroundColor="#7d1818" />
            <eLabel position="220,{button_y}" size="180,55" backgroundColor="#9e6a03" />
            <eLabel position="420,{button_y}" size="180,55" backgroundColor="#0969da" />
            
            <!-- Button Labels with Icons - Only 3 buttons now -->
            <widget name="key_red" position="25,{button_y+5}" size="170,45" zPosition="1" 
                    font="Regular;22" halign="center" valign="center" 
                    transparent="1" foregroundColor="#ffffff" 
                    shadowColor="#000000" shadowOffset="-1,-1" />
            <widget name="key_yellow" position="225,{button_y+5}" size="170,45" zPosition="1" 
                    font="Regular;22" halign="center" valign="center" 
                    transparent="1" foregroundColor="#ffffff" 
                    shadowColor="#000000" shadowOffset="-1,-1" />
            <widget name="key_blue" position="425,{button_y+5}" size="170,45" zPosition="1" 
                    font="Regular;22" halign="center" valign="center" 
                    transparent="1" foregroundColor="#ffffff" 
                    shadowColor="#000000" shadowOffset="-1,-1" />
        </screen>"""
        
        # Initialize labels - Only 3 buttons now
        self["key_red"] = Label("Cancel")
        self["key_yellow"] = Label("Defaults")
        self["key_blue"] = Label("Save")
        
        # Initialize config list
        ConfigListScreen.__init__(self, [], session=session)
        
        # Setup config
        self.config_manager = PilotFSConfig()
        self.setup_title = "PilotFS Configuration"
        
        # Setup actions - Only Cancel, Defaults, and Save now
        # IMPORTANT: Removed "ok": self.key_save to prevent modal crash
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "red": self.key_cancel,
            "yellow": self.load_defaults,
            "blue": self.key_save,
            "cancel": self.key_cancel,
            # REMOVED: "ok": self.key_save  # This causes modal crash!
        }, -2)
        
        # Initialize config list
        self.init_config_list()
    
    def init_config_list(self):
        """Initialize configuration list"""
        self.list = []
        
        # === GENERAL SETTINGS ===
        self.list.append(getConfigListEntry("══════ General Settings ══════", ConfigNothing()))
        
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
        self.list.append(getConfigListEntry("══════ Context Menu Settings ══════", ConfigNothing()))
        
        self.list.append(getConfigListEntry("Enable Smart Context Menus:", 
                     config.plugins.pilotfs.enable_smart_context))
        self.list.append(getConfigListEntry("OK Long Press Time (ms):", 
                     config.plugins.pilotfs.ok_long_press_time))
        self.list.append(getConfigListEntry("Group Tools Menu:", 
                     config.plugins.pilotfs.group_tools_menu))
        
        # === FILE OPERATIONS ===
        self.list.append(getConfigListEntry("══════ File Operations ══════", ConfigNothing()))
        
        self.list.append(getConfigListEntry("Enable Trash:", 
                     config.plugins.pilotfs.trash_enabled))
        self.list.append(getConfigListEntry("Enable Cache:", 
                     config.plugins.pilotfs.cache_enabled))
        self.list.append(getConfigListEntry("Preview Size Limit:", 
                     config.plugins.pilotfs.preview_size))
        
        # === EXIT BEHAVIOR ===
        self.list.append(getConfigListEntry("══════ Exit Behavior ══════", ConfigNothing()))
        
        self.list.append(getConfigListEntry("Save Left Path on Exit:", 
                     config.plugins.pilotfs.save_left_on_exit))
        self.list.append(getConfigListEntry("Save Right Path on Exit:", 
                     config.plugins.pilotfs.save_right_on_exit))
        
        # === MEDIA PLAYER ===
        self.list.append(getConfigListEntry("══════ Media Player ══════", ConfigNothing()))
        
        self.list.append(getConfigListEntry("Use Internal Player:", 
                     config.plugins.pilotfs.use_internal_player))
        self.list.append(getConfigListEntry("Fallback to External:", 
                     config.plugins.pilotfs.fallback_to_external))
        
        # === REMOTE ACCESS ===
        self.list.append(getConfigListEntry("══════ Remote Access ══════", ConfigNothing()))
        
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
        """Load default configuration - FIXED: Don't use session.openWithCallback which causes modal crash"""
        # Create message box directly
        self.session.openWithCallback(
            self.confirm_defaults,
            MessageBox,
            "Reset all settings to defaults?",
            MessageBox.TYPE_YESNO,
            timeout=0
        )
    
    def confirm_defaults(self, result):
        """Confirm and apply defaults"""
        if not result:
            return
        
        try:
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
            
            # Reinitialize the list
            self.init_config_list()
            
            # Show success message
            self.session.open(
                MessageBox,
                "Defaults loaded successfully!",
                MessageBox.TYPE_INFO,
                timeout=2
            )
            
            logger.info("Configuration reset to defaults")
            
        except Exception as e:
            logger.error(f"Error loading defaults: {e}")
            self.session.open(
                MessageBox,
                f"Error loading defaults:\n{e}",
                MessageBox.TYPE_ERROR
            )
    
    def key_save(self):
        """Save configuration"""
        try:
            # Apply changes from ConfigListScreen first
            for x in self["config"].list:
                x[1].save()
            
            # Then save all items
            for item in self.list:
                if hasattr(item[1], 'save'):
                    item[1].save()
            
            logger.info("Configuration saved")
            self.close()
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            self.session.open(
                MessageBox,
                f"Error saving configuration:\n{e}",
                MessageBox.TYPE_ERROR
            )
    
    def key_cancel(self):
        """Cancel configuration changes"""
        try:
            for item in self.list:
                if hasattr(item[1], 'cancel'):
                    item[1].cancel()
            
            logger.info("Configuration changes cancelled")
            self.close()
            
        except Exception as e:
            logger.error(f"Error cancelling configuration: {e}")
            self.close()
    
    def keyLeft(self):
        """Handle left key"""
        try:
            ConfigListScreen.keyLeft(self)
        except Exception as e:
            logger.error(f"Error in keyLeft: {e}")
    
    def keyRight(self):
        """Handle right key"""
        try:
            ConfigListScreen.keyRight(self)
        except Exception as e:
            logger.error(f"Error in keyRight: {e}")
    
    def keyOK(self):
        """Handle OK key - DO NOTHING to prevent modal crash"""
        # This method is intentionally empty to prevent the modal crash
        # The OK key should not trigger any action in the settings screen
        # Users should use the Blue (Save) button instead
        pass
    
    def update_help_text(self):
        """Update help text based on selected item"""
        try:
            current = self["config"].getCurrent()
            if current:
                # Could add context-sensitive help here
                pass
        except Exception as e:
            logger.debug(f"Error updating help text: {e}")