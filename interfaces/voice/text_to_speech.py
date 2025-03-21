"""
Text to Speech module for Jarvis using pyttsx3.
This basic implementation converts text to speech synchronously.
"""
import pyttsx3
from utils.logger import get_logger

logger = get_logger(__name__)

class TextToSpeech:
    def __init__(self):
        logger.info("Initializing Text-to-Speech using pyttsx3...")
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 0.9)
            voices = self.engine.getProperty('voices')
            # Choose a male voice if available
            for voice in voices:
                if "male" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            logger.info("pyttsx3 TTS initialized.")
        except Exception as e:
            logger.error("Error initializing pyttsx3: %s", str(e))
            self.engine = None
    
    def speak(self, text):
        if not text:
            return
        if self.engine:
            logger.info("Speaking: %s", text)
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print("Jarvis: " + text)
    
    def stop(self):
        if self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                logger.error("Error stopping pyttsx3: %s", str(e))
    
    def cleanup(self):
        logger.info("Cleaning up Text-to-Speech resources...")
        self.stop()
