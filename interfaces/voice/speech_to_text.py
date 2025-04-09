"""
Speech to Text module for Jarvis using SpeechRecognition.
This basic implementation uses the default microphone and Google's Speech Recognition.
"""
import speech_recognition as sr
from utils.logger import get_logger
import time

logger = get_logger(__name__)

class SpeechToText:
    def __init__(self):
        logger.info("Initializing Speech-to-Text using SpeechRecognition...")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise during initialization
        with self.microphone as source:
            logger.info("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Ambient noise adjustment complete")
        
    def listen(self):
        """Listen for speech and return the transcribed text"""
        logger.info("Listening for speech...")
        
        try:
            with self.microphone as source:
                # Adjust for ambient noise before each listen
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Set timeout and phrase_time_limit for better responsiveness
                audio = self.recognizer.listen(
                    source,
                    timeout=5,  # Wait up to 5 seconds for the start of a phrase
                    phrase_time_limit=10  # Maximum length of a phrase
                )
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    logger.info("Transcription result: %s", text)
                    return text
                except sr.UnknownValueError:
                    logger.debug("Speech was unintelligible")
                    return ""
                except sr.RequestError as e:
                    logger.error("Could not request results from Google Speech Recognition service; %s", e)
                    return ""
                    
        except sr.WaitTimeoutError:
            logger.debug("No speech detected within timeout period")
            return ""
        except Exception as e:
            logger.error("Error during speech recognition: %s", str(e))
            return ""
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up Speech-to-Text resources...")
        # No explicit cleanup needed for SpeechRecognition
