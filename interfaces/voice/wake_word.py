"""
Wake Word Detection module for Jarvis using Picovoice's Porcupine.
"""
import os
import pvporcupine
import pyaudio
import struct
import time
from utils.logger import get_logger

logger = get_logger(__name__)

class WakeWordDetector:
    """Detects wake word using Picovoice's Porcupine"""
    
    def __init__(self, wake_word="hey jarvis", sensitivity=0.5):
        """
        Initialize the wake word detector
        Args:
            wake_word (str): The wake word to detect ("hey jarvis", "computer", etc.)
            sensitivity (float): Detection sensitivity (0.0 to 1.0)
        """
        logger.info(f"Initializing Wake Word Detector with wake word: {wake_word}")
        
        try:
            # Get API key from environment variable
            access_key = os.environ.get("PICOVOICE_ACCESS_KEY")
            if not access_key:
                raise ValueError("PICOVOICE_ACCESS_KEY environment variable not set")
            
            # Initialize Porcupine
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=[wake_word],
                sensitivities=[sensitivity]
            )
            
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Open audio stream
            self.stream = self.audio.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            logger.info("Wake Word Detector initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Wake Word Detector: {str(e)}")
            raise
    
    def listen(self, timeout=None):
        """
        Listen for wake word
        Args:
            timeout (float, optional): Timeout in seconds. If None, listen indefinitely.
        Returns:
            bool: True if wake word detected, False otherwise
        """
        logger.info("Listening for wake word...")
        
        start_time = time.time()
        
        try:
            while True:
                # Check for timeout
                if timeout and (time.time() - start_time) > timeout:
                    logger.info("Wake word detection timed out")
                    return False
                
                # Read audio data
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # Process with Porcupine
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    logger.info("Wake word detected!")
                    return True
                
                # Small sleep to prevent CPU overuse
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error during wake word detection: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up Wake Word Detector...")
        try:
            if hasattr(self, 'stream'):
                self.stream.close()
            if hasattr(self, 'audio'):
                self.audio.terminate()
            if hasattr(self, 'porcupine'):
                self.porcupine.delete()
            logger.info("Wake Word Detector cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up Wake Word Detector: {str(e)}") 