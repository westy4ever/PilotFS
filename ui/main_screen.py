from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.FileList import FileList
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from enigma import getDesktop, eTimer
import threading
import os
import time

from ..core.config import PilotFSConfig
from ..core.file_operations import FileOperations
from ..core.archive import ArchiveManager
from ..core.search import SearchEngine
from ..network.remote_manager import RemoteConnectionManager
from ..network.mount import MountManager
from ..utils.formatters import get_file_icon, format_size
from ..utils.logging_config import get_logger
from .context_menu import ContextMenuHandler
from .dialogs import Dialogs


logger = get_logger(__name__)

class PilotFSMain(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        
        # Get screen dimensions
        w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
        pane_width = (w - 60) // 2
        pane_height = h - 300  # Increased spacing to prevent overlap
        
        # Initialize core components
        self.config = PilotFSConfig()
        self.file_ops = FileOperations(self.config)
        self.archive_mgr = ArchiveManager(self.file_ops)
        self.search_engine = SearchEngine()
        self.remote_mgr = RemoteConnectionManager(self.config)
        self.mount_mgr = MountManager(self.config)
        
        # Initialize UI components
        self.dialogs = Dialogs(self.session)
        self.context_menu = ContextMenuHandler(self)
        
        # Setup UI
        self.setup_ui(w, h, pane_width, pane_height)
        
        # Initialize state
        self.init_state()
        
        # Setup actions
        self.setup_actions()
        
        # Start
        self.onLayoutFinish.append(self.startup)


    def setup_ui(self, w, h, pane_width, pane_height):
        """Setup user interface"""
        button_y = h - 60
        label_y = h - 45
        
        self.skin = f"""
        <screen name="PilotFSMain" position="0,0" size="{w},{h}" backgroundColor="#1a1a1a" flags="wfNoBorder">
            <eLabel position="0,0" size="{w},60" backgroundColor="#0055aa" />
            <eLabel text="PilotFS PLATINUM" position="20,8" size="600,44" font="Regular;30" halign="left" valign="center" transparent="1" foregroundColor="#ffffff" />
            <eLabel text="v6.1 Professional" position="{w-250},12" size="230,36" font="Regular;22" halign="right" valign="center" transparent="1" foregroundColor="#00ffff" />
            
            <!-- Left Pane Banner -->
            <widget name="left_banner" position="25,70" size="{pane_width},28" 
                    font="Regular;20" halign="left" valign="center" 
                    backgroundColor="#333333" foregroundColor="#ffff00" 
                    borderWidth="0" borderColor="#ffff00" />
            
            <!-- Vertical Separator -->
            <eLabel position="{pane_width + 30},70" size="10,28" 
                    backgroundColor="#555555" />
            
            <!-- Right Pane Banner -->
            <widget name="right_banner" position="{pane_width + 45},70" 
                    size="{pane_width},28" font="Regular;20" halign="left" 
                    valign="center" backgroundColor="#333333" 
                    foregroundColor="#aaaaaa" borderWidth="0" borderColor="#ffff00" />
            
            <!-- File Lists -->
            <widget name="left_pane" position="25,125" size="{pane_width},{pane_height}" 
                    itemHeight="40" selectionColor="#FF0000" scrollbarMode="showOnDemand" />
            <widget name="right_pane" position="{pane_width + 45},125" size="{pane_width},{pane_height}" 
                    itemHeight="40" selectionColor="#FF0000" scrollbarMode="showOnDemand" />
            
            <!-- Info Panels -->
            <widget name="progress_bar" position="20,{h-170}" size="{w-40},8" 
                    backgroundColor="#333333" foregroundColor="#00aaff" 
                    borderWidth="2" borderColor="#aaaaaa" />
            <widget name="info_panel" position="20,{h-155}" size="{w-40},30" 
                    font="Regular;20" foregroundColor="#ff8800" transparent="1" />
            <widget name="status_bar" position="20,{h-120}" size="{w-40},35" 
                    font="Regular;22" foregroundColor="#ffffff" transparent="1" />
            <widget name="path_label" position="20,{h-195}" size="{w-40},28" 
                    font="Regular;24" foregroundColor="#cccccc" transparent="1" noWrap="1" />
            
            <!-- Footer -->
            <eLabel position="0,{h-60}" size="{w},60" backgroundColor="#000000" />
            
            <!-- Button Icons -->
            <ePixmap pixmap="buttons/red.png" position="20,{button_y}" size="30,30" alphatest="on" />
            <ePixmap pixmap="buttons/green.png" position="180,{button_y}" size="30,30" alphatest="on" />
            <ePixmap pixmap="buttons/yellow.png" position="340,{button_y}" size="30,30" alphatest="on" />
            <ePixmap pixmap="buttons/blue.png" position="500,{button_y}" size="30,30" alphatest="on" />
            
            <!-- Button Labels -->
            <eLabel text="Delete" position="60,{label_y}" size="100,30" font="Regular;20" transparent="1" foregroundColor="#ffffff" />
            <eLabel text="Rename" position="220,{label_y}" size="100,30" font="Regular;20" transparent="1" foregroundColor="#ffffff" />
            <eLabel text="Select" position="380,{label_y}" size="100,30" font="Regular;20" transparent="1" foregroundColor="#ffffff" />
            <eLabel text="Copy/Move" position="540,{label_y}" size="150,30" font="Regular;20" transparent="1" foregroundColor="#ffffff" />
            
            <!-- Help Text -->
            <widget name="help_text" position="50,{h-80}" size="{w-100},30" 
                    font="Regular;18" halign="right" transparent="1" foregroundColor="#aaaaaa" />
        </screen>"""
        
        # Create widgets
        left_path = self.config.plugins.pilotfs.left_path.value
        right_path = self.config.plugins.pilotfs.right_path.value
        
        self["left_pane"] = FileList(left_path, showDirectories=True, showFiles=True)
        self["right_pane"] = FileList(right_path, showDirectories=True, showFiles=True)
        self["left_pane"].useSelection = True
        self["right_pane"].useSelection = True
        
        self["progress_bar"] = ProgressBar()
        self["status_bar"] = Label("Loading...")
        self["path_label"] = Label("")
        self["info_panel"] = Label("")
        self["left_banner"] = Label("◀ LEFT PANE")
        self["right_banner"] = Label("RIGHT PANE ▶")
        self["help_text"] = Label("OK:Navigate(hold:Menu) 0:Menu YEL:Select MENU:Tools")
    
    def init_state(self):
        """Initialize application state"""
        # Operation state
        self.operation_in_progress = False
        self.operation_lock = threading.Lock()
        self.operation_timer = eTimer()
        self.operation_timer.callback.append(self.update_operation_progress)
        self.operation_current = 0
        self.operation_total = 0
        
        # OK button - Simple navigation (long press disabled)
        # Long press feature removed for immediate response
        
        # Clipboard
        self.clipboard = []
        self.clipboard_mode = None  # 'copy' or 'cut'
        
        # Bookmarks
        self.bookmarks = self.config.load_bookmarks()
        
        # Active pane
        starting_pane = self.config.plugins.pilotfs.starting_pane.value
        if starting_pane == "left":
            self.active_pane = self["left_pane"]
            self.inactive_pane = self["right_pane"]
        else:
            self.active_pane = self["right_pane"]
            self.inactive_pane = self["left_pane"]
        
        # Sort modes
        self.left_sort_mode = self.config.plugins.pilotfs.left_sort_mode.value
        self.right_sort_mode = self.config.plugins.pilotfs.right_sort_mode.value
        
        # Filter
        self.filter_pattern = None
        
        # Preview state
        self.preview_in_progress = False
    
    def setup_actions(self):
        """Setup key mappings"""
        self["actions"] = ActionMap([
            "OkCancelActions", "ColorActions", "DirectionActions", 
            "MenuActions", "NumberActions", "ChannelSelectBaseActions"
        ], {
            "ok": self.ok_pressed,
            "cancel": self.close_plugin,
            "up": self.up,
            "down": self.down,
            "left": self.focus_left,
            "right": self.focus_right,
            "red": self.delete_request,
            "green": self.rename_request,
            "yellow": self.toggle_selection,
            "blue": self.quick_copy,
            "menu": self.open_tools,
            "0": self.zero_pressed,
            "1": lambda: self.quick_bookmark(1),
            "2": lambda: self.quick_bookmark(2),
            "3": lambda: self.quick_bookmark(3),
            "4": lambda: self.quick_bookmark(4),
            "5": lambda: self.quick_bookmark(5),
            "6": lambda: self.quick_bookmark(6),
            "7": lambda: self.quick_bookmark(7),
            "8": lambda: self.quick_bookmark(8),
            "9": lambda: self.quick_bookmark(9),
            "play": self.preview_media,
            "playpause": self.preview_media,
            "info": self.show_icon_legend,
            "text": self.preview_file,
            "nextBouquet": self.next_sort,
            "prevBouquet": self.prev_sort,
            "channelUp": self.next_sort,
            "channelDown": self.prev_sort,
            "audio": self.show_storage_selector,
        }, -1)
    
    def startup(self):
        """Startup initialization"""
        self.check_dependencies()
        self.update_ui()
        self.update_help_text()
        
        if self.config.plugins.pilotfs.show_dirs_first.value == "yes":
            self.apply_show_dirs_first()
        
        logger.info("PilotFS started successfully")
    
    # UI Update Methods
    def update_ui(self):
        """Update user interface"""
        self.update_banners()
        self.update_status_bar()
        self.update_path_label()
        self.update_info_panel()
    
    def update_banners(self):
        """Update pane banners"""
        is_left_active = (self.active_pane == self["left_pane"])
        is_right_active = (self.active_pane == self["right_pane"])
        
        # Get directory paths
        try:
            left_dir = self["left_pane"].getCurrentDirectory()
            right_dir = self["right_pane"].getCurrentDirectory()
            
            # Shorten if too long
            if len(left_dir) > 45:
                left_dir = "..." + left_dir[-42:]
            if len(right_dir) > 45:
                right_dir = "..." + right_dir[-42:]
            
            # Build text with indicators
            left_text = "◀ LEFT: " + left_dir if is_left_active else "LEFT: " + left_dir
            right_text = "RIGHT: " + right_dir + " ▶" if is_right_active else "RIGHT: " + right_dir
        except Exception as e:
            logger.error(f"Error getting directory paths: {e}")
            left_text = "◀ LEFT" if is_left_active else "LEFT"
            right_text = "RIGHT ▶" if is_right_active else "RIGHT"
        
        self["left_banner"].setText(left_text)
        self["right_banner"].setText(right_text)
        
        # Update colors
        try:
            from enigma import gFont
            ACTIVE_COLOR = 16776960   # Yellow
            INACTIVE_COLOR = 11184810  # Gray
            
            left_instance = self["left_banner"].instance
            right_instance = self["right_banner"].instance
            
            if left_instance:
                left_instance.setForegroundColor(ACTIVE_COLOR if is_left_active else INACTIVE_COLOR)
                left_instance.setFont(gFont("Regular", 22 if is_left_active else 19))
            
            if right_instance:
                right_instance.setForegroundColor(ACTIVE_COLOR if is_right_active else INACTIVE_COLOR)
                right_instance.setFont(gFont("Regular", 22 if is_right_active else 19))
                
        except Exception as e:
            logger.error(f"Banner styling error: {e}")
    
    def update_status_bar(self):
        """Update status bar text"""
        try:
            marked = [x for x in self.active_pane.list if x[0][3]]
        except Exception:
            marked = []
        
        if self.operation_in_progress:
            text = f"⚙ OPERATION: {self.operation_current}/{self.operation_total} items..."
        elif self.clipboard:
            mode = "COPY" if self.clipboard_mode == "copy" else "CUT"
            text = f"📋 CLIPBOARD: {len(self.clipboard)} items ({mode}) - Press BLUE to paste"
        elif marked:
            total_size = sum(self.file_ops.get_file_size(x[0][0]) for x in marked)
            text = f"✓ SELECTED: {len(marked)} items ({format_size(total_size)}) - Press 0 for menu"
        else:
            text = "Arrows Navigate | RED:delete  GREEN:rename  YELLOW:select  BLUE:copy/move"
        
        self["status_bar"].setText(text)
    
    def update_path_label(self):
        """Update path label"""
        try:
            current_dir = self.active_pane.getCurrentDirectory()
            self["path_label"].setText(f"📁 {current_dir}")
        except Exception as e:
            logger.error(f"Error updating path label: {e}")
    
    def update_info_panel(self):
        """Update info panel with current file details - OPTIMIZED"""
        try:
            sel = self.active_pane.getSelection()
            if sel and sel[0]:
                path = sel[0]
                name = os.path.basename(path)
                icon = get_file_icon(path)
                
                # Only get size for files, not directories (too slow)
                if os.path.isfile(path):
                    try:
                        size = os.path.getsize(path)
                        size_str = format_size(size)
                    except:
                        size_str = "?"
                else:
                    size_str = "DIR"
                
                text = f"{icon} {name} | {size_str}"
                self["info_panel"].setText(text)
                return
        except Exception as e:
            logger.debug(f"Error updating info panel: {e}")
        
        self["info_panel"].setText("")

    def update_operation_progress(self):
        """Update progress bar during operations"""
        try:
            if self.operation_total > 0:
                progress = int((self.operation_current / self.operation_total) * 100)
                self["progress_bar"].setValue(progress)
            self.update_ui()
        except Exception as e:
            logger.error(f"Error updating operation progress: {e}")
    
    def update_help_text(self):
        """Update help text"""
        if self.config.plugins.pilotfs.enable_smart_context.value:
            help_text = "OK:Play/Open 0:Ctx 1-9:BMark CH±:Sort MENU:Tools"
        else:
            help_text = "OK:Play/Open 0:Ctx 1-9:BMark CH±:Sort MENU:Tools"
        self["help_text"].setText(help_text)
    
    # OK Button Long Press Detection
    def ok_pressed(self):
        """Handle OK button press - SIMPLE NAVIGATION"""
        # Long press disabled - always navigate immediately
        self.execute_ok_navigation()
    


    def execute_ok_navigation(self):
        """Execute navigation - PERFECT SMART BEHAVIOR"""
        try:
            sel = self.active_pane.getSelection()
            if not sel or not sel[0]:
                return
            
            path = sel[0]
            
            if os.path.isdir(path):
                # Folders: Enter directory
                self.active_pane.changeDir(path)
                self.update_ui()
            else:
                # Files: Smart behavior based on type
                ext = os.path.splitext(path)[1].lower()
                
                # === PLAY DIRECTLY (NO MENU) ===
                # Video files: PLAY
                if ext in ['.mp4', '.mkv', '.avi', '.ts', '.m2ts', '.mov', '.m4v', '.mpg', '.mpeg', '.wmv', '.flv']:
                    self.preview_media()
                
                # Audio files: PLAY
                elif ext in ['.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.ac3', '.dts']:
                    self.preview_media()
                
                # === SHOW SMART CONTEXT MENU ===
                # Script files: Show menu (Run/View/Edit)
                elif ext in ['.sh', '.py', '.pl']:
                    self.context_menu.show_smart_context_menu(path)
                
                # Archive files: Show menu (Extract/View)
                elif ext in ['.zip', '.tar', '.tar.gz', '.tgz', '.rar', '.7z', '.gz']:
                    self.context_menu.show_smart_context_menu(path)
                
                # IPK packages: Show menu (Install/View)
                elif ext == '.ipk':
                    self.context_menu.show_smart_context_menu(path)
                
                # === PREVIEW DIRECTLY ===
                # Text files: Preview
                elif ext in ['.txt', '.log', '.conf', '.cfg', '.ini', '.xml', '.json', '.md']:
                    self.preview_file()
                
                # Image files: Preview
                elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                    self.dialogs.preview_image(path, self.file_ops)
                
                # Default: Show file info
                else:
                    self.show_file_info()
                    
        except Exception as e:
            logger.error(f"Error in OK navigation: {e}")
            self.dialogs.show_message(f"Navigation error: {e}", type="error")

    def up(self):
        """Move up in file list"""
        try:
            self.active_pane.up()
            self.update_info_panel()  # Fast update
        except Exception as e:
            logger.error(f"Error moving up: {e}")
    
    def down(self):
        """Move down in file list"""
        try:
            self.active_pane.down()
            self.update_info_panel()  # Fast update
        except Exception as e:
            logger.error(f"Error moving down: {e}")
    
    def focus_left(self):
        """Switch focus to left pane"""
        try:
            self.active_pane = self["left_pane"]
            self.inactive_pane = self["right_pane"]
            self.update_ui()
            self.update_help_text()
        except Exception as e:
            logger.error(f"Error focusing left pane: {e}")
    
    def focus_right(self):
        """Switch focus to right pane"""
        try:
            self.active_pane = self["right_pane"]
            self.inactive_pane = self["left_pane"]
            self.update_ui()
            self.update_help_text()
        except Exception as e:
            logger.error(f"Error focusing right pane: {e}")
    
    # File Operations
    def toggle_selection(self):
        """Toggle file selection"""
        if not self.operation_in_progress:
            try:
                self.active_pane.toggleSelection()
                self.update_ui()
            except Exception as e:
                logger.error(f"Error toggling selection: {e}")
    
    def delete_request(self):
        """Request file deletion - RED button"""
        try:
            # Check for multi-selected files first
            marked = [x for x in self.active_pane.list if x[0][3]]
            
            if marked:
                # Multi-select delete
                files = [x[0][0] for x in marked]
                self.dialogs.show_confirmation(
                    f"Delete {len(files)} selected items?\n\nThis cannot be undone!",
                    lambda res: self._execute_delete_multiple(res, files) if res else None
                )
            else:
                # Single file delete
                sel = self.active_pane.getSelection()
                if not sel or not sel[0]:
                    self.dialogs.show_message("No file selected!", type="info")
                    return
                
                item_path = sel[0]
                item_name = os.path.basename(item_path)
                is_dir = os.path.isdir(item_path)
                item_type = "folder" if is_dir else "file"
                
                self.dialogs.show_confirmation(
                    f"Delete {item_type} '{item_name}'?\n\nThis cannot be undone!",
                    lambda res: self._execute_delete(res, item_path, item_name) if res else None
                )
        except Exception as e:
            logger.error(f"Error in delete request: {e}")
            self.dialogs.show_message(f"Delete error: {e}", type="error")
    
    def _execute_delete(self, confirmed, item_path, item_name):
        """Execute deletion"""
        if not confirmed:
            return
        
        try:
            self.file_ops.delete(item_path)
            self.active_pane.refresh()
            self.update_ui()
            
            if self.config.plugins.pilotfs.trash_enabled.value == "yes":
                msg = f"Moved to trash: {item_name}"
            else:
                msg = f"Permanently deleted: {item_name}"
            
            self.dialogs.show_message(msg, type="info", timeout=2)
        except Exception as e:
            logger.error(f"Error executing delete: {e}")
            self.dialogs.show_message(f"Delete failed: {e}", type="error")
    
    def rename_request(self):
        """Request file rename - GREEN button"""
        try:
            # Check for multi-selected files
            marked = [x for x in self.active_pane.list if x[0][3]]
            
            if len(marked) > 1:
                # Multi-select - redirect to bulk rename
                self.dialogs.show_message(
                    f"Multiple files selected ({len(marked)} items)\n\nUse MENU -> Tools -> Bulk Rename\nfor renaming multiple files",
                    type="info"
                )
                return
            
            # Single file rename
            sel = self.active_pane.getSelection()
            if not sel or not sel[0]:
                self.dialogs.show_message("No file selected!", type="info")
                return
            
            item_path = sel[0]
            current_name = os.path.basename(item_path)
            
            self.session.openWithCallback(
                lambda new_name: self._execute_rename(new_name, item_path, current_name) if new_name else None,
                VirtualKeyBoard,
                title="Enter new name:",
                text=current_name
            )
        except Exception as e:
            logger.error(f"Error in rename request: {e}")
            self.dialogs.show_message(f"Rename error: {e}", type="error")
    
    def _execute_rename(self, new_name, old_path, old_name):
        """Execute rename"""
        if not new_name or new_name == old_name:
            return
        
        try:
            new_path = self.file_ops.rename(old_path, new_name)
            self.active_pane.refresh()
            self.update_ui()
            self.dialogs.show_message(f"Renamed to: {new_name}", type="info", timeout=2)
        except Exception as e:
            logger.error(f"Error executing rename: {e}")
            self.dialogs.show_message(f"Rename failed: {e}", type="error")
    
    def quick_copy(self):
        """Quick copy/move operation"""
        try:
            if self.clipboard:
                self.paste_from_clipboard()
                return
            
            # Get destination
            if self.active_pane == self["left_pane"]:
                dest_pane = self["right_pane"]
            else:
                dest_pane = self["left_pane"]
            
            dest = dest_pane.getCurrentDirectory()
            files = self.get_selected_files()
            
            if not files:
                self.dialogs.show_message("No files selected!", type="info")
                return
            
            self.dialogs.show_transfer_dialog(files, dest, self.execute_transfer)
        except Exception as e:
            logger.error(f"Error in quick copy: {e}")
            self.dialogs.show_message(f"Copy error: {e}", type="error")
    
    def get_selected_files(self):
        """Get selected files"""
        files = []
        try:
            for item in self.active_pane.list:
                if item[0][3]:  # Marked
                    files.append(item[0][0])
            
            if not files:
                sel = self.active_pane.getSelection()
                if sel and sel[0]:
                    files.append(sel[0])
        except Exception as e:
            logger.error(f"Error getting selected files: {e}")
        
        return files
    
    def paste_from_clipboard(self):
        """Paste files from clipboard"""
        if not self.clipboard:
            return
        
        try:
            dest = self.active_pane.getCurrentDirectory()
            
            if not os.path.isdir(dest):
                self.dialogs.show_message(f"Invalid destination: {dest}", type="error")
                return
            
            mode = "cp" if self.clipboard_mode == "copy" else "mv"
            action = "Copy" if mode == "cp" else "Move"
            
            self.dialogs.show_confirmation(
                f"{action} {len(self.clipboard)} items to:\n{dest}?",
                lambda res: self.execute_paste(res, mode, self.clipboard[:], dest)
            )
        except Exception as e:
            logger.error(f"Error pasting from clipboard: {e}")
            self.dialogs.show_message(f"Paste error: {e}", type="error")
    
    def execute_paste(self, confirmed, mode, files, dest):
        """Execute paste operation"""
        if not confirmed:
            return
        
        with self.operation_lock:
            if self.operation_in_progress:
                self.dialogs.show_message("Another operation is in progress!", type="warning")
                return
            self.operation_in_progress = True
        
        try:
            self.operation_current = 0
            self.operation_total = len(files)
            self.operation_timer.start(500)
            
            thread = threading.Thread(
                target=self._perform_paste,
                args=(mode, files, dest),
                daemon=True
            )
            thread.start()
        except Exception as e:
            logger.error(f"Error starting paste operation: {e}")
            with self.operation_lock:
                self.operation_in_progress = False
            self.dialogs.show_message(f"Paste failed: {e}", type="error")
    
    def _perform_paste(self, mode, files, dest):
        """Perform paste operation in thread"""
        try:
            for i, src in enumerate(files):
                try:
                    if mode == "cp":
                        self.file_ops.copy(src, dest)
                    elif mode == "mv":
                        self.file_ops.move(src, dest)
                    
                    with self.operation_lock:
                        self.operation_current = i + 1
                    
                except Exception as e:
                    logger.error(f"Paste failed for {src}: {e}")
            
            # Operation complete
            with self.operation_lock:
                self.operation_in_progress = False
                self.operation_timer.stop()
            
            # Clear clipboard if it was a cut operation
            if mode == "mv":
                self.clipboard = []
                self.clipboard_mode = None
            
            # Update UI
            self.active_pane.refresh()
            self.inactive_pane.refresh()
            self.update_ui()
            
            self.dialogs.show_message("Operation complete!", type="info")
            
        except Exception as e:
            logger.error(f"Paste operation failed: {e}")
            with self.operation_lock:
                self.operation_in_progress = False
                self.operation_timer.stop()
            
            self.dialogs.show_message(f"Operation failed:\n{e}", type="error")
    
    def execute_transfer(self, mode, files, dest):
        """Execute file transfer"""
        with self.operation_lock:
            if self.operation_in_progress:
                self.dialogs.show_message("Another operation is in progress!", type="warning")
                return
            self.operation_in_progress = True
        
        try:
            self.operation_current = 0
            self.operation_total = len(files)
            self.operation_timer.start(500)
            
            thread = threading.Thread(
                target=self._perform_transfer,
                args=(mode, files, dest),
                daemon=True
            )
            thread.start()
        except Exception as e:
            logger.error(f"Error starting transfer operation: {e}")
            with self.operation_lock:
                self.operation_in_progress = False
            self.dialogs.show_message(f"Transfer failed: {e}", type="error")
    
    def _perform_transfer(self, mode, files, dest):
        """Perform transfer in thread"""
        try:
            for i, src in enumerate(files):
                try:
                    if mode == "cp":
                        self.file_ops.copy(src, dest)
                    elif mode == "mv":
                        self.file_ops.move(src, dest)
                    
                    with self.operation_lock:
                        self.operation_current = i + 1
                    
                except Exception as e:
                    logger.error(f"Transfer failed for {src}: {e}")
            
            # Operation complete
            with self.operation_lock:
                self.operation_in_progress = False
                self.operation_timer.stop()
            
            # Update UI
            self.active_pane.refresh()
            self.inactive_pane.refresh()
            self.update_ui()
            
            self.dialogs.show_message("Transfer complete!", type="info")
            
        except Exception as e:
            logger.error(f"Transfer operation failed: {e}")
            with self.operation_lock:
                self.operation_in_progress = False
                self.operation_timer.stop()
            
            self.dialogs.show_message(f"Transfer failed:\n{e}", type="error")
    
    # Tools and Features
    def open_tools(self):
        """Open tools menu"""
        if self.operation_in_progress:
            self.dialogs.show_message("Please wait for current operation to complete!", type="info")
            return
        
        try:
            self.context_menu.show_tools_menu()
        except Exception as e:
            logger.error(f"Error opening tools menu: {e}")
            self.dialogs.show_message(f"Tools menu error: {e}", type="error")
    
    def zero_pressed(self):
        """0 button - Show context menu"""
        try:
            if not self.config.plugins.pilotfs.enable_smart_context.value:
                self.show_file_info()
                return
            
            marked = [x for x in self.active_pane.list if x[0][3]]
            
            if marked:
                self.context_menu.show_multi_selection_context_menu(marked)
            else:
                self.context_menu.show_context_menu()
        except Exception as e:
            logger.error(f"Error in zero pressed: {e}")
            self.dialogs.show_message(f"Context menu error: {e}", type="error")
    
    def quick_bookmark(self, num):
        """Quick bookmark access"""
        try:
            key = str(num)
            if key in self.bookmarks:
                path = self.bookmarks[key]
                if os.path.isdir(path):
                    self.active_pane.changeDir(path)
                    self.update_ui()
                    self["status_bar"].setText(f"Jumped to bookmark {num}: {os.path.basename(path)}")
                else:
                    self.dialogs.show_message(f"Bookmark {num} path not found: {path}", type="error")
            else:
                current = self.active_pane.getCurrentDirectory()
                self.bookmarks[key] = current
                self.config.save_bookmarks(self.bookmarks)
                self.dialogs.show_message(f"Bookmark {num} set to:\n{current}", type="info", timeout=2)
        except Exception as e:
            logger.error(f"Error in quick bookmark: {e}")
            self.dialogs.show_message(f"Bookmark error: {e}", type="error")
    
    def preview_file(self):
        """Preview file contents"""
        try:
            sel = self.active_pane.getSelection()
            if not sel or not sel[0]:
                return
            
            file_path = sel[0]
            
            if os.path.isdir(file_path):
                self.dialogs.show_message("Cannot preview directory!\n\nPress OK to enter folder.", type="info")
                return
            
            # Check file size
            try:
                size = self.file_ops.get_file_size(file_path)
                max_size = int(self.config.plugins.pilotfs.preview_size.value) * 1024
                if size > max_size:
                    self.dialogs.show_message(
                        f"File too large to preview!\n\nSize: {format_size(size)}\nLimit: {format_size(max_size)}",
                        type="info"
                    )
                    return
            except:
                pass
            
            # Delegate to dialogs
            self.dialogs.preview_file(file_path, self.file_ops, self.config)
        except Exception as e:
            logger.error(f"Error previewing file: {e}")
            self.dialogs.show_message(f"Preview error: {e}", type="error")
    
    def preview_media(self):
        """Preview media file - IMPROVED with proper playback"""
        try:
            if self.preview_in_progress:
                self.dialogs.show_message("Media preview already in progress!", type="warning")
                return
            
            sel = self.active_pane.getSelection()
            if not sel or not sel[0]:
                return
            
            file_path = sel[0]
            
            # Check if it's a media file
            media_extensions = ['.mp4', '.mkv', '.avi', '.ts', '.m2ts', '.mp3', '.flac', '.wav']
            if not any(file_path.lower().endswith(ext) for ext in media_extensions):
                self.dialogs.show_message(
                    "Not a media file!\n\nSupported: MP4, MKV, AVI, TS, MP3, FLAC, etc.",
                    type="info"
                )
                return
            
            self.preview_in_progress = True
            
            # Try to play using Enigma2 service
            if self.config.plugins.pilotfs.use_internal_player.value:
                try:
                    self.play_media_file(file_path)
                except Exception as e:
                    logger.error(f"Internal player failed: {e}")
                    if self.config.plugins.pilotfs.fallback_to_external.value:
                        self.play_with_external_player(file_path)
                    else:
                        self.dialogs.show_message(f"Media playback failed:\n{e}", type="error")
            else:
                self.play_with_external_player(file_path)
            
            self.preview_in_progress = False
            
        except Exception as e:
            logger.error(f"Error previewing media: {e}")
            self.preview_in_progress = False
            self.dialogs.show_message(f"Media preview error: {e}", type="error")
    
    def show_icon_legend(self):
        """Show file type icon legend"""
        legend = "📋 FILE TYPE ICONS GUIDE:\n\n"
        legend += "📁 Folder / Directory\n"
        legend += "🎬 Video (MP4, MKV, AVI, TS)\n"
        legend += "🎵 Audio (MP3, FLAC, WAV, AAC)\n"
        legend += "🖼️ Image (JPG, PNG, GIF, BMP)\n"
        legend += "📦 Archive (ZIP, TAR, RAR, GZ)\n"
        legend += "📄 Text/Config (TXT, XML, PY, SH)\n"
        legend += "📄 Other Files\n\n"
        legend += "Icons appear in the info panel at the bottom."
        
        self.dialogs.show_message(legend, type="info")
    
    def show_storage_selector(self):
        """Show storage device selector"""
        if self.operation_in_progress:
            self.dialogs.show_message("Please wait for current operation to complete!", type="info")
            return
        
        try:
            self.dialogs.show_storage_selector(self.active_pane.changeDir, self.update_ui)
        except Exception as e:
            logger.error(f"Error showing storage selector: {e}")
            self.dialogs.show_message(f"Storage selector error: {e}", type="error")
    
    def show_file_info(self):
        """Show detailed file information"""
        try:
            sel = self.active_pane.getSelection()
            if not sel or not sel[0]:
                return
            
            info = self.file_ops.get_file_info(sel[0])
            if info:
                text = f"File: {info['name']}\n"
                text += f"Path: {os.path.dirname(info['path'])}\n"
                text += f"Size: {info['size_formatted']}\n"
                text += f"Modified: {info['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                text += f"Permissions: {info['permissions']}\n"
                
                if info['is_dir']:
                    text += f"Type: Directory\n"
                    if 'item_count' in info:
                        text += f"Items: {info['item_count']}\n"
                else:
                    text += f"Type: File\n"
                
                self.dialogs.show_message(text, type="info")
        except Exception as e:
            logger.error(f"Error showing file info: {e}")
            self.dialogs.show_message(f"File info error: {e}", type="error")
    
    # Sorting
    def next_sort(self):
        """Cycle to next sort mode"""
        try:
            if self.active_pane == self["left_pane"]:
                modes = ["name", "size", "date", "type"]
                current_idx = modes.index(self.left_sort_mode) if self.left_sort_mode in modes else 0
                self.left_sort_mode = modes[(current_idx + 1) % len(modes)]
                self.config.plugins.pilotfs.left_sort_mode.value = self.left_sort_mode
                self.config.plugins.pilotfs.left_sort_mode.save()
            else:
                modes = ["name", "size", "date", "type"]
                current_idx = modes.index(self.right_sort_mode) if self.right_sort_mode in modes else 0
                self.right_sort_mode = modes[(current_idx + 1) % len(modes)]
                self.config.plugins.pilotfs.right_sort_mode.value = self.right_sort_mode
                self.config.plugins.pilotfs.right_sort_mode.save()
            
            self.apply_sorting()
            self.update_ui()
            self.dialogs.show_message(f"Sort: {self.left_sort_mode if self.active_pane == self['left_pane'] else self.right_sort_mode.upper()}", 
                                     type="info", timeout=1)
        except Exception as e:
            logger.error(f"Error in next sort: {e}")
    
    def prev_sort(self):
        """Cycle to previous sort mode"""
        try:
            if self.active_pane == self["left_pane"]:
                modes = ["name", "size", "date", "type"]
                current_idx = modes.index(self.left_sort_mode) if self.left_sort_mode in modes else 0
                self.left_sort_mode = modes[(current_idx - 1) % len(modes)]
                self.config.plugins.pilotfs.left_sort_mode.value = self.left_sort_mode
                self.config.plugins.pilotfs.left_sort_mode.save()
            else:
                modes = ["name", "size", "date", "type"]
                current_idx = modes.index(self.right_sort_mode) if self.right_sort_mode in modes else 0
                self.right_sort_mode = modes[(current_idx - 1) % len(modes)]
                self.config.plugins.pilotfs.right_sort_mode.value = self.right_sort_mode
                self.config.plugins.pilotfs.right_sort_mode.save()
            
            self.apply_sorting()
            self.update_ui()
            self.dialogs.show_message(f"Sort: {self.left_sort_mode if self.active_pane == self['left_pane'] else self.right_sort_mode.upper()}", 
                                     type="info", timeout=1)
        except Exception as e:
            logger.error(f"Error in prev sort: {e}")
    
    def apply_sorting(self):
        """Apply current sort mode to active pane"""
        try:
            items = self.active_pane.list
            if not items:
                return
            
            # Determine sort mode
            if self.active_pane == self["left_pane"]:
                current_sort = self.left_sort_mode
            else:
                current_sort = self.right_sort_mode
            
            # Sort based on mode
            if current_sort == "name":
                items.sort(key=lambda x: x[0][0].lower())
            elif current_sort == "size":
                items.sort(key=lambda x: self.file_ops.get_file_size(x[0][0]), reverse=True)
            elif current_sort == "date":
                items.sort(key=lambda x: os.path.getmtime(x[0][0]) if os.path.exists(x[0][0]) else 0, reverse=True)
            elif current_sort == "type":
                items.sort(key=lambda x: (not x[0][1], os.path.splitext(x[0][0])[1].lower()))
            
            # Apply show directories first
            if self.config.plugins.pilotfs.show_dirs_first.value == "yes":
                dirs = [item for item in items if item[0][1]]
                files = [item for item in items if not item[0][1]]
                items = dirs + files
            
            self.active_pane.list = items
            self.active_pane.l.setList(items)
        except Exception as e:
            logger.error(f"Sorting failed: {e}")
    
    def apply_show_dirs_first(self):
        """Apply show directories first setting"""
        try:
            items = self.active_pane.list
            if not items:
                return
            
            dirs = [item for item in items if item[0][1]]
            files = [item for item in items if not item[0][1]]
            
            self.active_pane.list = dirs + files
            self.active_pane.l.setList(self.active_pane.list)
        except Exception as e:
            logger.error(f"Show dirs first failed: {e}")
    
    # System Methods
    def check_dependencies(self):
        """Check if required tools are available"""
        tools = {
            'rclone': 'Cloud sync',
            'zip': 'ZIP archives',
            'unzip': 'ZIP extraction',
            'tar': 'TAR archives',
            'cifs-utils': 'Network mounts',
            'smbclient': 'Network scanning',
            'curl': 'WebDAV support',
            'ftp': 'FTP client',
        }
        
        missing = []
        for tool, desc in tools.items():
            try:
                import subprocess
                result = subprocess.run(["which", tool], capture_output=True, timeout=2)
                if result.returncode != 0:
                    missing.append(f"{tool} ({desc})")
            except:
                missing.append(f"{tool} ({desc})")
        
        if missing:
            logger.warning(f"Missing tools: {', '.join(missing)}")
    
    def movie_player_callback(self, *args):
        """Callback when movie player closes - return to plugin"""
        logger.info("Movie player closed, returning to plugin")
        self.preview_in_progress = False
        # Refresh the current view
        self.update_ui()
    
    def play_media_file(self, path):
        """Play media file using Enigma2 service player"""
        try:
            from enigma import eServiceReference
            from Screens.InfoBar import MoviePlayer
            
            logger.info(f"Playing: {path}")
            
            # Create service reference (4097 = gstreamer)
            ref = eServiceReference(4097, 0, path)
            ref.setName(os.path.basename(path))
            
            # Open MoviePlayer with callback
            self.session.openWithCallback(
                self.movie_player_callback,
                MoviePlayer,
                ref
            )
            
        except ImportError:
            # Final fallback - external player
            logger.warning("Enigma2 player not available, using external")
            self.play_with_external_player(path)
        except Exception as e:
            logger.error(f"Playback error: {e}")
            self.dialogs.show_message(
                f"Cannot play media file:\n{os.path.basename(path)}\n\nError: {e}",
                type="error"
            )
    
    def play_with_external_player(self, path):
        """Play with external player as fallback"""
        import subprocess
        import threading
        
        def play_thread():
            # Try common media players
            players = [
                ['gst-launch-1.0', 'playbin', 'uri=file://' + path],
                ['ffplay', '-autoexit', '-nodisp', path],
                ['mplayer', '-quiet', path]
            ]
            
            for player_cmd in players:
                try:
                    subprocess.Popen(player_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.dialogs.show_message(
                        f"Playing with external player:\n{os.path.basename(path)}",
                        type="info",
                        timeout=3
                    )
                    return
                except FileNotFoundError:
                    continue
            
            self.dialogs.show_message(
                "No media player available!\n\nInstall: opkg install gstreamer1.0",
                type="error"
            )
        
        threading.Thread(target=play_thread, daemon=True).start()
    
    def close_plugin(self):
        """Clean shutdown"""
        if self.operation_in_progress:
            self.dialogs.show_message("Operation in progress!\n\nPlease wait...", type="warning")
            return
        
        try:
            # Save paths if configured
            if self.config.plugins.pilotfs.save_left_on_exit.value == "yes":
                self.config.plugins.pilotfs.left_path.value = self["left_pane"].getCurrentDirectory()
                self.config.plugins.pilotfs.left_path.save()
            
            if self.config.plugins.pilotfs.save_right_on_exit.value == "yes":
                self.config.plugins.pilotfs.right_path.value = self["right_pane"].getCurrentDirectory()
                self.config.plugins.pilotfs.right_path.save()
            
            logger.info("PilotFS shutdown complete")
            self.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.close()
    
    # Helper method for delete multiple
    def _execute_delete_multiple(self, confirmed, files):
        """Execute deletion of multiple items"""
        if not confirmed:
            return
        
        try:
            success = 0
            errors = []
            
            for item_path in files:
                try:
                    self.file_ops.delete(item_path)
                    success += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(item_path)}: {str(e)[:30]}")
            
            msg = f"Deleted: {success} items\n"
            if errors:
                msg += f"\nFailed: {len(errors)}\n"
                msg += "\n".join(errors[:3])
                if len(errors) > 3:
                    msg += f"\n... and {len(errors) - 3} more"
            
            self.active_pane.refresh()
            self.update_ui()
            self.dialogs.show_message(msg, type="info")
        except Exception as e:
            logger.error(f"Error deleting multiple items: {e}")
            self.dialogs.show_message(f"Delete multiple failed: {e}", type="error")