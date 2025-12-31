from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
import os

from ..utils.formatters import get_file_icon, format_size
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class ContextMenuHandler:
    def __init__(self, main_screen):
        self.main = main_screen
        self.config = main_screen.config
        self.file_ops = main_screen.file_ops
        self.dialogs = main_screen.dialogs
    
    def show_context_menu(self):
        """Show context menu for current selection"""
        sel = self.main.active_pane.getSelection()
        if not sel or not sel[0]:
            self.show_general_context_menu()
        else:
            self.show_item_context_menu()
    
    def show_general_context_menu(self):
        """Show context menu for current directory"""
        current_dir = self.main.active_pane.getCurrentDirectory()
        menu_items = [
            ("📂 Open Current Folder", "open"),
            ("📝 Rename Current Folder", "rename_folder"),
            ("📊 Disk Usage Here", "disk_usage"),
            ("🔍 Search in This Folder", "search_here"),
            ("📄 Create New File", "new_file"),
            ("📁 Create New Folder", "new_folder"),
            ("📋 Paste from Clipboard", "paste"),
            ("🌐 Mount Remote Share Here", "mount_here"),
            ("📡 Scan Network Here", "scan_here"),
            ("💾 Set as Bookmark", "bookmark"),
            ("⚙️ Settings for This Folder", "folder_settings"),
        ]
        
        self.main.session.openWithCallback(
            lambda choice: self.handle_general_context_menu(choice, current_dir) if choice else None,
            ChoiceBox,
            title=f"📂 Context: {os.path.basename(current_dir) or 'Root'}",
            list=menu_items
        )
    
    def handle_general_context_menu(self, choice, current_dir):
        """Handle general context menu selection"""
        if not choice:
            return
        
        action = choice[1]
        
        if action == "open":
            self.main.active_pane.refresh()
        elif action == "rename_folder":
            self.rename_folder(current_dir)
        elif action == "disk_usage":
            self.main.dialogs.show_disk_usage(current_dir, self.file_ops)
        elif action == "search_here":
            self.main.dialogs.show_search_dialog(current_dir, self.main.search_engine)
        elif action == "new_file":
            self.main.dialogs.show_create_file_dialog(current_dir, self.file_ops, self.main.update_ui)
        elif action == "new_folder":
            self.main.dialogs.show_create_folder_dialog(current_dir, self.file_ops, self.main.update_ui)
        elif action == "paste":
            self.main.paste_from_clipboard()
        elif action == "mount_here":
            self.main.dialogs.show_mount_dialog(current_dir, self.main.mount_mgr, self.main.active_pane, self.main.update_ui)
        elif action == "scan_here":
            self.main.dialogs.show_network_scan_dialog(self.main.mount_mgr)
        elif action == "bookmark":
            self.main.dialogs.show_bookmark_dialog(current_dir, self.main.bookmarks, self.main.config)
        elif action == "folder_settings":
            self.show_folder_settings(current_dir)
    
    def show_item_context_menu(self):
        """Show context menu for selected item"""
        sel = self.main.active_pane.getSelection()
        if not sel or not sel[0]:
            return
        
        item_path = sel[0]
        is_dir = os.path.isdir(item_path)
        item_name = os.path.basename(item_path)
        
        menu_items = []
        
        # Common actions
        if is_dir:
            menu_items.append(("📂 Open Folder", "open"))
            menu_items.append(("📁 Explore Contents", "explore"))
        else:
            menu_items.append(("📄 Open File", "open"))
        
        menu_items.append(("📝 Rename", "rename"))
        menu_items.append(("🗑️ Delete", "delete"))
        menu_items.append(("📋 Copy", "copy"))
        menu_items.append(("✂️ Cut", "cut"))
        menu_items.append(("📊 Info", "info"))
        
        # File-specific actions
        if not is_dir:
            ext = os.path.splitext(item_path)[1].lower()
            if ext in ['.mp4', '.mkv', '.avi', '.ts', '.mp3', '.flac']:
                menu_items.append(("🎬 Play Media", "play"))
            if ext in ['.txt', '.log', '.conf', '.py', '.sh', '.xml', '.json']:
                menu_items.append(("📝 Edit Text", "edit"))
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                menu_items.append(("🖼️ View Image", "view"))
            if ext in ['.zip', '.tar', '.tar.gz', '.tgz', '.rar']:
                menu_items.append(("📦 Extract Archive", "extract"))
        
        # Additional actions
        menu_items.append(("📁 Copy to Other Pane", "copy_other"))
        menu_items.append(("✂️ Move to Other Pane", "move_other"))
        menu_items.append(("🔒 Set Permissions", "chmod"))
        if not is_dir:
            menu_items.append(("🔐 Calculate Checksum", "checksum"))
        
        menu_items.append(("📄 Create Shortcut", "shortcut"))
        
        # Compress if multiple items selected
        marked = [x for x in self.main.active_pane.list if x[0][3]]
        if len(marked) > 1:
            menu_items.append(("📦 Compress Selected", "compress"))
        
        self.main.session.openWithCallback(
            lambda choice: self.handle_item_context_menu(choice, item_path, is_dir, item_name) if choice else None,
            ChoiceBox,
            title=f"📋 {item_name}",
            list=menu_items
        )
    
    def handle_item_context_menu(self, choice, item_path, is_dir, item_name):
        """Handle item context menu selection"""
        if not choice:
            return
        
        action = choice[1]
        
        if action == "open":
            if is_dir:
                self.main.active_pane.changeDir(item_path)
            else:
                self.main.preview_file()
        elif action == "explore":
            if is_dir:
                self.main.active_pane.changeDir(item_path)
        elif action == "rename":
            self.rename_item(item_path)
        elif action == "delete":
            self.delete_item(item_path, is_dir, item_name)
        elif action == "copy":
            self.copy_item(item_path)
        elif action == "cut":
            self.cut_item(item_path)
        elif action == "info":
            self.main.show_file_info()
        elif action == "play":
            self.main.preview_media()
        elif action == "edit":
            self.edit_text_file(item_path)
        elif action == "view":
            self.main.dialogs.preview_image(item_path, self.file_ops)
        elif action == "extract":
            self.main.dialogs.show_extract_dialog(item_path, self.main.archive_mgr, self.main.active_pane, self.main.update_ui)
        elif action == "copy_other":
            self.copy_to_other_pane(item_path)
        elif action == "move_other":
            self.move_to_other_pane(item_path)
        elif action == "chmod":
            self.main.dialogs.show_permissions_dialog([item_path], self.file_ops)
        elif action == "checksum":
            self.main.dialogs.show_checksum_dialog([item_path], self.file_ops)
        elif action == "shortcut":
            self.create_shortcut(item_path)
        elif action == "compress":
            files = [x[0][0] for x in self.main.active_pane.list if x[0][3]]
            self.main.dialogs.show_archive_dialog(files, self.main.archive_mgr, self.main.active_pane.getCurrentDirectory())
    
    def show_multi_selection_context_menu(self, marked_items):
        """Show context menu for multiple selected items"""
        menu_items = [
            ("📦 Compress Selected Items", "compress_multi"),
            ("📋 Copy Selected Items", "copy_multi"),
            ("✂️ Cut Selected Items", "cut_multi"),
            ("🗑️ Delete Selected Items", "delete_multi"),
            ("📝 Bulk Rename", "bulk_rename_multi"),
            ("🔒 Change Permissions", "chmod_multi"),
            ("📁 Move to Other Pane", "move_other_multi"),
            ("📄 Copy to Other Pane", "copy_other_multi"),
        ]
        
        self.main.session.openWithCallback(
            lambda choice: self.handle_multi_selection_menu(choice, marked_items) if choice else None,
            ChoiceBox,
            title=f"📋 {len(marked_items)} Selected Items",
            list=menu_items
        )
    
    def handle_multi_selection_menu(self, choice, marked_items):
        """Handle multi-selection menu action"""
        if not choice:
            return
        
        action = choice[1]
        file_paths = [item[0][0] for item in marked_items]
        
        if action == "compress_multi":
            self.main.dialogs.show_archive_dialog(file_paths, self.main.archive_mgr, 
                                                 self.main.active_pane.getCurrentDirectory())
        elif action == "copy_multi":
            self.main.clipboard = file_paths
            self.main.clipboard_mode = "copy"
            self.main.update_ui()
            self.main.dialogs.show_message(f"✅ Copied {len(file_paths)} items to clipboard", 
                                          type="info", timeout=2)
        elif action == "cut_multi":
            self.main.clipboard = file_paths
            self.main.clipboard_mode = "cut"
            self.main.update_ui()
            self.main.dialogs.show_message(f"✅ Cut {len(file_paths)} items to clipboard", 
                                          type="info", timeout=2)
        elif action == "delete_multi":
            self.delete_multiple_items(file_paths)
        elif action == "bulk_rename_multi":
            self.main.dialogs.show_bulk_rename_dialog(file_paths, self.file_ops, 
                                                     self.main.active_pane, self.main.update_ui)
        elif action == "chmod_multi":
            self.main.dialogs.show_permissions_dialog(file_paths, self.file_ops)
        elif action == "move_other_multi":
            dest_dir = self.main.inactive_pane.getCurrentDirectory()
            self.main.execute_transfer("mv", file_paths, dest_dir)
        elif action == "copy_other_multi":
            dest_dir = self.main.inactive_pane.getCurrentDirectory()
            self.main.execute_transfer("cp", file_paths, dest_dir)
    
    def show_tools_menu(self):
        """Show tools menu"""
        if self.config.plugins.pilotfs.group_tools_menu.value:
            # GROUPED MENU
            tools = [
                ("═══ FILE OPERATIONS ═══", None),
                ("📁 Create New File/Folder", "create"),
                ("📝 Bulk Rename Tool", "bulkrename"),
                ("🔍 Search Files", "search"),
                ("🔎 Search Content (Grep)", "grep"),
                ("📦 Create Archive (ZIP/TAR)", "archive"),
                ("📂 Extract Archive", "extract"),
                ("🔐 Verify Checksum", "checksum"),
                ("🔒 Set Permissions", "chmod"),
                
                ("═══ VIEW & NAVIGATION ═══", None),
                ("📚 Manage Bookmarks", "bookmarks"),
                ("👁️ File Preview", "preview"),
                ("💾 Storage Selector", "storage"),
                ("📊 Disk Usage Analysis", "diskusage"),
                ("🗑️ View/Restore Trash", "trash"),
                
                ("═══ NETWORK & REMOTE ═══", None),
                ("🗄️ Mount Remote (CIFS)", "mount"),
                ("📡 Scan Network Shares", "scan"),
                ("🔌 Test Network Connection", "ping"),
                ("🌐 Remote File Access", "remote"),
                ("☁️ Cloud Sync", "cloud"),
                
                ("═══ SYSTEM TOOLS ═══", None),
                ("🧹 Smart Cleanup", "clean"),
                ("🔧 Repair Environment", "repair"),
                ("🔗 Repair Picon", "picon"),
                ("📋 View Task Queue", "queue"),
                ("📄 View Log", "log"),
                
                ("═══ SETTINGS ═══", None),
                ("⚙️ Plugin Settings", "cfg"),
            ]
        else:
            # FLAT MENU
            tools = [
                ("📁 Create New File/Folder", "create"),
                ("📚 Manage Bookmarks", "bookmarks"),
                ("📝 Bulk Rename Tool", "bulkrename"),
                ("👁️ File Preview", "preview"),
                ("🔍 Search Files", "search"),
                ("🔎 Search Content (Grep)", "grep"),
                ("📦 Create Archive (ZIP/TAR)", "archive"),
                ("📂 Extract Archive", "extract"),
                ("🔐 Verify Checksum", "checksum"),
                ("🔒 Set Permissions", "chmod"),
                ("📊 Disk Usage Analysis", "diskusage"),
                ("💾 Storage Selector", "storage"),
                ("🗑️ View/Restore Trash", "trash"),
                ("🗄️ Mount Remote (CIFS)", "mount"),
                ("📡 Scan Network Shares", "scan"),
                ("🔌 Test Network Connection", "ping"),
                ("🌐 Remote File Access", "remote"),
                ("☁️ Cloud Sync", "cloud"),
                ("🧹 Smart Cleanup", "clean"),
                ("🔧 Repair Environment", "repair"),
                ("🔗 Repair Picon", "picon"),
                ("📋 View Task Queue", "queue"),
                ("📄 View Log", "log"),
                ("⚙️ Plugin Settings", "cfg"),
            ]
        
        self.main.session.openWithCallback(
            self.tools_callback,
            ChoiceBox,
            title="🔧 PLATINUM TOOLS MENU",
            list=tools
        )
    
    def tools_callback(self, answer):
        """Handle tools menu selection"""
        if not answer or answer[1] is None:
            return
        
        mode = answer[1]
        
        if mode == "cfg":
            self.main.session.open(self.main.dialogs.SetupScreen)
        elif mode == "bookmarks":
            self.main.dialogs.show_bookmark_manager(self.main.bookmarks, self.main.config, 
                                                   self.main.active_pane, self.main.update_ui)
        elif mode == "create":
            self.main.dialogs.show_create_dialog(self.main.active_pane.getCurrentDirectory(), 
                                                self.file_ops, self.main.update_ui)
        elif mode == "bulkrename":
            files = self.main.get_selected_files()
            if len(files) >= 2:
                self.main.dialogs.show_bulk_rename_dialog(files, self.file_ops, 
                                                         self.main.active_pane, self.main.update_ui)
            else:
                self.main.dialogs.show_message("Select at least 2 files for bulk rename!", type="info")
        elif mode == "preview":
            self.main.preview_file()
        elif mode == "search":
            self.main.dialogs.show_search_dialog(self.main.active_pane.getCurrentDirectory(), 
                                                self.main.search_engine)
        elif mode == "archive":
            files = self.main.get_selected_files()
            if files:
                self.main.dialogs.show_archive_dialog(files, self.main.archive_mgr, 
                                                     self.main.active_pane.getCurrentDirectory())
            else:
                self.main.dialogs.show_message("No files selected!", type="info")
        elif mode == "extract":
            sel = self.main.active_pane.getSelection()
            if sel and sel[0]:
                self.main.dialogs.show_extract_dialog(sel[0], self.main.archive_mgr, 
                                                     self.main.active_pane, self.main.update_ui)
            else:
                self.main.dialogs.show_message("No archive selected!", type="info")
        elif mode == "trash":
            self.main.dialogs.show_trash_manager(self.file_ops, self.main.active_pane, self.main.update_ui)
        elif mode == "mount":
            self.main.dialogs.show_mount_dialog(self.main.active_pane.getCurrentDirectory(), 
                                               self.main.mount_mgr, self.main.active_pane, self.main.update_ui)
        elif mode == "scan":
            self.main.dialogs.show_network_scan_dialog(self.main.mount_mgr)
        elif mode == "ping":
            self.main.dialogs.show_ping_dialog(self.main.mount_mgr)
        elif mode == "cloud":
            self.main.dialogs.show_cloud_sync_dialog()
        elif mode == "clean":
            self.main.dialogs.show_cleanup_dialog()
        elif mode == "picon":
            self.main.dialogs.show_picon_repair_dialog()
        elif mode == "chmod":
            files = self.main.get_selected_files()
            if files:
                self.main.dialogs.show_permissions_dialog(files, self.file_ops)
            else:
                self.main.dialogs.show_message("No files selected!", type="info")
        elif mode == "diskusage":
            self.main.dialogs.show_disk_usage(self.main.active_pane.getCurrentDirectory(), self.file_ops)
        elif mode == "log":
            self.main.dialogs.show_log_viewer()
        elif mode == "repair":
            self.main.dialogs.show_repair_dialog()
        elif mode == "grep":
            self.main.dialogs.show_content_search_dialog(self.main.active_pane.getCurrentDirectory(), 
                                                        self.main.search_engine)
        elif mode == "checksum":
            files = [f for f in self.main.get_selected_files() if os.path.isfile(f)]
            if files:
                self.main.dialogs.show_checksum_dialog(files, self.file_ops)
            else:
                self.main.dialogs.show_message("Please select files (not folders)", type="info")
        elif mode == "queue":
            self.main.dialogs.show_queue_dialog(self.main.operation_in_progress, 
                                               self.main.operation_current, self.main.operation_total)
        elif mode == "remote":
            self.main.dialogs.show_remote_access_dialog(self.main.remote_mgr, self.main.mount_mgr, 
                                                       self.main.active_pane, self.main.update_ui)
        elif mode == "storage":
            self.main.show_storage_selector()
    
    # Helper methods
    def rename_folder(self, folder_path):
        """Rename current folder"""
        current_name = os.path.basename(folder_path)
        
        self.main.session.openWithCallback(
            lambda new_name: self.execute_rename_folder(folder_path, new_name) if new_name else None,
            VirtualKeyBoard,
            title="Enter new folder name:",
            text=current_name
        )
    
    def execute_rename_folder(self, old_path, new_name):
        """Execute folder rename"""
        try:
            new_path = self.file_ops.rename(old_path, new_name)
            self.main.active_pane.changeDir(os.path.dirname(old_path))
            self.main.active_pane.refresh()
            self.main.update_ui()
            self.main.dialogs.show_message(f"✅ Folder renamed to: {new_name}", type="info")
        except Exception as e:
            self.main.dialogs.show_message(f"Rename failed:\n{e}", type="error")
    
    def rename_item(self, item_path):
        """Rename selected item"""
        current_name = os.path.basename(item_path)
        
        self.main.session.openWithCallback(
            lambda new_name: self.execute_rename_item(item_path, new_name) if new_name else None,
            VirtualKeyBoard,
            title="Enter new name:",
            text=current_name
        )
    
    def execute_rename_item(self, old_path, new_name):
        """Execute item rename"""
        try:
            new_path = self.file_ops.rename(old_path, new_name)
            self.main.active_pane.refresh()
            self.main.update_ui()
            self.main.dialogs.show_message(f"✅ Renamed to: {new_name}", type="info")
        except Exception as e:
            self.main.dialogs.show_message(f"Rename failed:\n{e}", type="error")
    
    def delete_item(self, item_path, is_dir, item_name):
        """Delete selected item"""
        item_type = "folder" if is_dir else "file"
        
        self.main.dialogs.show_confirmation(
            f"Delete {item_type} '{item_name}'?\n\nThis cannot be undone!",
            lambda res: self.execute_delete_item(res, item_path, item_name, item_type)
        )
    
    def execute_delete_item(self, confirmed, item_path, item_name, item_type):
        """Execute item deletion"""
        if not confirmed:
            return
        
        try:
            self.file_ops.delete(item_path)
            self.main.active_pane.refresh()
            self.main.update_ui()
            
            if self.config.plugins.pilotfs.trash_enabled.value == "yes":
                msg = f"✅ Moved to trash: {item_name}"
            else:
                msg = f"✅ Permanently deleted: {item_name}"
            
            self.main.dialogs.show_message(msg, type="info")
        except Exception as e:
            self.main.dialogs.show_message(f"Delete failed:\n{e}", type="error")
    
    def delete_multiple_items(self, file_paths):
        """Delete multiple selected items"""
        item_type = "items"
        
        self.main.dialogs.show_confirmation(
            f"Delete {len(file_paths)} {item_type}?\n\nThis cannot be undone!",
            lambda res: self.execute_delete_multiple(res, file_paths) if res else None
        )
    
    def execute_delete_multiple(self, confirmed, file_paths):
        """Execute deletion of multiple items"""
        if not confirmed:
            return
        
        success = 0
        errors = []
        
        for item_path in file_paths:
            try:
                self.file_ops.delete(item_path)
                success += 1
            except Exception as e:
                errors.append(f"{os.path.basename(item_path)}: {str(e)[:30]}")
        
        msg = f"✅ Deleted: {success} items\n"
        if errors:
            msg += f"\n❌ Failed: {len(errors)}\n"
            msg += "\n".join(errors[:3])
            if len(errors) > 3:
                msg += f"\n... and {len(errors) - 3} more"
        
        self.main.active_pane.refresh()
        self.main.update_ui()
        self.main.dialogs.show_message(msg, type="info")
    
    def copy_item(self, item_path):
        """Copy item to clipboard"""
        self.main.clipboard = [item_path]
        self.main.clipboard_mode = "copy"
        self.main.update_ui()
        self.main.dialogs.show_message(f"✅ Copied to clipboard: {os.path.basename(item_path)}", 
                                      type="info", timeout=2)
    
    def cut_item(self, item_path):
        """Cut item to clipboard"""
        self.main.clipboard = [item_path]
        self.main.clipboard_mode = "cut"
        self.main.update_ui()
        self.main.dialogs.show_message(f"✅ Cut to clipboard: {os.path.basename(item_path)}", 
                                      type="info", timeout=2)
    
    def copy_to_other_pane(self, item_path):
        """Copy item to other pane"""
        dest_dir = self.main.inactive_pane.getCurrentDirectory()
        
        self.main.dialogs.show_confirmation(
            f"Copy to:\n{dest_dir}?",
            lambda res: self.main.execute_transfer("cp", [item_path], dest_dir) if res else None
        )
    
    def move_to_other_pane(self, item_path):
        """Move item to other pane"""
        dest_dir = self.main.inactive_pane.getCurrentDirectory()
        
        self.main.dialogs.show_confirmation(
            f"Move to:\n{dest_dir}?",
            lambda res: self.main.execute_transfer("mv", [item_path], dest_dir) if res else None
        )
    
    def edit_text_file(self, file_path):
        """Edit text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(5000)
            
            preview = f"📝 Edit: {os.path.basename(file_path)}\n\n"
            preview += content[:2000]
            if len(content) > 2000:
                preview += "\n\n... (file truncated)"
            
            preview += "\n\nEdit this file? (Not implemented in this version)"
            
            self.main.dialogs.show_message(preview, type="info")
        except Exception as e:
            self.main.dialogs.show_message(f"Cannot edit file:\n{e}", type="error")
    
    def create_shortcut(self, item_path):
        """Create shortcut to item"""
        self.main.dialogs.show_message(
            "Shortcut creation would be implemented here.\n\n"
            "This would create a symbolic link to the selected item.",
            type="info"
        )
    
    def show_folder_settings(self, folder_path):
        """Folder-specific settings"""
        try:
            info = self.file_ops.get_file_info(folder_path)
            if info:
                msg = f"📁 Folder Settings\n\n"
                msg += f"Path: {info['path']}\n"
                msg += f"Permissions: {info['permissions']}\n"
                msg += f"Owner: {info['owner']}\n"
                msg += f"Group: {info['group']}\n"
                msg += f"Modified: {info['modified']}\n"
                if 'item_count' in info:
                    msg += f"Items: {info['item_count']}\n"
                
                self.main.dialogs.show_message(msg, type="info")
        except Exception as e:
            self.main.dialogs.show_message(f"Cannot read folder info:\n{e}", type="error")