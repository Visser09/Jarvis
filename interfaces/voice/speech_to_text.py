import speech_recognition as sr
from utils.logger import get_logger
import time

logger = get_logger(__name__)

class SpeechToText:
    def __init__(self):
        logger.info("Initializing Speech-to-Text using SpeechRecognition...")
        self.recognizer = sr.Recognizer()
        logger.info("Speech-to-Text ready")

    def listen(self):
        """Listen for speech and return the transcribed text"""
        logger.info("Listening for speech...")

        try:
            with sr.Microphone() as source:
                logger.info("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Listening for phrase...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)

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
        logger.info("Cleaning up Speech-to-Text resources...")
        # Nothing to clean up since we don't persist the microphone
