from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from enigma import eServiceReference, eServiceCenter, getDesktop, eTimer
import os
import logging

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class MediaPlayer(Screen):
    """Enhanced Media Player with playlist support and exit confirmation"""
    
    def __init__(self, session, file_path, playlist=None):
        Screen.__init__(self, session)
        self.file_path = file_path
        self.playlist = playlist or []
        self.current_index = 0
        
        # Find current file in playlist
        if self.playlist:
            try:
                self.current_index = self.playlist.index(file_path)
            except ValueError:
                self.current_index = 0
        
        # Get screen dimensions
        w, h = getDesktop(0).size().width(), getDesktop(0).size().height()
        
        self.skin = f"""
            <screen name="MediaPlayer" position="0,0" size="{w},{h}" backgroundColor="#000000" flags="wfNoBorder">
                <widget name="video" position="0,0" size="{w},{h}" zPosition="1" />
                <eLabel position="0,{h-100}" size="{w},100" backgroundColor="#1a1a1a" zPosition="2" />
                <widget name="title" position="20,{h-90}" size="{w-40},40" font="Regular;24" halign="left" transparent="1" foregroundColor="#ffffff" />
                <widget name="controls" position="20,{h-45}" size="{w-40},30" font="Regular;18" halign="left" transparent="1" foregroundColor="#ffff00" />
                <widget name="playlist_info" position="20,20" size="400,100" font="Regular;18" halign="left" transparent="1" foregroundColor="#00ffff" zPosition="3" />
            </screen>
        """
        
        # Create widgets
        self["title"] = Label("")
        self["controls"] = Label("")
        self["playlist_info"] = Label("")
        
        self["actions"] = ActionMap(["OkCancelActions", "MediaPlayerActions", "ColorActions"], 
            {
                "cancel": self.exit_confirmation,  # EXIT button
                "ok": self.toggle_play_pause,
                "playpause": self.toggle_play_pause,
                "stop": self.stop_playback,
                "pause": self.pause_playback,
                "play": self.play_playback,
                "previous": self.previous_track,
                "next": self.next_track,
                "red": self.stop_playback,
                "green": self.toggle_play_pause,
                "yellow": self.previous_track,
                "blue": self.next_track,
                "info": self.show_media_info,
                "text": self.toggle_playlist_info,
                "audio": self.toggle_audio_track,
                "video": self.toggle_subtitle,
                "menu": self.show_player_menu,
            }, -1)
        
        # Track playback state
        self.is_playing = False
        self.is_paused = False
        
        # Auto-hide playlist info timer
        self.info_timer = eTimer()
        self.info_timer.callback.append(self.hide_playlist_info)
        self.info_visible = False
        
        # Start playback
        self.onLayoutFinish.append(self.start_playback)
        
        # Set initial title
        self.update_title()
    
    def start_playback(self):
        """Start playing the media file"""
        try:
            logger.info(f"Starting playback: {self.file_path}")
            
            # Create service reference
            service_ref = eServiceReference(4097, 0, self.file_path)
            service_ref.setName(os.path.basename(self.file_path))
            
            # Try to play through InfoBar
            try:
                from Screens.InfoBar import InfoBar
                if InfoBar.instance:
                    InfoBar.instance.playService(service_ref)
                    self.is_playing = True
                    logger.info("Playback started via InfoBar")
            except ImportError:
                logger.warning("InfoBar not available")
                # Fallback to direct playback
                try:
                    from Screens.InfoBar import MoviePlayer
                    self.session.open(MoviePlayer, service_ref)
                    self.is_playing = True
                except:
                    logger.error("MoviePlayer also not available")
            
            # Update controls display
            self.update_controls()
            
            # Show playlist info if available
            if self.playlist and len(self.playlist) > 1:
                self.show_playlist_info()
                
        except Exception as e:
            logger.error(f"Playback error: {e}")
            from Screens.MessageBox import MessageBox
            self.session.open(MessageBox, f"Playback error: {e}", MessageBox.TYPE_ERROR)
            self.close()
    
    def update_title(self):
        """Update window title"""
        filename = os.path.basename(self.file_path)
        if self.playlist and len(self.playlist) > 1:
            title = f"🎵 {filename} ({self.current_index + 1}/{len(self.playlist)})"
        else:
            title = f"🎵 {filename}"
        self.setTitle(title)
        self["title"].setText(title)
    
    def update_controls(self):
        """Update controls display"""
        if self.playlist and len(self.playlist) > 1:
            controls = "EXIT:Exit  OK:Pause  ◀️YEL:Prev  ▶️BLUE:Next  RED:Stop  INFO:Info"
        else:
            controls = "EXIT:Exit  OK:Pause  RED:Stop  INFO:Media Info"
        self["controls"].setText(controls)
    
    def show_playlist_info(self):
        """Show playlist information overlay"""
        if not self.playlist or len(self.playlist) <= 1:
            return
        
        info = f"🎵 Playlist Mode\n\n"
        info += f"Track: {self.current_index + 1}/{len(self.playlist)}\n"
        info += f"Current: {os.path.basename(self.file_path)}\n"
        
        # Show next track if available
        if self.current_index + 1 < len(self.playlist):
            next_track = os.path.basename(self.playlist[self.current_index + 1])
            info += f"Next: {next_track}"
        
        self["playlist_info"].setText(info)
        self.info_visible = True
        
        # Auto-hide after 5 seconds
        self.info_timer.start(5000, True)
    
    def hide_playlist_info(self):
        """Hide playlist info overlay"""
        self["playlist_info"].setText("")
        self.info_visible = False
    
    def toggle_playlist_info(self):
        """Toggle playlist info display"""
        if self.info_visible:
            self.hide_playlist_info()
        else:
            self.show_playlist_info()
    
    def exit_confirmation(self):
        """Show exit confirmation dialog"""
        from Screens.MessageBox import MessageBox
        
        # If playing from playlist, show different message
        if self.playlist and len(self.playlist) > 1:
            message = "Exit media player?\n\nStop playing playlist and exit?"
        else:
            message = "Exit media player?"
        
        self.session.openWithCallback(
            self.exit_confirmed,
            MessageBox,
            message,
            MessageBox.TYPE_YESNO
        )
    
    def exit_confirmed(self, confirmed):
        """Handle exit confirmation result"""
        if confirmed:
            self.stop_playback()
            self.close()
        # If not confirmed, continue playing
    
    def stop_playback(self):
        """Stop media playback"""
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar.instance and InfoBar.instance.session:
                InfoBar.instance.stopService()
                self.is_playing = False
                logger.info("Playback stopped")
        except:
            pass
    
    def toggle_play_pause(self):
        """Toggle between play and pause"""
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar.instance:
                if self.is_paused:
                    InfoBar.instance.unPauseService()
                    self.is_paused = False
                    logger.info("Playback resumed")
                else:
                    InfoBar.instance.pauseService()
                    self.is_paused = True
                    logger.info("Playback paused")
        except:
            pass
    
    def pause_playback(self):
        """Pause playback"""
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar.instance:
                InfoBar.instance.pauseService()
                self.is_paused = True
                logger.info("Playback paused")
        except:
            pass
    
    def play_playback(self):
        """Resume playback"""
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar.instance:
                InfoBar.instance.unPauseService()
                self.is_paused = False
                logger.info("Playback resumed")
        except:
            pass
    
    def previous_track(self):
        """Play previous track in playlist"""
        if self.playlist and len(self.playlist) > 1:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.file_path = self.playlist[self.current_index]
            logger.info(f"Previous track: {self.file_path}")
            self.update_title()
            self.stop_playback()
            self.start_playback()
    
    def next_track(self):
        """Play next track in playlist"""
        if self.playlist and len(self.playlist) > 1:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.file_path = self.playlist[self.current_index]
            logger.info(f"Next track: {self.file_path}")
            self.update_title()
            self.stop_playback()
            self.start_playback()
    
    def show_media_info(self):
        """Show media file information"""
        try:
            info = f"📄 Media Information\n\n"
            info += f"File: {os.path.basename(self.file_path)}\n"
            info += f"Path: {os.path.dirname(self.file_path)}\n"
            
            # Get file size
            try:
                size = os.path.getsize(self.file_path)
                from ..utils.formatters import format_size
                info += f"Size: {format_size(size)}\n"
            except:
                info += f"Size: Unknown\n"
            
            # Get file extension
            ext = os.path.splitext(self.file_path)[1].lower()
            info += f"Type: {ext.upper()[1:] if ext else 'Unknown'}\n"
            
            if self.playlist and len(self.playlist) > 1:
                info += f"\n🎵 Playlist: {self.current_index + 1}/{len(self.playlist)}\n"
                info += f"Total tracks: {len(self.playlist)}\n"
            
            from Screens.MessageBox import MessageBox
            self.session.open(MessageBox, info, MessageBox.TYPE_INFO, timeout=5)
            
        except Exception as e:
            logger.error(f"Error showing media info: {e}")
    
    def toggle_audio_track(self):
        """Toggle audio tracks (if available)"""
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar.instance:
                # Try to cycle through audio tracks
                InfoBar.instance.audioSelection()
                logger.info("Audio track toggled")
        except:
            pass
    
    def toggle_subtitle(self):
        """Toggle subtitles (if available)"""
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar.instance:
                # Try to toggle subtitles
                InfoBar.instance.subtitleSelection()
                logger.info("Subtitle toggled")
        except:
            pass
    
    def show_player_menu(self):
        """Show player options menu"""
        from Screens.ChoiceBox import ChoiceBox
        
        menu_items = []
        
        # Always available options
        menu_items.append(("📊 Media Information", "info"))
        menu_items.append(("🎵 Toggle Playlist Info", "toggle_info"))
        
        if self.playlist and len(self.playlist) > 1:
            menu_items.append(("🔄 Restart Playlist", "restart"))
            menu_items.append(("🔀 Shuffle Playlist", "shuffle"))
            menu_items.append(("📋 Show All Tracks", "list"))
        
        # Audio/Video options
        menu_items.append(("🔊 Audio Track", "audio"))
        menu_items.append(("📝 Subtitles", "subtitle"))
        
        # Playback options
        if self.is_paused:
            menu_items.append(("▶️ Resume Playback", "resume"))
        else:
            menu_items.append(("⏸️ Pause Playback", "pause"))
        
        menu_items.append(("⏹️ Stop Playback", "stop"))
        menu_items.append(("🚪 Exit Player", "exit"))
        
        self.session.openWithCallback(
            self.handle_player_menu,
            ChoiceBox,
            title="🎵 Player Options",
            list=menu_items
        )
    
    def handle_player_menu(self, choice):
        """Handle player menu selection"""
        if not choice:
            return
        
        action = choice[1]
        
        try:
            if action == "info":
                self.show_media_info()
            elif action == "toggle_info":
                self.toggle_playlist_info()
            elif action == "restart":
                self.restart_playlist()
            elif action == "shuffle":
                self.shuffle_playlist()
            elif action == "list":
                self.show_all_tracks()
            elif action == "audio":
                self.toggle_audio_track()
            elif action == "subtitle":
                self.toggle_subtitle()
            elif action == "resume":
                self.play_playback()
            elif action == "pause":
                self.pause_playback()
            elif action == "stop":
                self.stop_playback()
            elif action == "exit":
                self.exit_confirmation()
        except Exception as e:
            logger.error(f"Error handling player menu: {e}")
    
    def restart_playlist(self):
        """Restart playlist from beginning"""
        if self.playlist and len(self.playlist) > 1:
            self.current_index = 0
            self.file_path = self.playlist[self.current_index]
            self.update_title()
            self.stop_playback()
            self.start_playback()
    
    def shuffle_playlist(self):
        """Shuffle playlist"""
        if self.playlist and len(self.playlist) > 1:
            import random
            current_file = self.playlist[self.current_index]
            
            # Shuffle the playlist
            shuffled = self.playlist.copy()
            random.shuffle(shuffled)
            
            # Ensure current file stays at current position
            if current_file in shuffled:
                shuffled.remove(current_file)
                shuffled.insert(self.current_index, current_file)
            
            self.playlist = shuffled
            self.show_playlist_info()
            logger.info("Playlist shuffled")
    
    def show_all_tracks(self):
        """Show all tracks in playlist"""
        if not self.playlist or len(self.playlist) <= 1:
            return
        
        from Screens.MessageBox import MessageBox
        
        tracks_info = "🎵 Playlist Tracks\n\n"
        for i, track in enumerate(self.playlist):
            track_name = os.path.basename(track)
            if i == self.current_index:
                tracks_info += f"▶️ {i + 1:02d}. {track_name}\n"
            else:
                tracks_info += f"   {i + 1:02d}. {track_name}\n"
        
        tracks_info += f"\nTotal: {len(self.playlist)} tracks"
        
        self.session.open(MessageBox, tracks_info, MessageBox.TYPE_INFO)
    
    def close(self):
        """Clean up and close"""
        # Stop info timer
        if self.info_timer.isActive():
            self.info_timer.stop()
        
        # Stop playback
        self.stop_playback()
        
        # Close screen
        Screen.close(self)