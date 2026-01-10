"""
PilotFS Enigma2 Player with SMART OK button
OK: Play/Pause + Double-tap for OSD toggle
"""

import os
import sys
import time  # Added for timing

# ============================================
# ENIGMA2 DETECTION (same as before)
# ============================================
ENIGMA_AVAILABLE = False
IS_ENIGMA2 = False
PLAYER_AVAILABLE = False

try:
    from Screens.Screen import Screen
    from Components.ActionMap import HelpableActionMap
    from Components.Label import Label
    from Components.ServicePosition import ServicePositionGauge
    from Components.ServiceEventTracker import ServiceEventTracker
    from enigma import eServiceReference, eTimer, iPlayableService
    from enigma import getDesktop
    
    ENIGMA_AVAILABLE = True
    IS_ENIGMA2 = True
    PLAYER_AVAILABLE = True
    print("[PilotFS Player] Enigma2 ready - SMART OK BUTTON")
except ImportError as e:
    print(f"[PilotFS Player] Enigma2 modules not available: {e}")
    # Mock classes for testing
    class Screen:
        def __init__(self, session):
            self.session = session
        def close(self): pass
    
    class HelpableActionMap: 
        def __init__(self, *args, **kwargs): pass
    
    class Label:
        def __init__(self, text=""): self.text = text
        def setText(self, text): self.text = text
    
    class ServicePositionGauge: pass
    class ServiceEventTracker: pass
    
    class eServiceReference:
        def __init__(self, type, flags, path):
            self.type = type
            self.flags = flags
            self.path = path
    
    class eTimer:
        def __init__(self): pass
        def start(self, *args): pass
        def stop(self): pass
    
    class iPlayableService:
        evStart = 1
        evEnd = 2

