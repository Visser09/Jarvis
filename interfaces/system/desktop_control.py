"""
Desktop Control module for Jarvis
"""
import os
import subprocess
import platform
import time
import winreg
import win32com.client
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
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.start_menu_paths = [
            os.path.expandvars("%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs")
        ]
        logger.info("Desktop Control initialized")
    
    def _search_start_menu(self, app_name):
        """Search for application in Start Menu"""
        app_name = app_name.lower()
        for start_menu_path in self.start_menu_paths:
            for root, dirs, files in os.walk(start_menu_path):
                for file in files:
                    if file.endswith('.lnk'):
                        if app_name in file.lower():
                            return os.path.join(root, file)
        return None

    def _search_registry(self, app_name):
        """Search for application in Windows Registry"""
        app_name = app_name.lower()
        try:
            # Search in HKEY_LOCAL_MACHINE
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if app_name in subkey_name.lower():
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                try:
                                    path = winreg.QueryValue(subkey, None)
                                    if path and os.path.exists(path):
                                        return path
                                except:
                                    continue
                    except:
                        continue
        except:
            pass
        return None

    def _search_common_paths(self, app_name):
        """Search for application in common installation paths"""
        app_name = app_name.lower()
        common_paths = [
            os.path.expandvars("%ProgramFiles%"),
            os.path.expandvars("%ProgramFiles(x86)%"),
            os.path.expandvars("%LocalAppData%"),
            os.path.expandvars("%AppData%")
        ]
        
        for base_path in common_paths:
            if not os.path.exists(base_path):
                continue
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.endswith('.exe') and app_name in file.lower():
                        return os.path.join(root, file)
        return None

    def open_application(self, app_name):
        """Open an application using various methods"""
        logger.info(f"Attempting to open application: {app_name}")
        
        # Try different methods to find and open the application
        methods = [
            (self._search_start_menu, "Start Menu"),
            (self._search_registry, "Registry"),
            (self._search_common_paths, "Common Paths")
        ]
        
        for search_method, method_name in methods:
            try:
                path = search_method(app_name)
                if path:
                    logger.info(f"Found application in {method_name}: {path}")
                    if path.endswith('.lnk'):
                        # Handle shortcut
                        self.shell.Run(path, 1, True)
                    else:
                        # Handle executable
                        subprocess.Popen(path)
                    return True
            except Exception as e:
                logger.error(f"Error in {method_name} search: {str(e)}")
                continue
        
        # If no method worked, try using the Windows search
        try:
            subprocess.Popen(f'explorer shell:AppsFolder\\{app_name}')
            return True
        except:
            pass
            
        raise Exception(f"Could not find or open application: {app_name}")
    
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