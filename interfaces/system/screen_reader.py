"""
Screen Reader module for Jarvis
"""
import os
import time
import numpy as np
from utils.logger import get_logger

logger = get_logger(__name__)

# Try to import required libraries
try:
    import pyautogui
    from PIL import Image
    SCREEN_READER_AVAILABLE = True
except ImportError:
    logger.warning("Required libraries for screen reading not available.")
    SCREEN_READER_AVAILABLE = False

class ScreenReader:
    """Screen reading and OCR capabilities"""
    
    def __init__(self):
        """Initialize screen reader capabilities"""
        logger.info("Initializing Screen Reader...")
        # Flag for continuous monitoring
        self.monitoring_active = False
        
        if SCREEN_READER_AVAILABLE:
            logger.info("Screen Reader initialized.")
        else:
            logger.warning("Screen Reader functionality will be limited.")

    def capture_screen(self, region=None):
        """Capture the screen or a region of it"""
        if not SCREEN_READER_AVAILABLE:
            logger.warning("Screen capture functionality not available.")
            return None
        
        try:
            screenshot = pyautogui.screenshot(region=region)
            logger.info("Screen captured successfully.")
            return screenshot
        except Exception as e:
            logger.error(f"Error capturing screen: {str(e)}")
            return None

    def read_text_from_screen(self, region=None):
        """Read text from the screen using OCR"""
        if not SCREEN_READER_AVAILABLE:
            logger.warning("OCR functionality not available.")
            return ""
        
        try:
            screenshot = self.capture_screen(region)
            if screenshot is None:
                return ""
            
            # Convert screenshot to numpy array
            screenshot_np = np.array(screenshot)
            
            logger.info("OCR functionality disabled.")
            return ""
            
        except Exception as e:
            logger.error(f"Error reading text from screen: {str(e)}")
            return ""
    
    def monitor_for_changes(self, region=None, interval=1.0, callback=None):
        """
        Continuously monitor the screen for changes and call the callback when changes are detected.
        The monitoring runs until self.monitoring_active is set to False.
        """
        if not SCREEN_READER_AVAILABLE:
            logger.warning("Screen monitoring functionality not available.")
            return False
        
        if callback is None:
            logger.warning("No callback provided for screen monitoring.")
            return False
        
        self.monitoring_active = True
        logger.info(f"Starting screen monitoring with an interval of {interval} seconds.")
        
        last_screenshot = self.capture_screen(region)
        if last_screenshot is None:
            return False
        
        while self.monitoring_active:
            time.sleep(interval)
            current_screenshot = self.capture_screen(region)
            if current_screenshot is None:
                continue
            
            difference = self._compare_images(last_screenshot, current_screenshot)
            if difference > 0.05:  # More than 5% difference
                logger.info(f"Screen change detected: {difference*100:.2f}% difference")
                callback(current_screenshot)
            
            last_screenshot = current_screenshot
        
        logger.info("Screen monitoring stopped.")
        return True
    
    def stop_monitoring(self):
        """Stop continuous screen monitoring"""
        self.monitoring_active = False
    
    def _compare_images(self, img1, img2):
        """Compare two images and return a difference percentage"""
        img1_np = np.array(img1)
        img2_np = np.array(img2)
        
        # If shapes differ, consider them completely different
        if img1_np.shape != img2_np.shape:
            return 1.0
        
        diff = np.abs(img1_np - img2_np).sum()
        max_diff = np.prod(img1_np.shape) * 255  # Maximum possible difference
        return diff / max_diff
