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
    def __init__(self, session, plugin_config=None):
        Screen.__init__(self, session)
        self.session = session
        
        # Initialize config manager and ensure all attributes are registered
        self.config_manager = PilotFSConfig()
        
        # UI Layout Calculations
        desktop_w, desktop_h = getDesktop(0).size().width(), getDesktop(0).size().height()
        panel_w = int(desktop_w * 0.85)
        panel_h = int(desktop_h * 0.85)
        config_h = panel_h - 180
        button_y = panel_h - 70
        
        self.skin = f"""
        <screen name="PilotFSSetup" position="center,center" size="{panel_w},{panel_h}" title="⚙️ PilotFS Configuration" backgroundColor="#0d1117">
            <eLabel position="0,0" size="{panel_w},70" backgroundColor="#161b22" />
            <eLabel position="0,68" size="{panel_w},2" backgroundColor="#1976d2" />
            <eLabel text="⚙️ PILOTFS CONFIGURATION" position="20,15" size="{panel_w-40},40" 
                    font="Regular;32" halign="center" valign="center" transparent="1" 
                    foregroundColor="#58a6ff" shadowColor="#000000" shadowOffset="-2,-2" />
            <widget name="config" position="30,85" size="{panel_w-60},{config_h}" 
                    scrollbarMode="showOnDemand" itemHeight="55" backgroundColor="#0d1117" 
                    foregroundColor="#c9d1d9" selectionBackground="#1976d2" />
            <eLabel position="0,{button_y-10}" size="{panel_w},2" backgroundColor="#30363d" />
            <eLabel position="0,{button_y-8}" size="{panel_w},80" backgroundColor="#010409" />
            <eLabel position="20,{button_y}" size="180,55" backgroundColor="#7d1818" />
            <eLabel position="220,{button_y}" size="180,55" backgroundColor="#9e6a03" />
            <eLabel position="420,{button_y}" size="180,55" backgroundColor="#0969da" />
            <widget name="key_red" position="25,{button_y+5}" size="170,45" zPosition="1" font="Regular;22" halign="center" valign="center" transparent="1" foregroundColor="#ffffff" />
            <widget name="key_yellow" position="225,{button_y+5}" size="170,45" zPosition="1" font="Regular;22" halign="center" valign="center" transparent="1" foregroundColor="#ffffff" />
            <widget name="key_blue" position="425,{button_y+5}" size="170,45" zPosition="1" font="Regular;22" halign="center" valign="center" transparent="1" foregroundColor="#ffffff" />
        </screen>"""
        
        self["key_red"] = Label("Cancel")
        self["key_yellow"] = Label("Defaults")
        self["key_blue"] = Label("Save")
        
        self.list = []
        self.init_config_list()

        ConfigListScreen.__init__(self, self.list, session=session)
        
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "red": self.key_cancel,
            "yellow": self.load_defaults,
            "blue": self.key_save,
            "cancel": self.key_cancel,
            "left": self.keyLeft,
            "right": self.keyRight,
            "ok": self.keyOK
        }, -2)

    def init_config_list(self):
        """Build the configuration list from config.py attributes"""
        self.list = []
        p = config.plugins.pilotfs
        
        # General Settings
        self.list.append(getConfigListEntry("══════ General Settings ══════", ConfigNothing()))
        self.list.append(getConfigListEntry("Default Left Path:", p.left_path))
        self.list.append(getConfigListEntry("Default Right Path:", p.right_path))
        self.list.append(getConfigListEntry("Starting Pane:", p.starting_pane))
        self.list.append(getConfigListEntry("Show Directories First:", p.show_dirs_first))
        self.list.append(getConfigListEntry("Left Pane Sort Mode:", p.left_sort_mode))
        self.list.append(getConfigListEntry("Right Pane Sort Mode:", p.right_sort_mode))
        
        # Context Menu
        self.list.append(getConfigListEntry("══════ Context Menu Settings ══════", ConfigNothing()))
        self.list.append(getConfigListEntry("Enable Smart Context Menus:", p.enable_smart_context))
        self.list.append(getConfigListEntry("OK Long Press Time (ms):", p.ok_long_press_time))
        self.list.append(getConfigListEntry("Group Tools Menu:", p.group_tools_menu))
        
        # File Operations
        self.list.append(getConfigListEntry("══════ File Operations ══════", ConfigNothing()))
        self.list.append(getConfigListEntry("Enable Trash:", p.trash_enabled))
        self.list.append(getConfigListEntry("Enable Cache:", p.cache_enabled))
        self.list.append(getConfigListEntry("Preview Size Limit:", p.preview_size))
        
        # Exit Behavior
        self.list.append(getConfigListEntry("══════ Exit Behavior ══════", ConfigNothing()))
        self.list.append(getConfigListEntry("Save Left Path on Exit:", p.save_left_on_exit))
        self.list.append(getConfigListEntry("Save Right Path on Exit:", p.save_right_on_exit))
        
        # Media Player
        self.list.append(getConfigListEntry("══════ Media Player ══════", ConfigNothing()))
        self.list.append(getConfigListEntry("Use Internal Player:", p.use_internal_player))
        self.list.append(getConfigListEntry("Fallback to External:", p.fallback_to_external))
        
        # Remote & Network
        self.list.append(getConfigListEntry("══════ Remote Access ══════", ConfigNothing()))
        self.list.append(getConfigListEntry("Remote IP for Mount:", p.remote_ip))
        
        # FTP Settings
        self.list.append(getConfigListEntry("--- FTP Settings ---", ConfigNothing()))
        self.list.append(getConfigListEntry("FTP Host:", p.ftp_host))
        self.list.append(getConfigListEntry("FTP Port:", p.ftp_port))
        self.list.append(getConfigListEntry("FTP User:", p.ftp_user))
        self.list.append(getConfigListEntry("FTP Password:", p.ftp_pass))
        
        # SFTP Settings
        self.list.append(getConfigListEntry("--- SFTP Settings ---", ConfigNothing()))
        self.list.append(getConfigListEntry("SFTP Host:", p.sftp_host))
        self.list.append(getConfigListEntry("SFTP Port:", p.sftp_port))
        self.list.append(getConfigListEntry("SFTP User:", p.sftp_user))
        self.list.append(getConfigListEntry("SFTP Password:", p.sftp_pass))
        
        # WebDAV Settings
        self.list.append(getConfigListEntry("--- WebDAV Settings ---", ConfigNothing()))
        self.list.append(getConfigListEntry("WebDAV URL:", p.webdav_url))
        self.list.append(getConfigListEntry("WebDAV User:", p.webdav_user))
        self.list.append(getConfigListEntry("WebDAV Password:", p.webdav_pass))
        
        self["config"].list = self.list
        self["config"].l.setList(self.list)

    def changedEntry(self):
        """Standard handler for ConfigListScreen to refresh logic on change"""
        for x in self.onChangedEntry:
            x()

    def key_save(self):
        """Save and close"""
        try:
            for item in self.list:
                if len(item) > 1 and hasattr(item[1], 'save'):
                    item[1].save()
            config.plugins.pilotfs.save()
            config.save() # Commit global settings
            self.close()
        except Exception as e:
            logger.error(f"Error saving: {e}")

    def key_cancel(self):
        """Cancel changes"""
        for item in self.list:
            if len(item) > 1 and hasattr(item[1], 'cancel'):
                item[1].cancel()
        self.close()

    def load_defaults(self):
        """Use the reset logic from config.py"""
        self.session.openWithCallback(self.confirm_defaults, MessageBox, "Reset all settings to defaults?", MessageBox.TYPE_YESNO)

    def confirm_defaults(self, result):
        if result:
            # Use your professional reset method from config.py
            if self.config_manager.reset_to_defaults():
                self.init_config_list()
            else:
                logger.error("Failed to reset defaults")

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def keyOK(self):
        pass

    def update_help_text(self):
        """Update description if a help widget is added to skin later"""
        try:
            current = self["config"].getCurrent()
            if current:
                pass
        except Exception as e:
            logger.debug(f"Error updating help text: {e}")