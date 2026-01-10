#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PilotFS Media Player Module
Handles audio and video playback with playlist support
"""

import os
import glob
from enigma import eServiceReference, iPlayableService
from Components.ActionMap import ActionMap
from Screens.InfoBar import MoviePlayer
class PilotFSMoviePlayer(MoviePlayer):
    """Custom MoviePlayer with exit confirmation"""
    
    def __init__(self, session, service, callback=None):
        MoviePlayer.__init__(self, session, service)
        self.exit_callback = callback
        
        # Override exit action
        self["actions"] = ActionMap(["MoviePlayerActions", "OkCancelActions"],
        {
            "cancel": self.ask_exit,
            "exit": self.ask_exit,
        }, -2)
    
    def ask_exit(self):
        """Ask for confirmation before exiting"""
        from Screens.MessageBox import MessageBox
        self.session.openWithCallback(
            self.exit_confirmed,
            MessageBox,
            "Exit media player?",
            MessageBox.TYPE_YESNO
        )
    
    def exit_confirmed(self, confirmed):
        """Handle exit confirmation"""
        if confirmed:
            self.close()

from Components.ServiceEventTracker import ServiceEventTracker
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class PilotFSMediaPlayer:
    """Media player helper for PilotFS"""
    
    def __init__(self, session, config):
        self.session = session
        self.config = config
        self.current_playlist = []
        self.current_index = 0
    
    def play_single_file(self, file_path, callback=None):
        """
        Play a single media file
        
        Args:
            file_path: Path to media file
            callback: Callback when playback ends
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            logger.info(f"Playing: {file_path}")
            
            # Create service reference (4097 = gstreamer)
            ref = eServiceReference(4097, 0, file_path)
            ref.setName(os.path.basename(file_path))
            
            # Open MoviePlayer
            self.session.openWithCallback(
                callback if callback else lambda *args: None,
                PilotFSMoviePlayer,
                ref
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Play single file error: {e}")
            return False
    
    def play_playlist(self, file_list, start_file=None, callback=None):
        """
        Play a playlist of files
        
        Args:
            file_list: List of file paths
            start_file: File to start with (default: first)
            callback: Callback when playback ends
        """
        try:
            if not file_list:
                logger.error("Empty playlist")
                return False
            
            # Store playlist
            self.current_playlist = file_list
            self.current_index = 0
            
            # Find starting position
            if start_file and start_file in file_list:
                self.current_index = file_list.index(start_file)
            
            logger.info(f"Playing playlist: {len(file_list)} files, starting at index {self.current_index}")
            
            # Play first file with playlist callback
            return self.play_single_file(
                self.current_playlist[self.current_index],
                lambda *args: self._playlist_callback(callback)
            )
            
        except Exception as e:
            logger.error(f"Play playlist error: {e}")
            return False
    
    def _playlist_callback(self, user_callback):
        """Handle playlist progression"""
        try:
            # Move to next track
            self.current_index += 1
            
            if self.current_index < len(self.current_playlist):
                # Play next file
                next_file = self.current_playlist[self.current_index]
                logger.info(f"Playing next: {next_file} ({self.current_index + 1}/{len(self.current_playlist)})")
                
                self.play_single_file(
                    next_file,
                    lambda *args: self._playlist_callback(user_callback)
                )
            else:
                # Playlist finished
                logger.info("Playlist finished")
                self.current_playlist = []
                self.current_index = 0
                
                if user_callback:
                    user_callback()
        
        except Exception as e:
            logger.error(f"Playlist callback error: {e}")
            if user_callback:
                user_callback()
    
    def can_play_file(self, file_path):
        """
        Check if file can be played
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if playable
        """
        if not os.path.exists(file_path):
            return False
        
        # Check file size
        try:
            size = os.path.getsize(file_path)
            if size == 0:
                return False
        except:
            return False
        
        # Check extension
        ext = os.path.splitext(file_path)[1].lower()
        
        video_ext = ['.mp4', '.mkv', '.avi', '.ts', '.m2ts', '.mov', '.m4v', '.mpg', '.mpeg', '.wmv', '.flv']
        audio_ext = ['.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.ac3', '.dts']
        
        return ext in video_ext or ext in audio_ext
    
    def detect_audio_files(self, directory):
        """
        Detect all audio files in a directory
        
        Args:
            directory: Directory to scan
            
        Returns:
            list: Sorted list of audio file paths
        """
        audio_extensions = ['.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.ac3', '.dts']
        audio_files = []
        
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    ext = os.path.splitext(item)[1].lower()
                    if ext in audio_extensions:
                        audio_files.append(item_path)
            
            # Sort alphabetically
            audio_files.sort()
            
        except Exception as e:
            logger.error(f"Error detecting audio files: {e}")
        
        return audio_files
    
    def detect_video_files(self, directory):
        """
        Detect all video files in a directory
        
        Args:
            directory: Directory to scan
            
        Returns:
            list: Sorted list of video file paths
        """
        video_extensions = ['.mp4', '.mkv', '.avi', '.ts', '.m2ts', '.mov', '.m4v', '.mpg', '.mpeg', '.wmv', '.flv']
        video_files = []
        
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    ext = os.path.splitext(item)[1].lower()
                    if ext in video_extensions:
                        video_files.append(item_path)
            
            # Sort alphabetically
            video_files.sort()
            
        except Exception as e:
            logger.error(f"Error detecting video files: {e}")
        
        return video_files
    
    def play_with_external_player(self, file_path):
        """
        Fallback: play with external player
        
        Args:
            file_path: Path to media file
            
        Returns:
            bool: True if launched successfully
        """
        import subprocess
        import threading
        
        def play_thread():
            # Try common media players
            players = [
                ['gst-launch-1.0', 'playbin', 'uri=file://' + file_path],
                ['ffplay', '-autoexit', '-nodisp', file_path],
                ['mplayer', '-quiet', file_path]
            ]
            
            for player_cmd in players:
                try:
                    subprocess.Popen(player_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    logger.info(f"Playing with external player: {player_cmd[0]}")
                    return True
                except FileNotFoundError:
                    continue
            
            logger.error("No external media player available")
            return False
        
        thread = threading.Thread(target=play_thread, daemon=True)
        thread.start()
        return True
