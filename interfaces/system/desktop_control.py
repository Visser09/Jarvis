"""
Desktop Control module for Jarvis
"""
import os
import subprocess
import platform
import time
from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import PyAutoGUI
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    logger.warning("PyAutoGUI not available. Limited desktop control functionality.")
    PYAUTOGUI_AVAILABLE = False

# Try to import PyGetWindow
try:
    import pygetwindow as gw
    PYGETWINDOW_AVAILABLE = True
except ImportError:
    logger.warning("PyGetWindow not available. Limited window management functionality.")
    PYGETWINDOW_AVAILABLE = False

class DesktopControl:
    """Desktop control and automation"""
    
    def __init__(self):
        """Initialize desktop control capabilities"""
        logger.info("Initializing Desktop Control...")
        self.system = platform.system()
        logger.info(f"Detected operating system: {self.system}")
        logger.info("Desktop Control initialization complete.")
    
    def open_application(self, app_name):
        """Open an application by name"""
        logger.info(f"Attempting to open application: {app_name}")
        
        app_name = app_name.lower()
        
        # Common applications with their commands for different platforms
        common_apps = {
            "chrome": {
                "Windows": "start chrome",
                "Darwin": "open -a 'Google Chrome'",
                "Linux": "google-chrome"
            },
            "firefox": {
                "Windows": "start firefox",
                "Darwin": "open -a Firefox",
                "Linux": "firefox"
            },
            "notepad": {
                "Windows": "notepad",
                "Darwin": "open -a TextEdit",
                "Linux": "gedit"
            },
            "calculator": {
                "Windows": "calc",
                "Darwin": "open -a Calculator",
                "Linux": "gnome-calculator"
            },
            "spotify": {
                "Windows": "start spotify",
                "Darwin": "open -a Spotify",
                "Linux": "spotify"
            },
            "tradingview": {
                "Windows": "start https://www.tradingview.com/chart/",
                "Darwin": "open https://www.tradingview.com/chart/",
                "Linux": "xdg-open https://www.tradingview.com/chart/"
            }
        }
        
        try:
            # Check if the app is in our common apps list
            for common_name, commands in common_apps.items():
                if common_name in app_name:
                    if self.system in commands:
                        command = commands[self.system]
                        subprocess.Popen(command, shell=True)
                        logger.info(f"Opened {common_name} using command: {command}")
                        return True
            
            # If not found in common apps, try a direct approach
            if self.system == "Windows":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif self.system == "Darwin":  # macOS
                subprocess.Popen(f"open -a '{app_name}'", shell=True)
            elif self.system == "Linux":
                subprocess.Popen(app_name, shell=True)
            
            logger.info(f"Attempted to open {app_name} using generic command")
            return True
            
        except Exception as e:
            logger.error(f"Error opening application {app_name}: {str(e)}")
            return False
    
    def close_application(self, app_name):
        """Close an application by name"""
        if not PYGETWINDOW_AVAILABLE:
            logger.warning("PyGetWindow not available. Cannot close applications.")
            return False
        
        try:
            # Find windows matching the app name
            windows = gw.getWindowsWithTitle(app_name)
            
            if not windows:
                logger.warning(f"No windows found with title containing '{app_name}'")
                return False
            
            # Close each matching window
            for window in windows:
                window.close()
                logger.info(f"Closed window: {window.title}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error closing application {app_name}: {str(e)}")
            return False
    
    def type_text(self, text):
        """Type text using PyAutoGUI"""
        if not PYAUTOGUI_AVAILABLE:
            logger.warning("PyAutoGUI not available. Cannot type text.")
            return False
        
        try:
            pyautogui.typewrite(text)
            logger.info(f"Typed text: {text}")
            return True
        except Exception as e:
            logger.error(f"Error typing text: {str(e)}")
            return False
    
    def click_position(self, x, y):
        """Click at a specific position"""
        if not PYAUTOGUI_AVAILABLE:
            logger.warning("PyAutoGUI not available. Cannot click position.")
            return False
        
        try:
            pyautogui.click(x, y)
            logger.info(f"Clicked at position: ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Error clicking position: {str(e)}")
            return False
    
    def get_open_windows(self):
        """Get a list of currently open windows"""
        if not PYGETWINDOW_AVAILABLE:
            logger.warning("PyGetWindow not available. Cannot get open windows.")
            return []
        
        try:
            windows = gw.getAllTitles()
            return [title for title in windows if title]  # Filter out empty titles
        except Exception as e:
            logger.error(f"Error getting open windows: {str(e)}")
            return []
    
    def execute_command(self, command):
        """Execute a system command"""
        try:
            logger.info(f"Executing command: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Command executed successfully")
                return result.stdout
            else:
                logger.warning(f"Command execution failed: {result.stderr}")
                return result.stderr
                
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return f"Error: {str(e)}"