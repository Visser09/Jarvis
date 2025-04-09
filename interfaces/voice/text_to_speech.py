"""
Text to Speech module for Jarvis using Microsoft Edge TTS for high-quality voice.
"""
import edge_tts
import asyncio
from utils.logger import get_logger
import threading
import os
import pygame
import tempfile

logger = get_logger(__name__)

class TextToSpeech:
    def __init__(self):
        logger.info("Initializing Text-to-Speech using Edge TTS...")
        try:
            # Use a British male voice for Jarvis
            self.voice = "en-GB-RyanNeural"  # Professional British male voice
            self.is_speaking = False
            self.current_thread = None
            # Initialize pygame mixer
            pygame.mixer.init()
            logger.info("Edge TTS initialized successfully with Jarvis voice")
        except Exception as e:
            logger.error(f"Error initializing Edge TTS: {str(e)}")
            self.voice = None
    
    def speak(self, text):
        """Speak the given text"""
        if not text:
            return
            
        try:
            # Stop any ongoing speech
            self.stop()
            
            def speak_async():
                try:
                    self.is_speaking = True
                    # Create event loop for async operations
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Create a temporary file with a unique name
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    # Generate and save audio
                    communicate = edge_tts.Communicate(text, self.voice)
                    loop.run_until_complete(communicate.save(temp_path))
                    
                    # Play the audio using pygame
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    
                    # Wait for the audio to finish playing
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    
                    # Clean up the temporary file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                        
                except Exception as e:
                    logger.error(f"Error in speak_async: {str(e)}")
                finally:
                    self.is_speaking = False
                    loop.close()
            
            self.current_thread = threading.Thread(target=speak_async)
            self.current_thread.start()
            
        except Exception as e:
            logger.error(f"Error in speak method: {str(e)}")
            print("Jarvis: " + text)
    
    def stop(self):
        """Stop any ongoing speech"""
        if self.is_speaking:
            self.is_speaking = False
            pygame.mixer.music.stop()
            if self.current_thread and self.current_thread.is_alive():
                self.current_thread.join(timeout=0.1)
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up Text-to-Speech resources...")
        self.stop()
        pygame.mixer.quit()
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join()
