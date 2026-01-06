from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from enigma import getDesktop, ePicLoad, eTimer, gRGB, RT_HALIGN_CENTER, RT_VALIGN_CENTER
import os

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class ImageViewer(Screen):
    """Advanced image viewer with zoom and rotate features"""
    
    def __init__(self, session, image_path):
        Screen.__init__(self, session)
        
        # Get screen dimensions
        w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
        
        self.image_path = image_path
        self.scale = 1.0
        self.rotation = 0
        self.position = [0, 0]
        
        # Create skin
        self.skin = """
        <screen name="ImageViewer" position="0,0" size="%d,%d" backgroundColor="#000000" flags="wfNoBorder">
            <widget name="image" position="0,0" size="%d,%d" alphatest="on" />
            <eLabel position="0,%d" size="%d,100" backgroundColor="#1a1a1a" />
            <widget name="info" position="20,%d" size="%d,30" font="Regular;22" halign="center" transparent="1" foregroundColor="#ffffff" />
            <widget name="help" position="20,%d" size="%d,30" font="Regular;18" halign="center" transparent="1" foregroundColor="#aaaaaa" />
        </screen>""" % (w, h, w, h-100, h-100, w, h-90, w-40, h-50, w-40)
        
        # Create widgets
        self["image"] = Pixmap()
        self["info"] = Label("")
        self["help"] = Label("GREEN:Zoom+ YELLOW:Zoom- BLUE:Rotate EXIT:Close")
        
        # Initialize ePicLoad
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.update_image)
        
        # Setup actions
        self.setup_actions()
        
        # Load image
        self.onLayoutFinish.append(self.load_image)
    
    def setup_actions(self):
        """Setup key mappings"""
        self["actions"] = ActionMap([
            "OkCancelActions", "ColorActions", "DirectionActions", "MenuActions"
        ], {
            "cancel": self.key_exit,
            "red": self.key_exit,
            "green": self.zoom_in,
            "yellow": self.zoom_out,
            "blue": self.rotate,
            "up": self.pan_up,
            "down": self.pan_down,
            "left": self.pan_left,
            "right": self.pan_right,
            "menu": self.show_options,
            "ok": self.reset_view,
        }, -1)
    
    def load_image(self):
        """Load the image"""
        try:
            if not os.path.isfile(self.image_path):
                self["info"].setText("Image not found!")
                return
            
            file_name = os.path.basename(self.image_path)
            try:
                size = os.path.getsize(self.image_path)
                from ..utils.formatters import format_size
                size_str = format_size(size)
            except:
                size_str = "Unknown"
            
            self["info"].setText("%s (%s)" % (file_name, size_str))
            
            # Get screen dimensions
            w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
            
            # Load image
            self.picload.setPara([w, h-100, 1, 1, False, 1, "#000000"])
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
        except Exception as e:
            logger.error("Error updating image: %s" % str(e))
    
    def zoom_in(self):
        """Zoom in"""
        self.scale = min(5.0, self.scale + 0.5)
        self["info"].setText("Zoom: %.1fx" % self.scale)
    
    def zoom_out(self):
        """Zoom out"""
        self.scale = max(0.5, self.scale - 0.5)
        self["info"].setText("Zoom: %.1fx" % self.scale)
    
    def rotate(self):
        """Rotate image"""
        self.rotation = (self.rotation + 90) % 360
        self["info"].setText("Rotation: %d degrees" % self.rotation)
    
    def pan_up(self):
        """Pan up"""
        self.position[1] -= 20
    
    def pan_down(self):
        """Pan down"""
        self.position[1] += 20
    
    def pan_left(self):
        """Pan left"""
        self.position[0] -= 20
    
    def pan_right(self):
        """Pan right"""
        self.position[0] += 20
    
    def reset_view(self):
        """Reset view"""
        self.scale = 1.0
        self.rotation = 0
        self.position = [0, 0]
        self.load_image()
    
    def show_options(self):
        """Show options menu"""
        menu = [
            ("Reset view", "reset"),
            ("Image info", "info"),
            ("Close viewer", "close")
        ]
        
        self.session.openWithCallback(self.options_callback, ChoiceBox, title="Image Options", list=menu)
    
    def options_callback(self, result):
        """Handle options"""
        if result is None:
            return
        
        if result[1] == "reset":
            self.reset_view()
        elif result[1] == "info":
            self.show_image_info()
        elif result[1] == "close":
            self.key_exit()
    
    def show_image_info(self):
        """Show image info"""
        try:
            info = "File: %s\nPath: %s\nZoom: %.1fx\nRotation: %d" % (
                os.path.basename(self.image_path),
                self.image_path,
                self.scale,
                self.rotation
            )
            self.session.open(MessageBox, info, type=MessageBox.TYPE_INFO, timeout=10)
        except Exception as e:
            logger.error("Error showing info: %s" % str(e))
    
    def key_exit(self):
        """Exit viewer - FIXED VERSION"""
        # Try to use the dialogs module if available
        try:
            # Import here to avoid circular imports
            from .dialogs import Dialogs
            dialogs = Dialogs(self.session)
            dialogs.show_confirmation(
                "Exit image viewer?", 
                lambda confirmed: self.close() if confirmed else None
            )
        except ImportError as e:
            logger.warning("Cannot import Dialogs: %s" % str(e))
            # Fallback: exit directly
            self.close()
        except Exception as e:
            logger.error("Error in exit confirmation: %s" % str(e))
            self.close()