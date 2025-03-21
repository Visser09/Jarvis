"""
Speech to Text module for Jarvis using SpeechRecognition.
This basic implementation uses the default microphone and Google's Speech Recognition.
"""
import speech_recognition as sr
from utils.logger import get_logger

logger = get_logger(__name__)

class SpeechToText:
    def __init__(self):
        logger.info("Initializing Speech-to-Text using SpeechRecognition...")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def listen(self):
        logger.info("Listening for speech...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        try:
            text = self.recognizer.recognize_google(audio)
            logger.info("Transcription result: %s", text)
            return text
        except sr.UnknownValueError:
            logger.error("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error("Could not request results from Google Speech Recognition service; %s", e)
            return ""
    
    def cleanup(self):
        logger.info("Cleaning up Speech-to-Text resources...")
        # No explicit cleanup needed for SpeechRecognition.
