from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.config import config
import os
import subprocess
import threading
import hashlib
from datetime import datetime
import glob

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
        try:
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
        except Exception as e:
            logger.error(f"Error showing message: {e}")
    
    def show_confirmation(self, text, callback):
        """Show confirmation dialog"""
        try:
            self.session.openWithCallback(callback, MessageBox, text, MessageBox.TYPE_YESNO)
        except Exception as e:
            logger.error(f"Error showing confirmation: {e}")
    
    def show_video_exit_confirmation(self, callback):
        """Show confirmation dialog when exiting video player"""
        try:
            self.session.openWithCallback(
                callback, 
                MessageBox, 
                "Stop playback and return to PilotFS?", 
                MessageBox.TYPE_YESNO
            )
        except Exception as e:
            logger.error(f"Error showing video exit confirmation: {e}")
    # Media exit confirmation - FIXED: removed session parameter
    def show_media_exit_confirmation(self, callback):
        """Show exit confirmation for media viewers"""
        try:
            self.session.openWithCallback(callback, MessageBox, 
                                       "Exit image viewer?", 
                                       MessageBox.TYPE_YESNO)
        except Exception as e:
            logger.error(f"Error showing media exit confirmation: {e}")
            # Fallback: execute callback with True (exit)
            callback(True)
    
    def show_video_exit_confirmation(self, callback):
        """Show exit confirmation for video playback - FIXED for proper behavior"""
        try:
            self.session.openWithCallback(
                callback,
                MessageBox,
                "Exit media player?",
                MessageBox.TYPE_YESNO,
                timeout=0
            )
        except Exception as e:
            logger.error(f"Error showing video exit confirmation: {e}")
            # Fallback: execute callback with True (exit)
            callback(True)
        
    
    def show_input(self, title, text="", callback=None):
        """Show input dialog"""
        try:
            self.session.openWithCallback(callback, VirtualKeyBoard, title=title, text=text)
        except Exception as e:
            logger.error(f"Error showing input: {e}")
    
    def show_choice(self, title, choices, callback=None):
        """Show choice dialog"""
        try:
            self.session.openWithCallback(callback, ChoiceBox, title=title, list=choices)
        except Exception as e:
            logger.error(f"Error showing choice: {e}")
    
    # File operations dialogs
    def show_create_dialog(self, current_dir, file_ops, update_callback):
        """Show create file/folder dialog"""
        try:
            choices = [
                ("Create New Folder", "folder"),
                ("Create New File", "file")
            ]
            
            self.show_choice(
                "Create New",
                choices,
                lambda choice: self._handle_create_choice(choice, current_dir, file_ops, update_callback) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing create dialog: {e}")
            self.show_message(f"Create dialog error: {e}", type="error")
    
    def _handle_create_choice(self, choice, current_dir, file_ops, update_callback):
        """Handle create choice"""
        try:
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
        except Exception as e:
            logger.error(f"Error handling create choice: {e}")
            self.show_message(f"Create choice error: {e}", type="error")
    
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
            logger.error(f"Error executing create: {e}")
            self.show_message("Creation failed: " + str(e), type="error")
    
    def show_create_file_dialog(self, current_dir, file_ops, update_callback):
        """Show create file dialog"""
        try:
            self.show_input(
                "Enter file name:",
                "new_file.txt",
                lambda name: self._execute_create(name, "file", current_dir, file_ops, update_callback) if name else None
            )
        except Exception as e:
            logger.error(f"Error showing create file dialog: {e}")
            self.show_message(f"Create file error: {e}", type="error")
    
    def show_create_folder_dialog(self, current_dir, file_ops, update_callback):
        """Show create folder dialog"""
        try:
            self.show_input(
                "Enter folder name:",
                "new_folder",
                lambda name: self._execute_create(name, "folder", current_dir, file_ops, update_callback) if name else None
            )
        except Exception as e:
            logger.error(f"Error showing create folder dialog: {e}")
            self.show_message(f"Create folder error: {e}", type="error")
    
    def show_transfer_dialog(self, files, destination, callback):
        """Show transfer dialog"""
        try:
            num_files = len([x for x in files if os.path.isfile(x)])
            num_dirs = len([x for x in files if os.path.isdir(x)])
            
            choices = [
                (f"Copy {len(files)} items ({num_dirs} folders, {num_files} files)", "cp"),
                (f"Move {len(files)} items ({num_dirs} folders, {num_files} files)", "mv")
            ]
            
            self.show_choice(
                "Transfer to: " + destination,
                choices,
                lambda choice: callback(choice[1], files, destination) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing transfer dialog: {e}")
            self.show_message(f"Transfer dialog error: {e}", type="error")
    
    def show_permissions_dialog(self, files, file_ops):
        """Show permissions dialog"""
        try:
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
        except Exception as e:
            logger.error(f"Error showing permissions dialog: {e}")
            self.show_message(f"Permissions dialog error: {e}", type="error")
    
    def _execute_change_permissions(self, mode_str, files, file_ops):
        """Execute permission change"""
        try:
            for file_path in files:
                file_ops.change_permissions(file_path, mode_str)
            
            self.show_message("Permissions changed to %s for %d items" % (mode_str, len(files)), type="info")
        except Exception as e:
            logger.error(f"Error executing permission change: {e}")
            self.show_message("Change permissions failed: " + str(e), type="error")
    
    def show_checksum_dialog(self, files, file_ops):
        """Show checksum dialog"""
        try:
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
        except Exception as e:
            logger.error(f"Error showing checksum dialog: {e}")
            self.show_message(f"Checksum dialog error: {e}", type="error")
    
    def _execute_checksum(self, algorithm, files, file_ops):
        """Execute checksum calculation"""
        def checksum_thread():
            try:
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
            except Exception as e:
                logger.error(f"Error in checksum thread: {e}")
                self.show_message(f"Checksum calculation failed: {e}", type="error")
        
        threading.Thread(target=checksum_thread, daemon=True).start()
    
    # Archive dialogs
    def show_archive_dialog(self, files, archive_mgr, current_dir):
        """Show archive creation dialog"""
        try:
            choices = [
                ("Create ZIP archive", "zip"),
                ("Create TAR.GZ archive", "tar.gz")
            ]
            
            self.show_choice(
                "Archive %d items" % len(files),
                choices,
                lambda choice: self._handle_archive_choice(choice, files, archive_mgr, current_dir) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing archive dialog: {e}")
            self.show_message(f"Archive dialog error: {e}", type="error")
    
    def _handle_archive_choice(self, choice, files, archive_mgr, current_dir):
        """Handle archive choice"""
        try:
            archive_type = choice[1]
            default_name = "archive_" + datetime.now().strftime('%Y%m%d_%H%M%S')
            
            self.show_input(
                "Archive name (" + archive_type.upper() + "):",
                default_name,
                lambda name: self._execute_create_archive(name, archive_type, files, archive_mgr, current_dir) if name else None
            )
        except Exception as e:
            logger.error(f"Error handling archive choice: {e}")
            self.show_message(f"Archive choice error: {e}", type="error")
    
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
            logger.error(f"Error executing archive creation: {e}")
            self.show_message("Archive creation failed: " + str(e), type="error")
    
    def show_extract_dialog(self, archive_path, archive_mgr, filelist, update_callback):
        """Show extract archive dialog"""
        try:
            archive_name = os.path.basename(archive_path)
            dest_dir = os.path.join(os.path.dirname(archive_path), 
                                   os.path.splitext(archive_name)[0].replace('.tar', ''))
            
            self.show_confirmation(
                "Extract '" + archive_name + "' to:\n" + dest_dir + "?",
                lambda res: self._execute_extract(res, archive_path, dest_dir, archive_mgr, filelist, update_callback)
            )
        except Exception as e:
            logger.error(f"Error showing extract dialog: {e}")
            self.show_message(f"Extract dialog error: {e}", type="error")
    
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
                logger.error(f"Error in extract thread: {e}")
                self.show_message("Extraction failed: " + str(e), type="error")
        
        threading.Thread(target=extract_thread, daemon=True).start()
    
    # Search dialogs
    def show_search_dialog(self, directory, search_engine):
        """Show file search dialog"""
        try:
            self.show_input(
                "Search files (wildcards: * ?):",
                "",
                lambda pattern: self._execute_file_search(pattern, directory, search_engine) if pattern else None
            )
        except Exception as e:
            logger.error(f"Error showing search dialog: {e}")
            self.show_message(f"Search dialog error: {e}", type="error")
    
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
                logger.error(f"Error in search thread: {e}")
                self.show_message("Search failed: " + str(e), type="error")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def show_content_search_dialog(self, directory, search_engine):
        """Show content search dialog"""
        try:
            self.show_input(
                "Search text in files:",
                "",
                lambda pattern: self._execute_content_search(pattern, directory, search_engine) if pattern else None
            )
        except Exception as e:
            logger.error(f"Error showing content search dialog: {e}")
            self.show_message(f"Content search dialog error: {e}", type="error")
    
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
                logger.error(f"Error in content search thread: {e}")
                self.show_message("Search failed: " + str(e), type="error")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    # Preview dialogs
    def preview_file(self, file_path, file_ops, config):
        """Preview file contents"""
        try:
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
        except Exception as e:
            logger.error(f"Error previewing file: {e}")
            self.show_message(f"Preview error: {e}", type="error")
    
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
            logger.error(f"Error previewing text file: {e}")
            self.show_message("Cannot preview file: " + str(e), type="error")
    
    def _preview_image(self, file_path, file_ops):
        """Preview image file - UPDATED to use ImageViewer"""
        try:
            # Try to use advanced ImageViewer
            try:
                from .image_viewer import ImageViewer
                self.session.open(ImageViewer, file_path)
                return
            except ImportError as e:
                logger.warning("ImageViewer not available: %s" % str(e))
            
            # Fallback to info display
            info = file_ops.get_file_info(file_path)
            
            preview = "Image Preview\n\n"
            preview += "File: %s\n" % info['name']
            preview += "Size: %s\n" % info['size_formatted']
            preview += "Type: %s\n" % os.path.splitext(file_path)[1].upper()
            preview += "Modified: %s\n\n" % info['modified'].strftime('%Y-%m-%d %H:%M')
            preview += "Advanced viewer not available."
            
            self.show_message(preview, type="info")
        except Exception as e:
            logger.error("Error previewing image: %s" % str(e))
            self.show_message("Cannot preview image: %s" % str(e), type="error")
    
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
            logger.error(f"Error previewing binary file: {e}")
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
            logger.error(f"Error previewing media: {e}")
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
                logger.error(f"Error in disk usage thread: {e}")
                self.show_message("Analysis failed: " + str(e), type="error")
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    # Storage selector - FIXED VERSION
    def show_storage_selector(self, change_dir_callback, update_callback):
        """Show storage selector - FIXED with dynamic detection"""
        try:
            choices = []
            
            # Dynamic storage detection
            storage_locations = self._detect_storage_devices()
            
            if not storage_locations:
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
        except Exception as e:
            logger.error(f"Error showing storage selector: {e}")
            self.show_message(f"Storage selector error: {e}", type="error")
    
    def _detect_storage_devices(self):
        """Dynamically detect storage devices"""
        storage_list = []
        
        try:
            # Check common mount points
            mount_patterns = [
                ("/media/*", "Storage"),
                ("/media/hdd/*", "HDD"),
                ("/media/usb*", "USB"),
                ("/media/net/*", "Network"),
                ("/media/sd*", "SD Card"),
                ("/media/mmc*", "MMC Card"),
                ("/mnt/*", "Mount"),
                ("/autofs/*", "AutoFS"),
            ]
            
            for pattern, label_prefix in mount_patterns:
                try:
                    mount_points = glob.glob(pattern)
                    for mp in mount_points:
                        if os.path.isdir(mp) and os.access(mp, os.R_OK):
                            # Check if it's a mount point
                            try:
                                with open('/proc/mounts', 'r') as f:
                                    mounts = f.read()
                                    if mp in mounts or os.path.ismount(mp):
                                        dev_name = os.path.basename(mp)
                                        storage_list.append((f"{label_prefix}: {dev_name}", mp))
                            except:
                                # Fallback: just use directory name
                                dev_name = os.path.basename(mp)
                                storage_list.append((f"{label_prefix}: {dev_name}", mp))
                except Exception as e:
                    logger.debug(f"Error scanning {pattern}: {e}")
            
            # Add root filesystem
            storage_list.append(("Root Filesystem", "/"))
            
            # Add common locations
            common_dirs = [
                ("Home Directory", os.path.expanduser("~")),
                ("Temp Directory", "/tmp"),
                ("System Logs", "/var/log"),
                ("Configuration", "/etc"),
            ]
            
            for label, path in common_dirs:
                if os.path.isdir(path):
                    storage_list.append((label, path))
            
        except Exception as e:
            logger.error(f"Error detecting storage devices: {e}")
        
        return storage_list
    
    def _select_storage(self, choice, change_dir_callback, update_callback):
        """Select storage location - FIXED to properly navigate"""
        try:
            path = choice[1]
            logger.info(f"Attempting to navigate to storage: {path}")
            
            if os.path.isdir(path) and os.access(path, os.R_OK):
                # Call the change_dir_callback to navigate
                change_dir_callback(path)
                # Call update_callback to refresh UI
                update_callback()
                logger.info(f"Successfully navigated to: {path}")
            else:
                logger.warning(f"Storage not accessible: {path}")
                self.show_message(f"Storage not accessible:\n{path}", type="error")
        except Exception as e:
            logger.error(f"Error selecting storage: {e}")
            self.show_message(f"Storage selection error: {e}", type="error")
    
    # Bookmark dialogs
    def show_bookmark_dialog(self, path, bookmarks, config):
        """Show bookmark dialog"""
        try:
            self.show_input(
                "Bookmark number (1-9):",
                "1",
                lambda num_str: self._set_bookmark(num_str, path, bookmarks, config) if num_str else None
            )
        except Exception as e:
            logger.error(f"Error showing bookmark dialog: {e}")
            self.show_message(f"Bookmark dialog error: {e}", type="error")
    
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
        except Exception as e:
            logger.error(f"Error setting bookmark: {e}")
            self.show_message(f"Bookmark error: {e}", type="error")
    
    def show_bookmark_manager(self, bookmarks, config, filelist, update_callback):
        """Show bookmark manager"""
        try:
            if not bookmarks:
                self.show_message("No bookmarks saved.\n\nPress 1-9 in any folder to create a bookmark!", type="info")
                return
            
            bookmark_list = [("Bookmark %s: %s" % (k, v), k) for k, v in sorted(bookmarks.items())]
            bookmark_list.append(("Clear All Bookmarks", "clear"))
            
            self.show_choice(
                "Manage Bookmarks",
                bookmark_list,
                lambda choice, cfg=config: self._handle_bookmark_action(choice, bookmarks, cfg, filelist, update_callback) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing bookmark manager: {e}")
            self.show_message(f"Bookmark manager error: {e}", type="error")
    
    def _handle_bookmark_action(self, choice, bookmarks, config, filelist, update_callback):
        """Handle bookmark action"""
        try:
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
        except Exception as e:
            logger.error(f"Error handling bookmark action: {e}")
            self.show_message(f"Bookmark action error: {e}", type="error")
    
    def _clear_bookmarks(self, confirmed, bookmarks, config):
        """Clear bookmarks"""
        if not confirmed:
            return
        
        try:
            bookmarks.clear()
            config.save_bookmarks(bookmarks)
            self.show_message("All bookmarks cleared", type="info", timeout=2)
        except Exception as e:
            logger.error(f"Error clearing bookmarks: {e}")
            self.show_message(f"Clear bookmarks error: {e}", type="error")
    
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
            logger.error(f"Error showing trash manager: {e}")
            self.show_message("Trash error: " + str(e), type="error")
    
    def _handle_trash_action(self, choice, file_ops, filelist, update_callback):
        """Handle trash action"""
        action = choice[1]
        
        try:
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
        except Exception as e:
            logger.error(f"Error handling trash action: {e}")
            self.show_message(f"Trash action error: {e}", type="error")
    
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
            logger.error(f"Error emptying trash: {e}")
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
            logger.error(f"Error restoring from trash: {e}")
            self.show_message("Restore failed: " + str(e), type="error")
    
    # Network dialogs
    def show_mount_dialog(self, mount_point, mount_mgr, filelist, update_callback):
        """Show mount remote dialog with full CIFS/SMB support"""
        try:
            choices = [
                ("🗄️ Mount CIFS/SMB Share", "mount_cifs"),
                ("📋 Show Mounted Shares", "list_mounts"),
                ("🔌 Unmount Share", "unmount"),
                ("🧹 Cleanup Stale Mounts", "cleanup"),
                ("📍 Available Mount Points", "mount_points"),
            ]
            
            self.show_choice(
                "🗄️ Mount Remote Share",
                choices,
                lambda choice: self._handle_mount_action(choice, mount_point, mount_mgr, filelist, update_callback) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing mount dialog: {e}")
            self.show_message(f"Mount dialog error: {e}", type="error")
    
    def show_network_scan_dialog(self, mount_mgr):
        """Show network scan dialog - discover SMB shares"""
        try:
            self.show_input(
                "Enter server IP to scan for shares:",
                "192.168.1.100",
                lambda server: self._execute_network_scan(server, mount_mgr) if server else None
            )
        except Exception as e:
            logger.error(f"Error showing network scan dialog: {e}")
            self.show_message(f"Network scan error: {e}", type="error")
    
    def show_ping_dialog(self, mount_mgr):
        """Show ping test dialog for network troubleshooting"""
        try:
            choices = [
                ("🔌 Ping Server", "ping_server"),
                ("🌐 Ping Common Servers", "ping_common"),
            ]
            
            self.show_choice(
                "🔌 Network Ping Test",
                choices,
                lambda choice: self._handle_ping_action(choice, mount_mgr) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing ping dialog: {e}")
            self.show_message(f"Ping dialog error: {e}", type="error")
    
    def show_remote_access_dialog(self, remote_mgr, mount_mgr, filelist, update_callback):
        """Show remote access dialog - FTP/SFTP/WebDAV - BASIC VERSION"""
        try:
            choices = [
                ("📡 Test FTP Connection", "ftp"),
                ("🔒 Test SFTP Connection", "sftp"),
                ("📋 View Saved Connections", "list"),
            ]
            
            self.show_choice(
                "🌐 Remote File Access",
                choices,
                lambda choice: self._handle_remote_basic(choice, remote_mgr) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing remote access dialog: {e}")
            self.show_message(f"Remote access error: {e}", type="error")
    
    def _handle_remote_basic(self, choice, remote_mgr):
        """Handle basic remote access"""
        action = choice[1]
        if action == "list":
            conns = remote_mgr.list_connections()
            if conns:
                msg = f"Saved Connections: {len(conns)}\n\n"
                for name, conn in list(conns.items())[:5]:
                    msg += f"• {name} ({conn.get('type', 'unknown')})\n"
                self.show_message(msg, type="info")
            else:
                self.show_message("No saved connections", type="info")
        else:
            self.show_message(f"{action.upper()} test - Enter server details in config", type="info")
    
    def _execute_network_scan(self, server, mount_mgr):
        """Execute network share scanning"""
        def scan_thread():
            try:
                import threading
                self.show_message(f"📡 Scanning {server}...", type="info", timeout=2)
                success, result = mount_mgr.scan_network_shares(server)
                
                if success:
                    shares = result
                    msg = f"✅ Found {len(shares)} share(s):\n\n"
                    for share in shares[:10]:
                        msg += f"📁 {share.get('name', 'unknown')}\n"
                    self.show_message(msg, type="info")
                else:
                    self.show_message(f"❌ Scan failed: {result}", type="error")
            except Exception as e:
                self.show_message(f"Scan error: {str(e)}", type="error")
        
        import threading
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def _handle_ping_action(self, choice, mount_mgr):
        """Handle ping action"""
        action = choice[1]
        if action == "ping_server":
            self.show_input(
                "Enter server IP:",
                "192.168.1.1",
                lambda server: self._execute_ping(server, mount_mgr) if server else None
            )
        elif action == "ping_common":
            self._ping_common_servers(mount_mgr)
    
    def _execute_ping(self, server, mount_mgr):
        """Execute ping test"""
        def ping_thread():
            try:
                success, message = mount_mgr.test_ping(server)
                if success:
                    self.show_message(f"✅ {server} reachable", type="info")
                else:
                    self.show_message(f"❌ {server} unreachable: {message}", type="error")
            except Exception as e:
                self.show_message(f"Ping error: {str(e)}", type="error")
        
        import threading
        threading.Thread(target=ping_thread, daemon=True).start()
    
    def _ping_common_servers(self, mount_mgr):
        """Ping common servers"""
        def ping_multiple():
            servers = [("Router", "192.168.1.1"), ("Google DNS", "8.8.8.8")]
            results = []
            for name, ip in servers:
                success, _ = mount_mgr.test_ping(ip)
                results.append(f"{'✅' if success else '❌'} {name} ({ip})")
            self.show_message("Network Test:\n\n" + "\n".join(results), type="info")
        
        import threading
        threading.Thread(target=ping_multiple, daemon=True).start()
    
    def _handle_mount_action(self, choice, mount_point, mount_mgr, filelist, update_callback):
        """Handle mount action - SIMPLIFIED"""
        action = choice[1]
        
        if action == "mount_cifs":
            self.show_message(
                "Mount CIFS:\n\n1. Enter server IP\n2. Enter share name\n3. Credentials (optional)\n\nUse manual mount for now:\nmount -t cifs //server/share /media/net/share",
                type="info"
            )
        elif action == "list_mounts":
            def list_thread():
                success, mounts = mount_mgr.list_mounts()
                if success:
                    network = [m for m in mounts if '//' in m or ':' in m]
                    if network:
                        msg = f"Network Mounts ({len(network)}):\n\n"
                        msg += "\n".join(network[:5])
                        self.show_message(msg, type="info")
                    else:
                        self.show_message("No network mounts active", type="info")
                else:
                    self.show_message("Failed to list mounts", type="error")
            
            import threading
            threading.Thread(target=list_thread, daemon=True).start()
        else:
            self.show_message(f"{action} - Use system tools for now", type="info")
    
    def _handle_bulk_rename_choice(self, choice, files, file_ops, filelist, update_callback):
        """Handle bulk rename choice"""
        try:
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
                self.show_input("Enter new extension (without dot):", "", 
                              lambda text: self._execute_bulk_rename(mode, text, None, files, file_ops, filelist, update_callback) if text else None)
            elif mode == "remove":
                self.show_input("Enter pattern to remove:", "", 
                              lambda text: self._execute_bulk_rename(mode, text, None, files, file_ops, filelist, update_callback) if text else None)
        except Exception as e:
            logger.error(f"Error handling bulk rename choice: {e}")
            self.show_message(f"Bulk rename choice error: {e}", type="error")
    
    def _handle_replace_find(self, find_text, mode, files, file_ops, filelist, update_callback):
        """Handle replace find text"""
        try:
            self.show_input("Replace '%s' with:" % find_text, "", 
                           lambda replace_text: self._execute_bulk_rename(mode, find_text, replace_text, files, file_ops, filelist, update_callback) if replace_text is not None else None)
        except Exception as e:
            logger.error(f"Error handling replace find: {e}")
            self.show_message(f"Replace find error: {e}", type="error")
    
    def _execute_bulk_rename_case(self, mode, files, file_ops, filelist, update_callback):
        """Execute case change bulk rename"""
        try:
            preview = []
            for file_path in files:
                old_name = os.path.basename(file_path)
                name, ext = os.path.splitext(old_name)
                if mode == "upper":
                    new_name = name.upper() + ext
                else:
                    new_name = name.lower() + ext
                preview.append((old_name, new_name))
            
            self._show_rename_preview_and_confirm(preview, mode, None, None, files, file_ops, filelist, update_callback)
        except Exception as e:
            logger.error(f"Error executing bulk rename case: {e}")
            self.show_message(f"Bulk rename case error: {e}", type="error")
    
    def _execute_bulk_rename(self, mode, text, replace_text, files, file_ops, filelist, update_callback):
        """Execute bulk rename with preview - FIXED extension handling"""
        try:
            preview = []
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
                        new_name = f"{text}_{i:03d}{ext}"
                    elif mode == "extension":
                        # Handle extension with or without dot
                        if text.startswith('.'):
                            new_ext = text
                        else:
                            new_ext = '.' + text
                        new_name = name + new_ext
                    elif mode == "remove":
                        new_name = old_name.replace(text, "")
                    else:
                        new_name = old_name
                    
                    preview.append((old_name, new_name))
                except Exception:
                    preview.append((old_name, old_name))  # Fallback on error
            
            self._show_rename_preview_and_confirm(preview, mode, text, replace_text, files, file_ops, filelist, update_callback)
        except Exception as e:
            logger.error(f"Error executing bulk rename: {e}")
            self.show_message(f"Bulk rename error: {e}", type="error")
    
    def _show_rename_preview_and_confirm(self, preview, mode, text, replace_text, files, file_ops, filelist, update_callback):
        """Show preview and confirm bulk rename"""
        try:
            preview_text = "Bulk Rename Preview (%d files):\n\n" % len(files)
            for old, new in preview[:10]:
                preview_text += f"{old}\n  -> {new}\n\n"
            
            if len(preview) > 10:
                preview_text += f"... and {len(preview) - 10} more\n\n"
            
            preview_text += "Proceed with rename?"
            
            self.show_confirmation(
                preview_text,
                lambda res: self._confirm_bulk_rename(res, mode, text, replace_text, files, file_ops, filelist, update_callback)
            )
        except Exception as e:
            logger.error(f"Error showing rename preview: {e}")
            self.show_message(f"Rename preview error: {e}", type="error")
    
    def _confirm_bulk_rename(self, confirmed, mode, text, replace_text, files, file_ops, filelist, update_callback):
        """Confirm and execute bulk rename"""
        if not confirmed:
            return
        
        try:
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
                        new_name = f"{text}_{i:03d}{ext}"
                    elif mode == "extension":
                        # Handle extension with or without dot
                        if text.startswith('.'):
                            new_ext = text
                        else:
                            new_ext = '.' + text
                        new_name = name + new_ext
                    elif mode == "remove":
                        new_name = old_name.replace(text, "")
                    elif mode == "upper":
                        new_name = name.upper() + ext
                    elif mode == "lower":
                        new_name = name.lower() + ext
                    else:
                        new_name = old_name
                    
                    file_ops.rename(file_path, new_name)
                    success += 1
                    
                except Exception as e:
                    errors.append(f"{os.path.basename(file_path)}: {str(e)[:30]}")
            
            msg = f"Renamed: {success} files\n"
            if errors:
                msg += f"\nFailed: {len(errors)}\n"
                msg += "\n".join(errors[:5])
                if len(errors) > 5:
                    msg += f"\n... and {len(errors) - 5} more"
            
            filelist.refresh()
            update_callback()
            self.show_message(msg, type="info")
        except Exception as e:
            logger.error(f"Error confirming bulk rename: {e}")
            self.show_message(f"Bulk rename confirmation error: {e}", type="error")
    
    # ========================================================================
    # MISSING DIALOG METHODS - FIXING THE ERRORS
    # ========================================================================
    
    def show_cleanup_dialog(self, directory, file_ops, filelist, update_callback):
        """Show cleanup dialog for temporary/duplicate files"""
        try:
            choices = [
                ("🗑️ Clean Temporary Files (.tmp, .temp, .log)", "temp"),
                ("🧹 Remove Empty Directories", "empty"),
                ("🔍 Find Duplicate Files", "duplicates"),
                ("📉 Remove Large Cache Files", "cache"),
            ]
            
            self.show_choice(
                "🧹 Cleanup Operations",
                choices,
                lambda choice: self._handle_cleanup_choice(choice, directory, file_ops, filelist, update_callback) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing cleanup dialog: {e}")
            self.show_message(f"Cleanup dialog error: {e}", type="error")
    
    def _handle_cleanup_choice(self, choice, directory, file_ops, filelist, update_callback):
        """Handle cleanup choice"""
        action = choice[1]
        
        if action == "temp":
            self.show_confirmation(
                "Remove all temporary files?\n(.tmp, .temp, .log, backup files)",
                lambda res: self._execute_cleanup_temp(res, directory, file_ops, filelist, update_callback)
            )
        elif action == "empty":
            self.show_confirmation(
                "Remove all empty directories?\n(This cannot be undone)",
                lambda res: self._execute_cleanup_empty(res, directory, file_ops, filelist, update_callback)
            )
        elif action == "duplicates":
            self.show_message("Finding duplicates... (Feature in development)", type="info")
        elif action == "cache":
            self.show_confirmation(
                "Remove cache files > 100MB?\n(This may improve performance)",
                lambda res: self._execute_cleanup_cache(res, directory, file_ops, filelist, update_callback)
            )
    
    def _execute_cleanup_temp(self, confirmed, directory, file_ops, filelist, update_callback):
        """Execute temporary files cleanup"""
        if not confirmed:
            return
        
        def cleanup_thread():
            try:
                temp_extensions = ['.tmp', '.temp', '.log', '.bak', '.backup', '.old']
                count = 0
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if any(file.endswith(ext) for ext in temp_extensions):
                            try:
                                os.remove(os.path.join(root, file))
                                count += 1
                            except:
                                pass
                
                filelist.refresh()
                update_callback()
                self.show_message(f"🧹 Removed {count} temporary files", type="info")
            except Exception as e:
                logger.error(f"Error in cleanup temp thread: {e}")
                self.show_message(f"Cleanup failed: {e}", type="error")
        
        threading.Thread(target=cleanup_thread, daemon=True).start()
    
    def _execute_cleanup_empty(self, confirmed, directory, file_ops, filelist, update_callback):
        """Execute empty directories cleanup"""
        if not confirmed:
            return
        
        def cleanup_thread():
            try:
                count = 0
                
                for root, dirs, files in os.walk(directory, topdown=False):
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            if not os.listdir(dir_path):
                                os.rmdir(dir_path)
                                count += 1
                        except:
                            pass
                
                filelist.refresh()
                update_callback()
                self.show_message(f"🧹 Removed {count} empty directories", type="info")
            except Exception as e:
                logger.error(f"Error in cleanup empty thread: {e}")
                self.show_message(f"Cleanup failed: {e}", type="error")
        
        threading.Thread(target=cleanup_thread, daemon=True).start()
    
    def _execute_cleanup_cache(self, confirmed, directory, file_ops, filelist, update_callback):
        """Execute cache files cleanup"""
        if not confirmed:
            return
        
        def cleanup_thread():
            try:
                count = 0
                total_size = 0
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if 'cache' in file.lower() or file.endswith('.cache'):
                            file_path = os.path.join(root, file)
                            try:
                                size = os.path.getsize(file_path)
                                if size > 100 * 1024 * 1024:  # 100MB
                                    os.remove(file_path)
                                    count += 1
                                    total_size += size
                            except:
                                pass
                
                filelist.refresh()
                update_callback()
                self.show_message(f"🧹 Removed {count} cache files\nFreed: {format_size(total_size)}", type="info")
            except Exception as e:
                logger.error(f"Error in cleanup cache thread: {e}")
                self.show_message(f"Cleanup failed: {e}", type="error")
        
        threading.Thread(target=cleanup_thread, daemon=True).start()
    
    def show_repair_dialog(self, files, file_ops, filelist, update_callback):
        """Show file repair dialog"""
        try:
            choices = [
                ("🔧 Fix File Permissions (755/644)", "permissions"),
                ("🔄 Fix Line Endings (Windows/Unix)", "line_endings"),
                ("📝 Fix File Encoding (UTF-8)", "encoding"),
                ("📦 Verify Archive Integrity", "archive"),
            ]
            
            self.show_choice(
                "🔧 File Repair Tools",
                choices,
                lambda choice: self._handle_repair_choice(choice, files, file_ops, filelist, update_callback) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing repair dialog: {e}")
            self.show_message(f"Repair dialog error: {e}", type="error")
    
    def _handle_repair_choice(self, choice, files, file_ops, filelist, update_callback):
        """Handle repair choice"""
        action = choice[1]
        
        if action == "permissions":
            self.show_message("Repairing permissions...", type="info", timeout=2)
            self._execute_permission_repair(files, file_ops, filelist, update_callback)
        elif action == "line_endings":
            self.show_message("Fixing line endings... (Feature in development)", type="info")
        elif action == "encoding":
            self.show_message("Fixing encoding... (Feature in development)", type="info")
        elif action == "archive":
            self.show_message("Verifying archives... (Feature in development)", type="info")
    
    def _execute_permission_repair(self, files, file_ops, filelist, update_callback):
        """Execute permission repair"""
        def repair_thread():
            try:
                count = 0
                
                for file_path in files:
                    try:
                        if os.path.isdir(file_path):
                            file_ops.change_permissions(file_path, "755")
                        else:
                            # Check if file is executable
                            if os.access(file_path, os.X_OK) or file_path.endswith(('.sh', '.py', '.bin')):
                                file_ops.change_permissions(file_path, "755")
                            else:
                                file_ops.change_permissions(file_path, "644")
                        count += 1
                    except:
                        pass
                
                filelist.refresh()
                update_callback()
                self.show_message(f"🔧 Fixed permissions for {count} files", type="info")
            except Exception as e:
                logger.error(f"Error in permission repair thread: {e}")
                self.show_message(f"Permission repair failed: {e}", type="error")
        
        threading.Thread(target=repair_thread, daemon=True).start()
    
    def show_picon_repair_dialog(self, directory, file_ops, filelist, update_callback):
        """Show picon repair dialog for Enigma2"""
        try:
            choices = [
                ("🖼️ Scan for Broken Picons", "scan"),
                ("🔄 Fix Picon Names", "rename"),
                ("📦 Download Missing Picons", "download"),
                ("🗑️ Remove Duplicate Picons", "dedupe"),
            ]
            
            self.show_choice(
                "🖼️ Picon Management",
                choices,
                lambda choice: self._handle_picon_choice(choice, directory, file_ops, filelist, update_callback) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing picon repair dialog: {e}")
            self.show_message(f"Picon dialog error: {e}", type="error")
    
    def _handle_picon_choice(self, choice, directory, file_ops, filelist, update_callback):
        """Handle picon choice"""
        action = choice[1]
        
        if action == "scan":
            self._scan_broken_picons(directory, file_ops, filelist, update_callback)
        elif action == "rename":
            self.show_message("Renaming picons... (Feature in development)", type="info")
        elif action == "download":
            self.show_message("Downloading picons... (Feature in development)", type="info")
        elif action == "dedupe":
            self.show_message("Removing duplicates... (Feature in development)", type="info")
    
    def _scan_broken_picons(self, directory, file_ops, filelist, update_callback):
        """Scan for broken picons"""
        def scan_thread():
            try:
                broken = []
                picon_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if any(file.endswith(ext) for ext in picon_extensions):
                            file_path = os.path.join(root, file)
                            try:
                                size = os.path.getsize(file_path)
                                if size < 100:  # Likely broken if <100 bytes
                                    broken.append(file_path)
                            except:
                                pass
                
                if broken:
                    msg = f"Found {len(broken)} potentially broken picons:\n\n"
                    for picon in broken[:10]:
                        msg += f"• {os.path.basename(picon)}\n"
                    if len(broken) > 10:
                        msg += f"\n... and {len(broken) - 10} more"
                    
                    self.show_message(msg, type="warning")
                else:
                    self.show_message("✅ No broken picons found", type="info")
                    
            except Exception as e:
                logger.error(f"Error in picon scan thread: {e}")
                self.show_message(f"Picon scan failed: {e}", type="error")
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def show_queue_dialog(self, queue_manager):
        """Show queue management dialog"""
        try:
            choices = [
                ("📋 View Current Queue", "view"),
                ("▶️ Start Queue Processing", "start"),
                ("⏸️ Pause Queue", "pause"),
                ("🗑️ Clear Queue", "clear"),
                ("📊 Queue Statistics", "stats"),
            ]
            
            self.show_choice(
                "📋 Operation Queue",
                choices,
                lambda choice: self._handle_queue_action(choice, queue_manager) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing queue dialog: {e}")
            self.show_message(f"Queue dialog error: {e}", type="error")
    
    def _handle_queue_action(self, choice, queue_manager):
        """Handle queue action"""
        action = choice[1]
        
        if action == "view":
            queue = queue_manager.get_queue()
            if queue:
                msg = f"Queue: {len(queue)} items\n\n"
                for i, item in enumerate(queue[:5], 1):
                    msg += f"{i}. {item.get('type', 'unknown')}: {item.get('name', 'unknown')}\n"
                if len(queue) > 5:
                    msg += f"\n... and {len(queue) - 5} more"
                self.show_message(msg, type="info")
            else:
                self.show_message("Queue is empty", type="info")
        elif action == "start":
            self.show_message("Starting queue...", type="info", timeout=2)
        elif action == "pause":
            self.show_message("Pausing queue...", type="info", timeout=2)
        elif action == "clear":
            self.show_confirmation(
                "Clear all queued operations?",
                lambda res: self._execute_queue_clear(res, queue_manager)
            )
        elif action == "stats":
            stats = queue_manager.get_stats()
            msg = f"Queue Statistics:\n\n"
            msg += f"Total operations: {stats.get('total', 0)}\n"
            msg += f"Completed: {stats.get('completed', 0)}\n"
            msg += f"Failed: {stats.get('failed', 0)}\n"
            msg += f"Pending: {stats.get('pending', 0)}"
            self.show_message(msg, type="info")
    
    def _execute_queue_clear(self, confirmed, queue_manager):
        """Execute queue clear"""
        if not confirmed:
            return
        
        try:
            queue_manager.clear_queue()
            self.show_message("Queue cleared", type="info", timeout=2)
        except Exception as e:
            logger.error(f"Error clearing queue: {e}")
            self.show_message(f"Clear queue failed: {e}", type="error")
    
    def show_log_viewer(self):
        """Show log viewer dialog"""
        try:
            log_content = self._read_log_file()
            if log_content:
                # Truncate if too long
                if len(log_content) > 5000:
                    log_content = "... (earlier logs truncated) ...\n\n" + log_content[-5000:]
                
                self.show_message(f"PilotFS Logs:\n\n{log_content}", type="info")
            else:
                self.show_message("Log file is empty or not found", type="info")
        except Exception as e:
            logger.error(f"Error showing log viewer: {e}")
            self.show_message(f"Log viewer error: {e}", type="error")
    
    def _read_log_file(self):
        """Read log file content"""
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                return "Log file not found: " + LOG_FILE
        except Exception as e:
            return f"Error reading log file: {e}"
    
    def show_bulk_rename_dialog(self, files, file_ops, filelist, update_callback):
        """Show bulk rename dialog"""
        try:
            choices = [
                ("🅰️ Convert to UPPERCASE", "upper"),
                ("🅰️ Convert to lowercase", "lower"),
                ("➕ Add Prefix", "prefix"),
                ("➕ Add Suffix", "suffix"),
                ("🔀 Replace Text", "replace"),
                ("🔢 Number Files", "number"),
                ("📄 Change Extension", "extension"),
                ("🗑️ Remove Pattern", "remove"),
            ]
            
            self.show_choice(
                "🔄 Bulk Rename %d Files" % len(files),
                choices,
                lambda choice: self._handle_bulk_rename_choice(choice, files, file_ops, filelist, update_callback) if choice else None
            )
        except Exception as e:
            logger.error(f"Error showing bulk rename dialog: {e}")
            self.show_message(f"Bulk rename dialog error: {e}", type="error")
    
    # Property for SetupScreen
    @property
    def SetupScreen(self):
        """Get setup screen class - Imported here to avoid circular dependency"""
        from ..ui.setup_screen import PilotFSSetup # <--- ADD THIS LINE HERE
        return PilotFSSetup