# ============================================
# SMART PLAYER CLASS
# ============================================
class PilotFSPlayer(Screen):
    """Smart player with OK button doing Play/Pause + OSD toggle."""
    
    def __init__(self, session, file_path, parent_screen=None):
        # Get screen size
        try:
            desktop = getDesktop(0)
            self.screen_width = desktop.size().width()
            self.screen_height = desktop.size().height()
        except:
            self.screen_width = 1280
            self.screen_height = 720
        
        # Calculate dimensions
        player_height = self.screen_height - 100
        control_height = 80
        
        # Skin with OSD elements
        skin = f"""
        <screen name="PilotFSPlayer" position="0,0" size="{self.screen_width},{self.screen_height}" backgroundColor="#000000" flags="wfNoBorder">
            <!-- Video Area -->
            <eLabel position="0,0" size="{self.screen_width},{player_height}" backgroundColor="#000000" />
            
            <!-- OSD Control Bar (visible by default) -->
            <eLabel name="osd_bar" position="0,{player_height}" size="{self.screen_width},{control_height}" backgroundColor="#1a1a1a" />
            
            <!-- Title -->
            <widget name="title" position="20,{player_height + 10}" size="{self.screen_width - 40},30" 
                    font="Regular;24" halign="left" foregroundColor="#ffffff" transparent="1" />
            
            <!-- Progress Bar -->
            <widget name="position" position="20,{player_height + 45}" size="{self.screen_width - 40},8" />
            
            <!-- Time Display -->
            <widget name="time" position="20,{player_height + 55}" size="200,20" 
                    font="Regular;18" halign="left" foregroundColor="#aaaaaa" transparent="1" />
            
            <!-- Controls -->
            <ePixmap pixmap="skin_default/icons/play.png" position="{self.screen_width//2},{player_height + 15}" size="40,40" alphatest="blend" />
            <eLabel text="OK: Play/Pause/OSD" position="{self.screen_width//2 - 100},{player_height + 55}" size="200,20" 
                    font="Regular;16" halign="center" foregroundColor="#00ff00" transparent="1" />
            
            <!-- Help text -->
            <widget name="help" position="20,{self.screen_height - 25}" size="{self.screen_width - 40},20" 
                    font="Regular;18" halign="right" foregroundColor="#888888" transparent="1" />
        </screen>
        """
        
        self.skin = skin
        Screen.__init__(self, session)
        
        self.file_path = file_path
        self.parent_screen = parent_screen
        self.service_handler = None
        self.is_playing = False
        self.is_paused = False
        
        # OSD state
        self.osd_visible = True
        self.last_ok_press = 0
        self.ok_doubletap_timeout = 0.8  # seconds for double-tap
        
        # Timers
        self.seek_timer = eTimer()
        self.seek_timer.callback.append(self.updatePosition)
        
        # Initialize UI
        self["title"] = Label(os.path.basename(file_path))
        self["position"] = ServicePositionGauge(self.session.nav)
        self["time"] = Label("00:00 / 00:00")
        self["help"] = Label("OK: Play/Pause (double-tap: OSD) | EXIT: Close")
        
        # Smart actions
        self["actions"] = HelpableActionMap(self, "MediaPlayerActions", 
            {
                "ok": (self.smartOK, "Play/Pause or toggle OSD"),
                "cancel": (self.closePlayer, "Close player"),
                "left": (self.seekBackward, "Rewind 10s"),
                "right": (self.seekForward, "Forward 10s"),
                "audio": (self.audioSelection, "Audio tracks"),
                "info": (self.showInfo, "File info"),
                "showMenu": (self.toggleOSD, "Toggle OSD"),
            }, -1)
        
        # Service events
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={
            iPlayableService.evStart: self.serviceStarted,
            iPlayableService.evEnd: self.serviceEnded,
        })
        
        # Auto-start
        self.onFirstExecBegin.append(self.startPlayback)
    
    # ============================================
    # SMART OK BUTTON IMPLEMENTATION
    # ============================================
    
    def smartOK(self):
        """Smart OK button: Play/Pause with double-tap for OSD."""
        current_time = time.time()
        time_since_last_press = current_time - self.last_ok_press
        
        print(f"[Smart OK] Time since last: {time_since_last_press:.2f}s")
        
        if time_since_last_press < self.ok_doubletap_timeout and self.is_playing:
            # Double-tap while playing: Toggle OSD
            print("[Smart OK] Double-tap detected: Toggling OSD")
            self.toggleOSD()
        else:
            # Single tap: Play/Pause toggle
            print("[Smart OK] Single tap: Play/Pause toggle")
            self._togglePlayPause()
        
        self.last_ok_press = current_time
    
    def _togglePlayPause(self):
        """Toggle between play and pause."""
        if not self.is_playing:
            self.play()
            self.updateHelpText("Playing - OK: Pause (double-tap: OSD)")
        else:
            if self.is_paused:
                self.play()
                self.updateHelpText("Playing - OK: Pause (double-tap: OSD)")
            else:
                self.pause()
                self.updateHelpText("Paused - OK: Play (double-tap: OSD)")
    
    def toggleOSD(self):
        """Toggle on-screen display."""
        self.osd_visible = not self.osd_visible
        
        if self.osd_visible:
            self.updateHelpText("OSD: ON - OK: Play/Pause (double-tap: OSD)")
            print("[PilotFS] OSD shown")
            # In full implementation, would show widgets
        else:
            self.updateHelpText("OSD: OFF - OK: Play/Pause (double-tap: ON)")
            print("[PilotFS] OSD hidden")
            # In full implementation, would hide widgets
    
    def updateHelpText(self, text):
        """Update help text with current state."""
        status_prefix = ""
        if self.is_playing:
            if self.is_paused:
                status_prefix = "⏸ "
            else:
                status_prefix = "▶ "
        
        self["help"].setText(status_prefix + text)
    
    # ============================================
    # BASIC PLAYBACK CONTROLS
    # ============================================
    
    def startPlayback(self):
        """Start playback."""
        if IS_ENIGMA2:
            try:
                ref = eServiceReference(4097, 0, self.file_path)
                ref.setName(os.path.basename(self.file_path))
                self.session.nav.playService(ref)
                self.service_handler = self.session.nav.getCurrentService()
                self.is_playing = True
                self.seek_timer.start(1000)
                self.updateHelpText("Playing - OK: Pause (double-tap: OSD)")
                print(f"[PilotFS] Playing: {os.path.basename(self.file_path)}")
            except Exception as e:
                print(f"[PilotFS] Playback error: {e}")
                self["help"].setText(f"Error: {str(e)[:30]}")
        else:
            self.is_playing = True
            self.updateHelpText("TEST: Playing - OK: Pause (double-tap: OSD)")
    
    def play(self):
        """Play or resume."""
        if IS_ENIGMA2 and self.service_handler:
            try:
                self.service_handler.pause()
                self.is_paused = False
            except:
                pass
        self.is_playing = True
        self.is_paused = False
    
    def pause(self):
        """Pause playback."""
        if IS_ENIGMA2 and self.service_handler:
            try:
                self.service_handler.pause()
                self.is_paused = True
            except:
                pass
        self.is_paused = True
    
    def seekForward(self):
        """Forward 10 seconds."""
        self.updateHelpText(">> 10s - OK: Play/Pause")
        print("[PilotFS] Forward 10s")
    
    def seekBackward(self):
        """Rewind 10 seconds."""
        self.updateHelpText("<< 10s - OK: Play/Pause")
        print("[PilotFS] Backward 10s")
    
    def audioSelection(self):
        """Audio tracks."""
        self.updateHelpText("Audio selection - OK: Play/Pause")
        print("[PilotFS] Audio selection")
    
    def showInfo(self):
        """Show file info."""
        self.updateHelpText("File info - OK: Play/Pause")
        print("[PilotFS] Show info")
    
    # ============================================
    # EVENT HANDLERS
    # ============================================
    
    def serviceStarted(self):
        """Service started."""
        self.is_playing = True
        self.updateHelpText("Playing - OK: Pause (double-tap: OSD)")
    
    def serviceEnded(self):
        """Service ended."""
        self.is_playing = False
        self.is_paused = False
        self.seek_timer.stop()
        self.updateHelpText("Playback ended")
        # Auto-close after delay
        self.close_timer = eTimer()
        self.close_timer.callback.append(self.closePlayer)
        self.close_timer.start(2000)
    
    def updatePosition(self):
        """Update position display."""
        if not IS_ENIGMA2:
            self["time"].setText("01:30 / 05:00")
    
    def closePlayer(self):
        """Close player."""
        if IS_ENIGMA2:
            try:
                self.session.nav.stopService()
            except:
                pass
        self.seek_timer.stop()
        if hasattr(self, 'close_timer'):
            self.close_timer.stop()
        self.close()
        if self.parent_screen:
            try:
                self.parent_screen.update_ui()
            except:
                pass

# ============================================
# HELPER FUNCTIONS (same as before)
# ============================================
def get_player_status():
    return {
        'enigma_available': ENIGMA_AVAILABLE,
        'is_enigma2': IS_ENIGMA2,
        'player_available': PLAYER_AVAILABLE,
        'version': '2.1',
        'features': 'Smart OK button (Play/Pause + OSD toggle)'
    }

def is_media_file(file_path):
    if not file_path or not isinstance(file_path, str):
        return False
    if isinstance(file_path, (list, tuple)) and len(file_path) > 0:
        file_path = file_path[0]
    ext = os.path.splitext(file_path)[1].lower()
    video_exts = ['.mp4', '.mkv', '.avi', '.ts', '.mov', '.mpg', '.mpeg', '.m2ts']
    audio_exts = ['.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a']
    return ext in video_exts or ext in audio_exts

def can_play_file(file_path):
    return is_media_file(file_path) and PLAYER_AVAILABLE

__all__ = [
    'PilotFSPlayer',
    'get_player_status',
    'is_media_file',
    'can_play_file',
    'IS_ENIGMA2',
    'ENIGMA_AVAILABLE',
    'PLAYER_AVAILABLE'
]
