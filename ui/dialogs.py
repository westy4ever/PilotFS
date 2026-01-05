from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
import os
import subprocess
import threading
import hashlib
from datetime import datetime

from ..ui.setup_screen import PilotFSSetup
from ..utils.formatters import format_size, get_file_icon
from ..utils.logging_config import get_logger
from ..constants import TRASH_PATH, LOG_FILE

logger = get_logger(__name__)

class Dialogs:
    def __init__(self, session):
        self.session = session
    
    # Basic dialogs
    def show_message(self, text, type="info", timeout=0):
        """Show message dialog"""
        if type == "info":
            mtype = MessageBox.TYPE_INFO
        elif type == "warning":
            mtype = MessageBox.TYPE_WARNING
        elif type == "error":
            mtype = MessageBox.TYPE_ERROR
        else:
            mtype = MessageBox.TYPE_INFO
        
        if timeout > 0:
            self.session.open(MessageBox, text, mtype, timeout=timeout)
        else:
            self.session.open(MessageBox, text, mtype)
    
    def show_confirmation(self, text, callback):
        """Show confirmation dialog"""
        self.session.openWithCallback(callback, MessageBox, text, MessageBox.TYPE_YESNO)
    
    def show_input(self, title, text="", callback=None):
        """Show input dialog"""
        self.session.openWithCallback(callback, VirtualKeyBoard, title=title, text=text)
    
    def show_choice(self, title, choices, callback=None):
        """Show choice dialog"""
        self.session.openWithCallback(callback, ChoiceBox, title=title, list=choices)
    
    # File operations dialogs
    def show_create_dialog(self, current_dir, file_ops, update_callback):
        """Show create file/folder dialog"""
        choices = [
            ("Create New Folder", "folder"),
            ("Create New File", "file")
        ]
        
        self.show_choice(
            "Create New",
            choices,
            lambda choice: self._handle_create_choice(choice, current_dir, file_ops, update_callback) if choice else None
        )
    
    def _handle_create_choice(self, choice, current_dir, file_ops, update_callback):
        """Handle create choice"""
        create_type = choice[1]
        
        if create_type == "folder":
            title = "Enter folder name:"
            default = "new_folder"
        else:
            title = "Enter file name:"
            default = "new_file.txt"
        
        self.show_input(
            title,
            default,
            lambda name: self._execute_create(name, create_type, current_dir, file_ops, update_callback) if name else None
        )
    
    def _execute_create(self, name, create_type, current_dir, file_ops, update_callback):
        """Execute creation"""
        try:
            if create_type == "folder":
                new_path = file_ops.create_directory(current_dir, name)
                msg = "Folder created: " + name
            else:
                new_path = file_ops.create_file(current_dir, name)
                msg = "File created: " + name
            
            update_callback()
            self.show_message(msg, type="info", timeout=2)
        except Exception as e:
            self.show_message("Creation failed: " + str(e), type="error")
    
    def show_create_file_dialog(self, current_dir, file_ops, update_callback):
        """Show create file dialog"""
        self.show_input(
            "Enter file name:",
            "new_file.txt",
            lambda name: self._execute_create(name, "file", current_dir, file_ops, update_callback) if name else None
        )
    
    def show_create_folder_dialog(self, current_dir, file_ops, update_callback):
        """Show create folder dialog"""
        self.show_input(
            "Enter folder name:",
            "new_folder",
            lambda name: self._execute_create(name, "folder", current_dir, file_ops, update_callback) if name else None
        )
    
    def show_transfer_dialog(self, files, destination, callback):
        """Show transfer dialog"""
        num_files = len([x for x in files if os.path.isfile(x)])
        num_dirs = len([x for x in files if os.path.isdir(x)])
        
        choices = [
            ("Copy %d items (%d folders, %d files)" % (len(files), num_dirs, num_files), "cp"),
            ("Move %d items (%d folders, %d files)" % (len(files), num_dirs, num_files), "mv")
        ]
        
        self.show_choice(
            "Transfer to: " + destination,
            choices,
            lambda choice: callback(choice[1], files, destination) if choice else None
        )
    
    def show_permissions_dialog(self, files, file_ops):
        """Show permissions dialog"""
        choices = [
            ("755 (rwxr-xr-x) - Executable", "755"),
            ("644 (rw-r--r--) - Standard file", "644"),
            ("777 (rwxrwxrwx) - Full access", "777"),
            ("600 (rw-------) - Owner only", "600")
        ]
        
        self.show_choice(
            "Set permissions for %d items" % len(files),
            choices,
            lambda choice: self._execute_change_permissions(choice[1], files, file_ops) if choice else None
        )
    
    def _execute_change_permissions(self, mode_str, files, file_ops):
        """Execute permission change"""
        try:
            for file_path in files:
                file_ops.change_permissions(file_path, mode_str)
            
            self.show_message("Permissions changed to %s for %d items" % (mode_str, len(files)), type="info")
        except Exception as e:
            self.show_message("Change permissions failed: " + str(e), type="error")
    
    def show_checksum_dialog(self, files, file_ops):
        """Show checksum dialog"""
        choices = [
            ("Calculate MD5", "md5"),
            ("Calculate SHA1", "sha1"),
            ("Calculate SHA256", "sha256")
        ]
        
        self.show_choice(
            "Checksum for %d file(s)" % len(files),
            choices,
            lambda choice: self._execute_checksum(choice[1], files, file_ops) if choice else None
        )
    
    def _execute_checksum(self, algorithm, files, file_ops):
        """Execute checksum calculation"""
        def checksum_thread():
            results = []
            
            for file_path in files:
                try:
                    if algorithm == "md5":
                        hasher = hashlib.md5()
                    elif algorithm == "sha1":
                        hasher = hashlib.sha1()
                    else:
                        hasher = hashlib.sha256()
                    
                    with open(file_path, 'rb') as f:
                        while True:
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            hasher.update(chunk)
                    
                    checksum = hasher.hexdigest()
                    results.append((os.path.basename(file_path), checksum))
                    
                except Exception as e:
                    results.append((os.path.basename(file_path), "ERROR: " + str(e)))
            
            msg = algorithm.upper() + " Checksums:\n\n"
            for name, checksum in results:
                msg += name + ":\n" + checksum + "\n\n"
            
            self.show_message(msg, type="info")
        
        threading.Thread(target=checksum_thread, daemon=True).start()
    
    # Archive dialogs
    def show_archive_dialog(self, files, archive_mgr, current_dir):
        """Show archive creation dialog"""
        choices = [
            ("Create ZIP archive", "zip"),
            ("Create TAR.GZ archive", "tar.gz")
        ]
        
        self.show_choice(
            "Archive %d items" % len(files),
            choices,
            lambda choice: self._handle_archive_choice(choice, files, archive_mgr, current_dir) if choice else None
        )
    
    def _handle_archive_choice(self, choice, files, archive_mgr, current_dir):
        """Handle archive choice"""
        archive_type = choice[1]
        default_name = "archive_" + datetime.now().strftime('%Y%m%d_%H%M%S')
        
        self.show_input(
            "Archive name (" + archive_type.upper() + "):",
            default_name,
            lambda name: self._execute_create_archive(name, archive_type, files, archive_mgr, current_dir) if name else None
        )
    
    def _execute_create_archive(self, name, archive_type, files, archive_mgr, current_dir):
        """Execute archive creation"""
        try:
            if archive_type == "zip" and not name.endswith(".zip"):
                name += ".zip"
            elif archive_type == "tar.gz" and not name.endswith(".tar.gz"):
                name += ".tar.gz"
            
            archive_path = os.path.join(current_dir, name)
            archive_mgr.create_archive(files, archive_path, archive_type)
            
            self.show_message("Archive created: " + name, type="info")
        except Exception as e:
            self.show_message("Archive creation failed: " + str(e), type="error")
    
    def show_extract_dialog(self, archive_path, archive_mgr, filelist, update_callback):
        """Show extract archive dialog"""
        archive_name = os.path.basename(archive_path)
        dest_dir = os.path.join(os.path.dirname(archive_path), 
                               os.path.splitext(archive_name)[0].replace('.tar', ''))
        
        self.show_confirmation(
            "Extract '" + archive_name + "' to:\n" + dest_dir + "?",
            lambda res: self._execute_extract(res, archive_path, dest_dir, archive_mgr, filelist, update_callback)
        )
    
    def _execute_extract(self, confirmed, archive_path, dest_dir, archive_mgr, filelist, update_callback):
        """Execute archive extraction"""
        if not confirmed:
            return
        
        def extract_thread():
            try:
                archive_mgr.extract_archive(archive_path, dest_dir)
                filelist.refresh()
                update_callback()
                self.show_message("Extracted to: " + dest_dir, type="info")
            except Exception as e:
                self.show_message("Extraction failed: " + str(e), type="error")
        
        threading.Thread(target=extract_thread, daemon=True).start()
    
    # Search dialogs
    def show_search_dialog(self, directory, search_engine):
        """Show file search dialog"""
        self.show_input(
            "Search files (wildcards: * ?):",
            "",
            lambda pattern: self._execute_file_search(pattern, directory, search_engine) if pattern else None
        )
    
    def _execute_file_search(self, pattern, directory, search_engine):
        """Execute file search"""
        def search_thread():
            try:
                results = search_engine.search_files(directory, pattern, recursive=True, max_results=100)
                
                if results:
                    result_text = "Found %d matches:\n\n" % len(results)
                    for item in results[:20]:
                        icon = "Folder" if item['is_dir'] else "File"
                        result_text += icon + " " + item['name'] + "\n"
                    
                    if len(results) > 20:
                        result_text += "\n... and %d more" % (len(results) - 20)
                    
                    self.show_message(result_text, type="info")
                else:
                    self.show_message("No files found matching: " + pattern, type="info")
                    
            except Exception as e:
                self.show_message("Search failed: " + str(e), type="error")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def show_content_search_dialog(self, directory, search_engine):
        """Show content search dialog"""
        self.show_input(
            "Search text in files:",
            "",
            lambda pattern: self._execute_content_search(pattern, directory, search_engine) if pattern else None
        )
    
    def _execute_content_search(self, pattern, directory, search_engine):
        """Execute content search"""
        def search_thread():
            try:
                results = search_engine.search_content(directory, pattern, recursive=True, max_results=50)
                
                if results:
                    result_text = "Found '%s' in %d file(s):\n\n" % (pattern, len(results))
                    for item in results[:20]:
                        result_text += "File: " + item['name'] + "\n"
                    
                    if len(results) > 20:
                        result_text += "\n... and %d more" % (len(results) - 20)
                    
                    self.show_message(result_text, type="info")
                else:
                    self.show_message("No files contain: " + pattern, type="info")
                    
            except Exception as e:
                self.show_message("Search failed: " + str(e), type="error")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    # Preview dialogs
    def preview_file(self, file_path, file_ops, config):
        """Preview file contents"""
        if os.path.isdir(file_path):
            self.show_message("Cannot preview directory!\n\nPress OK to enter folder.", type="info")
            return
        
        try:
            size = file_ops.get_file_size(file_path)
            max_size = int(config.plugins.pilotfs.preview_size.value) * 1024
            if size > max_size:
                self.show_message(
                    "File too large to preview!\n\nSize: " + format_size(size) + "\nLimit: " + format_size(max_size),
                    type="info"
                )
                return
        except:
            pass
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.txt', '.log', '.conf', '.cfg', '.ini', '.xml', '.json', '.py', '.sh', '.md']:
            self._preview_text_file(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            self._preview_image(file_path, file_ops)
        else:
            self._preview_binary(file_path)
    
    def _preview_text_file(self, file_path):
        """Preview text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 50:
                        break
                    lines.append(line)
                content = ''.join(lines)
            
            preview = "File: " + os.path.basename(file_path) + "\n"
            preview += "=" * 40 + "\n\n"
            preview += content
            
            if len(content.splitlines()) == 50:
                preview += "\n\n... (file continues)"
            
            self.show_message(preview, type="info")
        except Exception as e:
            self.show_message("Cannot preview file: " + str(e), type="error")
    
    def _preview_image(self, file_path, file_ops):
        """Preview image file"""
        try:
            info = file_ops.get_file_info(file_path)
            
            preview = "Image Preview\n\n"
            preview += "File: " + info['name'] + "\n"
            preview += "Size: " + info['size_formatted'] + "\n"
            preview += "Type: " + os.path.splitext(file_path)[1].upper() + "\n"
            preview += "Modified: " + info['modified'].strftime('%Y-%m-%d %H:%M') + "\n\n"
            preview += "Image preview requires media viewer.\n"
            preview += "Use file browser to open image."
            
            self.show_message(preview, type="info")
        except Exception as e:
            self.show_message("Cannot preview image: " + str(e), type="error")
    
    def preview_image(self, file_path, file_ops):
        """Preview image (public wrapper)"""
        self._preview_image(file_path, file_ops)
    
    def _preview_binary(self, file_path):
        """Preview binary file"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read(256)
            
            preview = "Binary Preview: " + os.path.basename(file_path) + "\n"
            preview += "=" * 40 + "\n\n"
            
            for i in range(0, min(len(data), 128), 16):
                chunk = data[i:i+16]
                hex_str = ' '.join('%02x' % b for b in chunk)
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                preview += "%04x  %-48s  %s\n" % (i, hex_str, ascii_str)
            
            if len(data) > 128:
                preview += "\n... (showing first 128 bytes)"
            
            self.show_message(preview, type="info")
        except Exception as e:
            self.show_message("Cannot preview file: " + str(e), type="error")
    
    def preview_media(self, file_path, config):
        """Preview media file"""
        try:
            info = "Media File: " + os.path.basename(file_path) + "\n\n"
            info += "Path: " + file_path + "\n\n"
            info += "Media playback would start here.\n"
            info += "Press PLAY button to play with external player."
            
            self.show_message(info, type="info")
        except Exception as e:
            self.show_message("Media preview error: " + str(e), type="error")
    
    # System dialogs
    def show_disk_usage(self, directory, file_ops):
        """Show disk usage analysis"""
        def analyze_thread():
            try:
                entries = []
                total_size = 0
                
                try:
                    with os.scandir(directory) as it:
                        for entry in it:
                            try:
                                size = file_ops.get_file_size(entry.path, use_cache=True)
                                entries.append({
                                    'name': entry.name,
                                    'size': size,
                                    'is_dir': entry.is_dir()
                                })
                                total_size += size
                            except:
                                pass
                except:
                    pass
                
                entries.sort(key=lambda x: x['size'], reverse=True)
                
                result = "Disk Usage Analysis\n" + directory + "\n\n"
                result += "Total: " + format_size(total_size) + "\n\n"
                
                for item in entries[:15]:
                    percent = (item['size'] / total_size * 100) if total_size > 0 else 0
                    icon = "Folder" if item['is_dir'] else "File"
                    result += "%s %s: %s (%.1f%%)\n" % (icon, item['name'], format_size(item['size']), percent)
                
                if len(entries) > 15:
                    result += "\n... and %d more items" % (len(entries) - 15)
                
                self.show_message(result, type="info")
            except Exception as e:
                self.show_message("Analysis failed: " + str(e), type="error")
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    # Storage selector
    def show_storage_selector(self, change_dir_callback, update_callback):
        """Show storage selector"""
        choices = []
        
        storage_locations = [
            ("Internal Hard Disk", "/media/hdd"),
            ("USB Storage", "/media/usb"),
            ("USB 1", "/media/usb1"),
            ("USB 2", "/media/usb2"),
            ("Network Mounts", "/media/net"),
            ("Root Filesystem", "/"),
            ("System Temp", "/tmp"),
            ("Flash Memory", "/media/mmc"),
            ("SD Card", "/media/sdcard"),
        ]
        
        for label, path in storage_locations:
            if os.path.isdir(path):
                try:
                    st = os.statvfs(path)
                    free_gb = (st.f_bavail * st.f_frsize) / (1024**3)
                    display = "%s (%.1fGB free)" % (label, free_gb)
                    choices.append((display, path))
                except:
                    choices.append((label, path))
        
        if choices:
            self.show_choice(
                "Select Storage Location",
                choices,
                lambda choice: self._select_storage(choice, change_dir_callback, update_callback) if choice else None
            )
        else:
            self.show_message("No storage devices found!", type="info")
    
    def _select_storage(self, choice, change_dir_callback, update_callback):
        """Select storage location"""
        path = choice[1]
        if os.path.isdir(path):
            change_dir_callback(path)
            update_callback()
        else:
            self.show_message("Storage not accessible: " + path, type="error")
    
    # Bookmark dialogs
    def show_bookmark_dialog(self, path, bookmarks, config):
        """Show bookmark dialog"""
        self.show_input(
            "Bookmark number (1-9):",
            "1",
            lambda num_str: self._set_bookmark(num_str, path, bookmarks, config) if num_str else None
        )
    
    def _set_bookmark(self, num_str, path, bookmarks, config):
        """Set bookmark"""
        try:
            num = int(num_str)
            if 1 <= num <= 9:
                bookmarks[str(num)] = path
                config.save_bookmarks(bookmarks)
                self.show_message("Bookmark %d set to: %s" % (num, os.path.basename(path)), type="info", timeout=2)
            else:
                self.show_message("Please enter a number 1-9", type="error")
        except ValueError:
            self.show_message("Invalid number!", type="error")
    
    def show_bookmark_manager(self, bookmarks, config, filelist, update_callback):
        """Show bookmark manager"""
        if not bookmarks:
            self.show_message("No bookmarks saved.\n\nPress 1-9 in any folder to create a bookmark!", type="info")
            return
        
        bookmark_list = [("Bookmark %s: %s" % (k, v), k) for k, v in sorted(bookmarks.items())]
        bookmark_list.append(("Clear All Bookmarks", "clear"))
        
        self.show_choice(
            "Manage Bookmarks",
            bookmark_list,
            lambda choice: self._handle_bookmark_action(choice, bookmarks, config, filelist, update_callback) if choice else None
        )
    
    def _handle_bookmark_action(self, choice, bookmarks, config, filelist, update_callback):
        """Handle bookmark action"""
        key = choice[1]
        if key == "clear":
            self.show_confirmation(
                "Clear all bookmarks?",
                lambda res: self._clear_bookmarks(res, bookmarks, config) if res else None
            )
        else:
            if key in bookmarks:
                path = bookmarks[key]
                if os.path.isdir(path):
                    filelist.changeDir(path)
                    update_callback()
                else:
                    self.show_message("Bookmark path not found: " + path, type="error")
    
    def _clear_bookmarks(self, confirmed, bookmarks, config):
        """Clear bookmarks"""
        if not confirmed:
            return
        
        bookmarks.clear()
        config.save_bookmarks(bookmarks)
        self.show_message("All bookmarks cleared", type="info", timeout=2)
    
    # Trash management
    def show_trash_manager(self, file_ops, filelist, update_callback):
        """Show trash manager"""
        try:
            if not os.path.exists(TRASH_PATH):
                self.show_message("Trash is empty", type="info")
                return
            
            items = os.listdir(TRASH_PATH)
            if not items:
                self.show_message("Trash is empty", type="info")
                return
            
            choices = [
                ("Open Trash Folder (%d items)" % len(items), "open"),
                ("Empty Trash (Permanent Delete)", "empty"),
                ("Restore All Items", "restore_all")
            ]
            
            self.show_choice(
                "Trash Management",
                choices,
                lambda choice: self._handle_trash_action(choice, file_ops, filelist, update_callback) if choice else None
            )
        except Exception as e:
            self.show_message("Trash error: " + str(e), type="error")
    
    def _handle_trash_action(self, choice, file_ops, filelist, update_callback):
        """Handle trash action"""
        action = choice[1]
        
        if action == "open":
            filelist.changeDir(TRASH_PATH)
            update_callback()
        elif action == "empty":
            self.show_confirmation(
                "Permanently delete all items in trash?",
                lambda res: self._empty_trash(res, file_ops, filelist, update_callback) if res else None
            )
        elif action == "restore_all":
            self.show_confirmation(
                "Restore all items from trash?",
                lambda res: self._restore_all_from_trash(res, file_ops, filelist, update_callback) if res else None
            )
    
    def _empty_trash(self, confirmed, file_ops, filelist, update_callback):
        """Empty trash"""
        if not confirmed:
            return
        
        try:
            file_ops.empty_trash()
            filelist.refresh()
            update_callback()
            self.show_message("Trash emptied successfully", type="info")
        except Exception as e:
            self.show_message("Empty trash failed: " + str(e), type="error")
    
    def _restore_all_from_trash(self, confirmed, file_ops, filelist, update_callback):
        """Restore all from trash"""
        if not confirmed:
            return
        
        try:
            items = os.listdir(TRASH_PATH)
            restored = 0
            failed = 0
            
            for item in items:
                try:
                    trash_item = os.path.join(TRASH_PATH, item)
                    file_ops.restore_from_trash(trash_item)
                    restored += 1
                except:
                    failed += 1
            
            msg = "Restored: %d items" % restored
            if failed > 0:
                msg += "\nFailed: %d items" % failed
            
            filelist.refresh()
            update_callback()
            self.show_message(msg, type="info")
        except Exception as e:
            self.show_message("Restore failed: " + str(e), type="error")
    
    # Network dialogs - stubs for now
    def show_mount_dialog(self, mount_point, mount_mgr, filelist, update_callback):
        """Show mount dialog"""
        self.show_message("Mount remote - feature coming soon", type="info")
    
    def show_network_scan_dialog(self, mount_mgr):
        """Show network scan dialog"""
        self.show_message("Network scan - feature coming soon", type="info")
    
    def show_ping_dialog(self, mount_mgr):
        """Show ping dialog"""
        self.show_message("Ping test - feature coming soon", type="info")
    
    def show_remote_access_dialog(self, remote_mgr, mount_mgr, filelist, update_callback):
        """Show remote access dialog"""
        self.show_message("Remote access - feature coming soon", type="info")
    
    # System tools dialogs - stubs for now
    def show_cleanup_dialog(self):
        """Show cleanup dialog"""
        self.show_message("System cleanup - feature coming soon", type="info")
    
    def show_picon_repair_dialog(self):
        """Show picon repair dialog"""
        self.show_message("Picon repair - feature coming soon", type="info")
    
    def show_cloud_sync_dialog(self):
        """Show cloud sync dialog"""
        self.show_message("Cloud sync - feature coming soon", type="info")
    
    def show_repair_dialog(self):
        """Show repair dialog"""
        self.show_message("System repair - feature coming soon", type="info")
    
    def show_queue_dialog(self, operation_in_progress, current, total):
        """Show queue dialog"""
        if operation_in_progress:
            msg = "Operation in progress:\n\nProgress: %s / %s\n\nPlease wait for current operation to complete." % (current if current is not None else 0, total if total is not None else 0)
        else:
            msg = "No operations currently running.\n\nSystem is idle."
        
        self.show_message(msg, type="info")
    
    def show_log_viewer(self):
        """Show log viewer"""
        try:
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                recent = ''.join(lines[-30:])
                self.show_message(recent, type="info")
        except Exception as e:
            self.show_message("Could not read log: " + str(e), type="error")
    
    # Bulk rename - stub for now
    def show_bulk_rename_dialog(self, files, file_ops, filelist, update_callback):
        """Show bulk rename dialog"""
        self.show_message("Bulk rename - feature coming soon\n\nThis feature requires VirtualKeyBoard", type="info")
    
    # Property for SetupScreen
    @property
    def SetupScreen(self):
        """Get setup screen class"""
        return PilotFSSetup

    # Network dialogs - FULL implementations
    def show_mount_dialog(self, mount_point, mount_mgr, filelist, update_callback):
        """Show mount dialog"""
        self.show_input(
            "Enter Remote IP:",
            "",
            lambda ip: self._execute_mount(ip, mount_point, mount_mgr, filelist, update_callback) if ip else None
        )
    
    def _execute_mount(self, ip, mount_point, mount_mgr, filelist, update_callback):
        """Execute mount"""
        def mount_thread():
            try:
                success, message = mount_mgr.mount_cifs(ip, "Harddisk", mount_point)
                if success:
                    filelist.changeDir(mount_point)
                    filelist.refresh()
                    update_callback()
                    self.show_message("Success: " + message, type="info", timeout=3)
                else:
                    self.show_message("Error: " + message, type="error")
            except Exception as e:
                self.show_message("Mount error: " + str(e), type="error")
        
        threading.Thread(target=mount_thread, daemon=True).start()
    
    def show_network_scan_dialog(self, mount_mgr):
        """Show network scan dialog"""
        self.show_input(
            "Enter IP to scan:",
            "",
            lambda ip: self._execute_network_scan(ip, mount_mgr) if ip else None
        )
    
    def _execute_network_scan(self, ip, mount_mgr):
        """Execute network scan"""
        def scan_thread():
            try:
                success, result = mount_mgr.scan_network_shares(ip)
                if success:
                    msg = "Network Scan Results for %s:\n\n" % ip
                    for share in result:
                        msg += "Share: %s (%s)\n" % (share['name'], share['type'])
                    self.show_message(msg, type="info")
                else:
                    self.show_message("Scan failed: " + result, type="error")
            except Exception as e:
                self.show_message("Scan error: " + str(e), type="error")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def show_ping_dialog(self, mount_mgr):
        """Show ping dialog"""
        self.show_input(
            "Enter IP to ping:",
            "192.168.1.1",
            lambda ip: self._execute_ping(ip, mount_mgr) if ip else None
        )
    
    def _execute_ping(self, ip, mount_mgr):
        """Execute ping"""
        def ping_thread():
            try:
                success, message = mount_mgr.test_ping(ip)
                if success:
                    self.show_message("Success: " + message, type="info")
                else:
                    self.show_message("Error: " + message, type="error")
            except Exception as e:
                self.show_message("Ping error: " + str(e), type="error")
        
        threading.Thread(target=ping_thread, daemon=True).start()
    
    def show_remote_access_dialog(self, remote_mgr, mount_mgr, filelist, update_callback):
        """Show remote access dialog"""
        choices = [
            ("Manage Saved Connections", "manage"),
            ("FTP Client", "ftp"),
            ("SFTP Client (SSH)", "sftp"),
            ("WebDAV Client", "webdav"),
            ("Test Connection", "test"),
        ]
        
        self.show_choice(
            "Remote File Access",
            choices,
            lambda choice: self._handle_remote_access(choice, remote_mgr, mount_mgr, filelist, update_callback) if choice else None
        )
    
    def _handle_remote_access(self, choice, remote_mgr, mount_mgr, filelist, update_callback):
        """Handle remote access selection"""
        action = choice[1]
        
        if action == "manage":
            self._manage_remote_connections(remote_mgr)
        elif action == "ftp":
            self.show_message("FTP Client - Use Tools menu for specific operations", type="info")
        elif action == "sftp":
            self.show_message("SFTP requires sshpass to be installed:\n\nopkg install sshpass", type="info")
        elif action == "webdav":
            self.show_message("WebDAV requires curl to be installed:\n\nopkg install curl", type="info")
        elif action == "test":
            self.show_ping_dialog(mount_mgr)
    
    def _manage_remote_connections(self, remote_mgr):
        """Manage remote connections"""
        connections = remote_mgr.list_connections()
        
        if not connections:
            choices = [("Add New Connection", "add")]
        else:
            choices = []
            for name, conn in connections.items():
                display = "%s (%s://%s)" % (name, conn['type'], conn['host'])
                choices.append((display, name))
            choices.append(("Add New Connection", "add"))
            choices.append(("Clear All Connections", "clear"))
        
        self.show_choice(
            "Manage Remote Connections",
            choices,
            lambda choice: self._handle_connection_management(choice, remote_mgr) if choice else None
        )
    
    def _handle_connection_management(self, choice, remote_mgr):
        """Handle connection management"""
        action = choice[1]
        
        if action == "add":
            self.show_message("Use Tools -> Mount Remote for adding connections", type="info")
        elif action == "clear":
            self.show_confirmation(
                "Clear all saved connections?",
                lambda res: self._clear_connections(res, remote_mgr) if res else None
            )
    
    def _clear_connections(self, confirmed, remote_mgr):
        """Clear all connections"""
        if not confirmed:
            return
        
        try:
            remote_mgr.clear_connections()
            self.show_message("All connections cleared!", type="info")
        except Exception as e:
            self.show_message("Failed to clear connections: " + str(e), type="error")
    
    # System tools dialogs - FULL implementations
    def show_cleanup_dialog(self):
        """Show cleanup dialog"""
        self.show_confirmation(
            "Cleanup log files?\n\nThis will remove old log files from system.",
            lambda res: self._execute_cleanup(res) if res else None
        )
    
    def _execute_cleanup(self, confirmed):
        """Execute cleanup"""
        if not confirmed:
            return
        
        def cleanup_thread():
            try:
                log_paths = ["/media/hdd/*.log", "/home/root/*.log", "/tmp/*.log"]
                removed = 0
                
                for pattern in log_paths:
                    try:
                        result = subprocess.run(["sh", "-c", "rm -f " + pattern], 
                                              capture_output=True, timeout=5)
                        if result.returncode == 0:
                            removed += 1
                    except:
                        pass
                
                self.show_message("Logs cleaned from %d locations!" % removed, type="info")
            except Exception as e:
                self.show_message("Cleanup failed: " + str(e), type="error")
        
        threading.Thread(target=cleanup_thread, daemon=True).start()
    
    def show_picon_repair_dialog(self):
        """Show picon repair dialog"""
        self.show_confirmation(
            "Repair picon symlink?\n\nThis will recreate the picon symbolic link.",
            lambda res: self._execute_picon_repair(res) if res else None
        )
    
    def _execute_picon_repair(self, confirmed):
        """Execute picon repair"""
        if not confirmed:
            return
        
        def repair_thread():
            try:
                picon_source = "/media/hdd/picon"
                picon_target = "/usr/share/enigma2/picon"
                
                if not os.path.isdir(picon_source):
                    self.show_message("Picon source not found: " + picon_source, type="error")
                    return
                
                if os.path.islink(picon_target):
                    os.unlink(picon_target)
                elif os.path.exists(picon_target):
                    self.show_message("Picon target exists but is not a symlink!", type="error")
                    return
                
                os.symlink(picon_source, picon_target)
                self.show_message("Picon link repaired successfully!", type="info")
            except Exception as e:
                self.show_message("Picon repair failed: " + str(e), type="error")
        
        threading.Thread(target=repair_thread, daemon=True).start()
    
    def show_cloud_sync_dialog(self):
        """Show cloud sync dialog"""
        self.show_message(
            "Cloud Sync requires rclone to be configured.\n\n" +
            "1. Install: opkg install rclone\n" +
            "2. Configure: rclone config\n" +
            "3. Use sync command in terminal",
            type="info"
        )
    
    def show_repair_dialog(self):
        """Show repair dialog"""
        self.show_confirmation(
            "Install missing dependencies?\n\nThis may take several minutes.",
            lambda res: self._execute_repair(res) if res else None
        )
    
    def _execute_repair(self, confirmed):
        """Execute repair"""
        if not confirmed:
            return
        
        def repair_thread():
            try:
                packages = ['rclone', 'zip', 'unzip', 'tar', 'cifs-utils', 'samba-client', 'curl', 'ftp', 'sshfs']
                
                subprocess.run(["opkg", "update"], capture_output=True, timeout=60)
                
                installed = []
                failed = []
                
                for pkg in packages:
                    try:
                        result = subprocess.run(["opkg", "install", pkg], capture_output=True, timeout=120)
                        if result.returncode == 0:
                            installed.append(pkg)
                        else:
                            failed.append(pkg)
                    except:
                        failed.append(pkg)
                
                msg = "Installed: %d\n" % len(installed)
                if installed:
                    msg += "\n".join("  - " + p for p in installed)
                
                if failed:
                    msg += "\n\nFailed: %d\n" % len(failed)
                    msg += "\n".join("  - " + p for p in failed)
                
                self.show_message(msg, type="info")
            except Exception as e:
                self.show_message("Repair failed: " + str(e), type="error")
        
        threading.Thread(target=repair_thread, daemon=True).start()

    # FULL Bulk Rename Implementation
    def show_bulk_rename_dialog(self, files, file_ops, filelist, update_callback):
        """Show bulk rename dialog - FULL implementation"""
        if len(files) < 2:
            self.show_message("Select at least 2 files for bulk rename!", type="info")
            return
        
        choices = [
            ("Add Prefix", "prefix"),
            ("Add Suffix", "suffix"),
            ("Replace Text", "replace"),
            ("Number Sequence", "number"),
            ("Change Extension", "extension"),
            ("Remove Pattern", "remove"),
            ("Uppercase", "upper"),
            ("Lowercase", "lower")
        ]
        
        self.show_choice(
            "Bulk Rename %d files" % len(files),
            choices,
            lambda choice: self._handle_bulk_rename_choice(choice, files, file_ops, filelist, update_callback) if choice else None
        )
    
    def _handle_bulk_rename_choice(self, choice, files, file_ops, filelist, update_callback):
        """Handle bulk rename choice"""
        mode = choice[1]
        
        if mode in ["upper", "lower"]:
            # Direct execution for case changes
            self._execute_bulk_rename_case(mode, files, file_ops, filelist, update_callback)
        elif mode == "prefix":
            self.show_input("Enter prefix to add:", "", 
                          lambda text: self._execute_bulk_rename(mode, text, None, files, file_ops, filelist, update_callback) if text else None)
        elif mode == "suffix":
            self.show_input("Enter suffix (before extension):", "", 
                          lambda text: self._execute_bulk_rename(mode, text, None, files, file_ops, filelist, update_callback) if text else None)
        elif mode == "replace":
            self.show_input("Enter text to find:", "", 
                          lambda find_text: self._handle_replace_find(find_text, mode, files, file_ops, filelist, update_callback) if find_text else None)
        elif mode == "number":
            self.show_input("Enter base name (numbers added):", "file", 
                          lambda text: self._execute_bulk_rename(mode, text, None, files, file_ops, filelist, update_callback) if text else None)
        elif mode == "extension":
            self.show_input("Enter new extension (no dot):", "", 
                          lambda text: self._execute_bulk_rename(mode, text, None, files, file_ops, filelist, update_callback) if text else None)
        elif mode == "remove":
            self.show_input("Enter pattern to remove:", "", 
                          lambda text: self._execute_bulk_rename(mode, text, None, files, file_ops, filelist, update_callback) if text else None)
    
    def _handle_replace_find(self, find_text, mode, files, file_ops, filelist, update_callback):
        """Handle replace find text"""
        self.show_input("Replace '%s' with:" % find_text, "", 
                       lambda replace_text: self._execute_bulk_rename(mode, find_text, replace_text, files, file_ops, filelist, update_callback) if replace_text is not None else None)
    
    def _execute_bulk_rename_case(self, mode, files, file_ops, filelist, update_callback):
        """Execute case change bulk rename"""
        preview = []
        for file_path in files:
            old_name = os.path.basename(file_path)
            if mode == "upper":
                new_name = old_name.upper()
            else:
                new_name = old_name.lower()
            preview.append((old_name, new_name))
        
        self._show_rename_preview_and_confirm(preview, mode, None, None, files, file_ops, filelist, update_callback)
    
    def _execute_bulk_rename(self, mode, text, replace_text, files, file_ops, filelist, update_callback):
        """Execute bulk rename with preview"""
        preview = []
        for i, file_path in enumerate(files, 1):
            old_name = os.path.basename(file_path)
            name, ext = os.path.splitext(old_name)
            
            if mode == "prefix":
                new_name = text + old_name
            elif mode == "suffix":
                new_name = name + text + ext
            elif mode == "replace":
                new_name = old_name.replace(text, replace_text)
            elif mode == "number":
                new_name = "%s_%03d%s" % (text, i, ext)
            elif mode == "extension":
                new_name = name + "." + text
            elif mode == "remove":
                new_name = old_name.replace(text, "")
            else:
                new_name = old_name
            
            preview.append((old_name, new_name))
        
        self._show_rename_preview_and_confirm(preview, mode, text, replace_text, files, file_ops, filelist, update_callback)
    
    def _show_rename_preview_and_confirm(self, preview, mode, text, replace_text, files, file_ops, filelist, update_callback):
        """Show preview and confirm bulk rename"""
        preview_text = "Bulk Rename Preview (%d files):\n\n" % len(files)
        for old, new in preview[:10]:
            preview_text += "%s\n  -> %s\n\n" % (old, new)
        
        if len(preview) > 10:
            preview_text += "... and %d more\n\n" % (len(preview) - 10)
        
        preview_text += "Proceed with rename?"
        
        self.show_confirmation(
            preview_text,
            lambda res: self._confirm_bulk_rename(res, mode, text, replace_text, files, file_ops, filelist, update_callback)
        )
    
    def _confirm_bulk_rename(self, confirmed, mode, text, replace_text, files, file_ops, filelist, update_callback):
        """Confirm and execute bulk rename"""
        if not confirmed:
            return
        
        success = 0
        errors = []
        
        for i, file_path in enumerate(files, 1):
            try:
                old_name = os.path.basename(file_path)
                name, ext = os.path.splitext(old_name)
                
                if mode == "prefix":
                    new_name = text + old_name
                elif mode == "suffix":
                    new_name = name + text + ext
                elif mode == "replace":
                    new_name = old_name.replace(text, replace_text)
                elif mode == "number":
                    new_name = "%s_%03d%s" % (text, i, ext)
                elif mode == "extension":
                    new_name = name + "." + text
                elif mode == "remove":
                    new_name = old_name.replace(text, "")
                elif mode == "upper":
                    new_name = old_name.upper()
                elif mode == "lower":
                    new_name = old_name.lower()
                else:
                    new_name = old_name
                
                file_ops.rename(file_path, new_name)
                success += 1
                
            except Exception as e:
                errors.append("%s: %s" % (os.path.basename(file_path), str(e)[:30]))
        
        msg = "Renamed: %s files\n" % success
        if errors:
            msg += "\nFailed: %d\n" % len(errors)
            msg += "\n".join(errors[:5])
            if len(errors) > 5:
                msg += "\n... and %d more" % (len(errors) - 5)
        
        filelist.refresh()
        update_callback()
        self.show_message(msg, type="info")

    def show_network_browser_dialog(self, filelist, update_callback, network_browser, ftp_client, sftp_client, webdav_client):
        """Show network browser connection dialog"""
        choices = [
            ("Connect to FTP Server", "ftp"),
            ("Connect to SFTP Server", "sftp"),
            ("Connect to WebDAV Server", "webdav"),
            ("Recent Connections", "recent")
        ]
        
        self.show_choice(
            "Network Browser",
            choices,
            lambda choice: self._handle_network_browser_choice(choice, filelist, update_callback, network_browser, ftp_client, sftp_client, webdav_client) if choice else None
        )
    
    def _handle_network_browser_choice(self, choice, filelist, update_callback, network_browser, ftp_client, sftp_client, webdav_client):
        """Handle network browser choice"""
        protocol = choice[1]
        
        if protocol == "recent":
            self.show_message("Recent connections - feature coming soon", type="info")
            return
        
        # Show connection dialog
        self.show_input(
            "Enter %s address:\n(e.g., user@host:port)" % protocol.upper(),
            "",
            lambda addr: self._connect_network_browser(addr, protocol, filelist, update_callback, network_browser, ftp_client, sftp_client, webdav_client) if addr else None
        )
    
    def _connect_network_browser(self, address, protocol, filelist, update_callback, network_browser, ftp_client, sftp_client, webdav_client):
        """Connect network browser"""
        try:
            # Build network path
            network_path = "%s://%s/" % (protocol, address)
            
            # Test connection by listing root
            entries = network_browser.list_directory(network_path, ftp_client, sftp_client, webdav_client)
            
            # If successful, update file list (this would need FileList modification)
            self.show_message("Connected to %s\n\nFound %d items\n\nNote: Full dual-pane integration requires FileList modification" % (address, len(entries)), type="info")
            
        except Exception as e:
            self.show_message("Connection failed:\n%s" % str(e), type="error")
