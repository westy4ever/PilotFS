from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from enigma import getDesktop, ePicLoad
import os
import glob
import logging

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class ImageViewer(Screen):
    """Enhanced Image Viewer with slideshow and exit confirmation"""
    
    def __init__(self, session, image_path=None, image_list=None, directory=None):
        Screen.__init__(self, session)
        
        # Get screen dimensions
        w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
        
        self.image_path = image_path
        self.directory = directory
        
        # Get image list
        self.image_list = self.get_image_list(image_path, image_list, directory)
        self.current_index = 0
        
        # Find current index
        if self.image_path and self.image_list:
            try:
                self.current_index = self.image_list.index(self.image_path)
            except ValueError:
                self.current_index = 0
        
        # Create skin
        self.skin = """
        <screen name="ImageViewer" position="0,0" size="%d,%d" backgroundColor="#000000" flags="wfNoBorder">
            <widget name="image" position="0,0" size="%d,%d" alphatest="on" />
            <eLabel position="0,%d" size="%d,80" backgroundColor="#1a1a1a" zPosition="-1" />
            <widget name="info" position="10,%d" size="%d,40" font="Regular;20" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="help" position="10,%d" size="%d,30" font="Regular;18" halign="left" transparent="1" foregroundColor="#ffff00" />
            <widget name="controls" position="%d,%d" size="400,80" font="Regular;18" halign="right" transparent="1" foregroundColor="#00ffff" />
        </screen>""" % (w, h, w, h-80, h-80, w, h-75, w-20, h-40, w-20, w-410, h-75)
        
        # Create widgets
        self["image"] = Pixmap()
        self["info"] = Label("")
        self["help"] = Label("")
        self["controls"] = Label("")
        
        # Set help text based on number of images
        if len(self.image_list) > 1:
            self["help"].setText("EXIT:Close  LEFT:Prev  RIGHT:Next  OK:Fullscreen")
            self["controls"].setText("EXIT:Exit  ◀:Prev  ▶:Next  OK:Options")
        else:
            self["help"].setText("EXIT:Close  OK:Fullscreen")
            self["controls"].setText("EXIT:Exit  OK:Options")
        
        # Initialize ePicLoad
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.update_image)
        
        # Track viewer state
        self.fullscreen = False
        self.zoom_level = 1.0
        self.rotation = 0
        
        # Setup actions
        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions"], 
        {
            "cancel": self.exit_confirmation,  # EXIT button
            "ok": self.toggle_fullscreen,
            "left": self.prev_image,
            "right": self.next_image,
            "up": self.zoom_in,
            "down": self.zoom_out,
            "red": self.exit_confirmation,
            "green": self.zoom_in,
            "yellow": self.zoom_out,
            "blue": self.rotate_image,
            "menu": self.show_options,
        }, -1)
        
        # Load image
        self.onLayoutFinish.append(self.load_image)
    
    def get_image_list(self, image_path, image_list, directory):
        """Get list of images to display"""
        if image_list and len(image_list) > 0:
            return image_list
        
        # If directory is provided, get all images from that directory
        if directory and os.path.isdir(directory):
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
            all_files = []
            for ext in image_extensions:
                all_files.extend(glob.glob(os.path.join(directory, f"*{ext}")))
                all_files.extend(glob.glob(os.path.join(directory, f"*{ext.upper()}")))
            return sorted(all_files)
        
        # If only single image path is provided
        if image_path and os.path.isfile(image_path):
            # Get all images in the same directory
            dir_path = os.path.dirname(image_path)
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
            all_files = []
            for ext in image_extensions:
                all_files.extend(glob.glob(os.path.join(dir_path, f"*{ext}")))
                all_files.extend(glob.glob(os.path.join(dir_path, f"*{ext.upper()}")))
            return sorted(all_files)
        
        return []
    
    def load_image(self):
        """Load the image"""
        if not self.image_path or not self.image_list:
            self["info"].setText("No image selected!")
            return
        
        try:
            if not os.path.isfile(self.image_path):
                self["info"].setText("Image not found!")
                return
            
            file_name = os.path.basename(self.image_path)
            
            # Show image counter if we have a list
            if len(self.image_list) > 1:
                info_text = "[%d/%d] %s" % (self.current_index + 1, len(self.image_list), file_name)
            else:
                info_text = file_name
            
            # Add zoom and rotation info
            if self.zoom_level != 1.0:
                info_text += f" | Zoom: {self.zoom_level:.1f}x"
            if self.rotation != 0:
                info_text += f" | Rotate: {self.rotation}°"
            
            self["info"].setText(info_text)
            
            # Get screen dimensions
            w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
            
            # Calculate display size based on zoom
            display_w = int(w * self.zoom_level)
            display_h = int((h-80) * self.zoom_level)
            
            # Load image with current settings
            self.picload.setPara([display_w, display_h-80, 1, 1, 0, 0, "#000000"])
            self.picload.startDecode(self.image_path)
            
        except Exception as e:
            logger.error("Error loading image: %s" % str(e))
            self["info"].setText("Error: %s" % str(e))
    
    def update_image(self, picInfo=None):
        """Update the image display"""
        try:
            ptr = self.picload.getData()
            if ptr:
                self["image"].instance.setPixmap(ptr)
                self["image"].show()
                
                # Center the image
                if self.zoom_level > 1.0:
                    w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
                    self["image"].instance.setPosition((w - self["image"].instance.size().width()) // 2, 
                                                      (h - 80 - self["image"].instance.size().height()) // 2)
        except Exception as e:
            logger.error("Error updating image: %s" % str(e))
    
    def prev_image(self):
        """Load previous image in slideshow"""
        if len(self.image_list) <= 1:
            self["help"].setText("Only one image in folder")
            return
        
        # Calculate previous index
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.image_list) - 1
        
        self.image_path = self.image_list[self.current_index]
        self.load_image()
    
    def next_image(self):
        """Load next image in slideshow"""
        if len(self.image_list) <= 1:
            self["help"].setText("Only one image in folder")
            return
        
        # Calculate next index
        self.current_index += 1
        if self.current_index >= len(self.image_list):
            self.current_index = 0
        
        self.image_path = self.image_list[self.current_index]
        self.load_image()
    
    def exit_confirmation(self):
        """Show exit confirmation dialog"""
        from Screens.MessageBox import MessageBox
        
        # If viewing multiple images, show different message
        if len(self.image_list) > 1:
            message = "Exit image viewer?\n\nStop slideshow and exit?"
        else:
            message = "Exit image viewer?"
        
        self.session.openWithCallback(
            self.exit_confirmed,
            MessageBox,
            message,
            MessageBox.TYPE_YESNO
        )
    
    def exit_confirmed(self, confirmed):
        """Handle exit confirmation result"""
        if confirmed:
            self.close()
        # If not confirmed, stay in viewer
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        from Screens.ChoiceBox import ChoiceBox
        
        menu_items = [
            ("🔄 Toggle Fullscreen", "fullscreen"),
            ("➕ Zoom In", "zoom_in"),
            ("➖ Zoom Out", "zoom_out"),
            ("↪️ Rotate Right", "rotate_right"),
            ("↩️ Rotate Left", "rotate_left"),
            ("🔄 Reset View", "reset"),
            ("📊 Image Info", "info"),
            ("🚪 Exit Viewer", "exit"),
        ]
        
        self.session.openWithCallback(
            self.handle_viewer_options,
            ChoiceBox,
            title="🖼️ Image Viewer Options",
            list=menu_items
        )
    
    def handle_viewer_options(self, choice):
        """Handle viewer options selection"""
        if not choice:
            return
        
        action = choice[1]
        
        try:
            if action == "fullscreen":
                self.toggle_fullscreen_mode()
            elif action == "zoom_in":
                self.zoom_in()
            elif action == "zoom_out":
                self.zoom_out()
            elif action == "rotate_right":
                self.rotate_image(90)
            elif action == "rotate_left":
                self.rotate_image(-90)
            elif action == "reset":
                self.reset_view()
            elif action == "info":
                self.show_image_info()
            elif action == "exit":
                self.exit_confirmation()
        except Exception as e:
            logger.error(f"Error handling viewer options: {e}")
    
    def toggle_fullscreen_mode(self):
        """Toggle between fullscreen and normal mode"""
        self.fullscreen = not self.fullscreen
        
        # Update skin for fullscreen mode
        w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
        
        if self.fullscreen:
            # Hide info bar and controls
            self["info"].hide()
            self["help"].hide()
            self["controls"].hide()
            self.skin = """
            <screen name="ImageViewer" position="0,0" size="%d,%d" backgroundColor="#000000" flags="wfNoBorder">
                <widget name="image" position="0,0" size="%d,%d" alphatest="on" />
            </screen>""" % (w, h, w, h)
            self["help"].setText("EXIT:Exit  OK:Options  ◀:Prev  ▶:Next")
        else:
            # Show info bar and controls
            self["info"].show()
            self["help"].show()
            self["controls"].show()
            self.skin = """
            <screen name="ImageViewer" position="0,0" size="%d,%d" backgroundColor="#000000" flags="wfNoBorder">
                <widget name="image" position="0,0" size="%d,%d" alphatest="on" />
                <eLabel position="0,%d" size="%d,80" backgroundColor="#1a1a1a" zPosition="-1" />
                <widget name="info" position="10,%d" size="%d,40" font="Regular;20" halign="left" transparent="1" foregroundColor="#ffffff" />
                <widget name="help" position="10,%d" size="%d,30" font="Regular;18" halign="left" transparent="1" foregroundColor="#ffff00" />
                <widget name="controls" position="%d,%d" size="400,80" font="Regular;18" halign="right" transparent="1" foregroundColor="#00ffff" />
            </screen>""" % (w, h, w, h-80, h-80, w, h-75, w-20, h-40, w-20, w-410, h-75)
        
        # Reload the skin
        self.load_image()
    
    def zoom_in(self):
        """Zoom in on image"""
        if self.zoom_level < 3.0:  # Max 3x zoom
            self.zoom_level += 0.2
            self.load_image()
    
    def zoom_out(self):
        """Zoom out from image"""
        if self.zoom_level > 0.4:  # Min 0.4x zoom
            self.zoom_level -= 0.2
            self.load_image()
    
    def rotate_image(self, degrees=90):
        """Rotate image by specified degrees"""
        self.rotation = (self.rotation + degrees) % 360
        
        # Update ePicLoad parameters for rotation
        w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
        display_w = int(w * self.zoom_level)
        display_h = int((h-80) * self.zoom_level)
        
        # Set rotation parameter (0=0°, 1=90°, 2=180°, 3=270°)
        rotation_code = self.rotation // 90
        
        self.picload.setPara([display_w, display_h-80, 1, 1, rotation_code, 0, "#000000"])
        self.picload.startDecode(self.image_path)
        
        # Update info display
        self.load_image()
    
    def reset_view(self):
        """Reset zoom and rotation to defaults"""
        self.zoom_level = 1.0
        self.rotation = 0
        self.load_image()
    
    def show_image_info(self):
        """Show detailed image information"""
        try:
            import os
            from datetime import datetime
            
            info = "📄 Image Information\n\n"
            info += f"File: {os.path.basename(self.image_path)}\n"
            info += f"Path: {os.path.dirname(self.image_path)}\n"
            
            # Get file size
            try:
                size = os.path.getsize(self.image_path)
                from ..utils.formatters import format_size
                info += f"Size: {format_size(size)}\n"
            except:
                info += f"Size: Unknown\n"
            
            # Get file extension and type
            ext = os.path.splitext(self.image_path)[1].lower()
            image_types = {
                '.jpg': 'JPEG Image',
                '.jpeg': 'JPEG Image',
                '.png': 'PNG Image',
                '.gif': 'GIF Image',
                '.bmp': 'Bitmap Image',
                '.tiff': 'TIFF Image',
                '.webp': 'WebP Image'
            }
            info += f"Type: {image_types.get(ext, ext.upper()[1:] if ext else 'Unknown')}\n"
            
            # Get modification time
            try:
                mtime = os.path.getmtime(self.image_path)
                info += f"Modified: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            except:
                info += f"Modified: Unknown\n"
            
            if len(self.image_list) > 1:
                info += f"\n📋 Slideshow: {self.current_index + 1}/{len(self.image_list)}\n"
                info += f"Total images: {len(self.image_list)}\n"
            
            info += f"\n🔍 View Settings:\n"
            info += f"Zoom: {self.zoom_level:.1f}x\n"
            info += f"Rotation: {self.rotation}°\n"
            info += f"Fullscreen: {'Yes' if self.fullscreen else 'No'}\n"
            
            from Screens.MessageBox import MessageBox
            self.session.open(MessageBox, info, MessageBox.TYPE_INFO)
            
        except Exception as e:
            logger.error(f"Error showing image info: {e}")
    
    def show_options(self):
        """Show viewer options menu"""
        self.toggle_fullscreen()
    
    def close(self):
        """Clean up and close viewer"""
        # Stop any pending operations
        try:
            self.picload.PictureData.get().remove(self.update_image)
        except:
            pass
        
        # Close screen
        Screen.close(self)