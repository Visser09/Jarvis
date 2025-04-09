"""
Spotify Control module for Jarvis
"""
import subprocess
import time
import pyautogui
import win32gui
import win32con
import os
from utils.logger import get_logger

logger = get_logger(__name__)

class SpotifyControl:
    def __init__(self):
        """Initialize Spotify control capabilities"""
        logger.info("Initializing Spotify Control...")
        self.is_playing = False
        self.spotify_path = os.path.expandvars("%APPDATA%\\Spotify\\Spotify.exe")
        logger.info("Spotify Control initialized")

    def _ensure_spotify_running(self):
        """Ensure Spotify is running"""
        try:
            # Check if Spotify is running
            spotify_hwnd = self._find_spotify_window()
            if not spotify_hwnd:
                # Start Spotify if not running
                if os.path.exists(self.spotify_path):
                    subprocess.Popen([self.spotify_path])
                    time.sleep(5)  # Wait for Spotify to start
                    spotify_hwnd = self._find_spotify_window()
                    if not spotify_hwnd:
                        logger.error("Could not find Spotify window after starting")
                        return False
                    return True
                else:
                    logger.error("Spotify executable not found")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error ensuring Spotify is running: {str(e)}")
            return False

    def _find_spotify_window(self):
        """Find Spotify window using multiple methods"""
        try:
            # Try different window class names
            spotify_hwnd = None
            class_names = ["Chrome_WidgetWin_0", "SpotifyMainWindow", "Spotify"]
            
            for class_name in class_names:
                spotify_hwnd = win32gui.FindWindow(class_name, None)
                if spotify_hwnd:
                    break
            
            # If still not found, try finding by title
            if not spotify_hwnd:
                def callback(hwnd, extra):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if "spotify" in title.lower():
                            extra.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(callback, windows)
                if windows:
                    spotify_hwnd = windows[0]
            
            return spotify_hwnd
        except Exception as e:
            logger.error(f"Error finding Spotify window: {str(e)}")
            return None

    def _bring_spotify_to_front(self):
        """Bring Spotify window to front"""
        try:
            # First ensure Spotify is running
            if not self._ensure_spotify_running():
                return False

            spotify_hwnd = self._find_spotify_window()
            if spotify_hwnd:
                # Bring window to front
                win32gui.ShowWindow(spotify_hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(spotify_hwnd)
                time.sleep(1)  # Increased delay to ensure window is ready
                return True
            logger.error("Could not find Spotify window")
            return False
        except Exception as e:
            logger.error(f"Error bringing Spotify to front: {str(e)}")
            return False

    def _send_spotify_command(self, command):
        """Send a command to Spotify"""
        try:
            # Ensure Spotify is running and in front
            if not self._ensure_spotify_running():
                return False

            # Bring Spotify to front
            if not self._bring_spotify_to_front():
                return False

            # Send the command
            pyautogui.press(command)
            time.sleep(0.5)  # Increased delay between commands
            return True
        except Exception as e:
            logger.error(f"Error sending Spotify command: {str(e)}")
            return False

    def play(self):
        """Play music on Spotify"""
        try:
            if self._send_spotify_command('playpause'):
                self.is_playing = True
                return True
            return False
        except Exception as e:
            logger.error(f"Error playing Spotify: {str(e)}")
            return False

    def pause(self):
        """Pause music on Spotify"""
        try:
            if self._send_spotify_command('playpause'):
                self.is_playing = False
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausing Spotify: {str(e)}")
            return False

    def next_track(self):
        """Skip to next track"""
        try:
            return self._send_spotify_command('nexttrack')
        except Exception as e:
            logger.error(f"Error skipping track: {str(e)}")
            return False

    def previous_track(self):
        """Go to previous track"""
        try:
            return self._send_spotify_command('prevtrack')
        except Exception as e:
            logger.error(f"Error going to previous track: {str(e)}")
            return False

    def set_volume(self, volume_percent):
        """Set Spotify volume (0-100)"""
        try:
            volume = max(0, min(100, volume_percent))
            # Use nircmd to set process volume
            subprocess.run(['nircmd', 'setprocessvolume', 'spotify.exe', str(volume/100)], 
                         capture_output=True, text=True)
            return True
        except Exception as e:
            logger.error(f"Error setting volume: {str(e)}")
            return False

    def search_and_play(self, query):
        """Search for a song and play it"""
        try:
            # Ensure Spotify is running and in front
            if not self._ensure_spotify_running():
                return False

            # Bring Spotify to front
            if not self._bring_spotify_to_front():
                return False

            # Open search
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(1.5)  # Increased delay
            
            # Clear any existing text
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.5)
            
            # Type search query
            pyautogui.write(query)
            time.sleep(2)  # Wait for search results
            
            # Press enter to search
            pyautogui.press('enter')
            time.sleep(3)  # Wait for results to load
            
            # Move to first result and play
            pyautogui.press('tab')  # Move to first result
            time.sleep(0.5)
            pyautogui.press('enter')  # Play the song
            time.sleep(1)
            
            self.is_playing = True
            return True
        except Exception as e:
            logger.error(f"Error searching and playing: {str(e)}")
            return False 