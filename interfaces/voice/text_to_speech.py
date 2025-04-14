import edge_tts
import asyncio
from utils.logger import get_logger
import threading
import os
import pygame
import tempfile
import time

from interfaces.system.spotify_control import SpotifyControl

logger = get_logger(__name__)

class TextToSpeech:
    def __init__(self, spotify_instance=None):
        logger.info("Initializing Text-to-Speech using Edge TTS...")
        try:
            self.voice = "en-GB-RyanNeural"
            self.is_speaking = False
            self.current_thread = None
            self.spotify = spotify_instance

            # Ensure wake word stream is initialized first
            time.sleep(0.5)  # Wait a bit to avoid audio device conflicts

            # Reset and safely re-initialize pygame mixer
            try:
                pygame.mixer.quit()
                time.sleep(0.2)  # Ensure device is freed
                pygame.mixer.init(frequency=24000, size=-16, channels=2, buffer=512)
                logger.info("Pygame mixer initialized at 24000 Hz.")
            except Exception as e:
                logger.error(f"Failed to initialize pygame mixer: {e}")

            logger.info("Edge TTS initialized successfully with Jarvis voice")
        except Exception as e:
            logger.error(f"Error initializing Edge TTS: {str(e)}")
            self.voice = None

    def speak(self, text):
        if not text:
            return
        try:
            self.stop()

            def speak_async():
                try:
                    self.is_speaking = True
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                        temp_path = temp_file.name

                    communicate = edge_tts.Communicate(text, self.voice)
                    loop.run_until_complete(communicate.save(temp_path))

                    if self.spotify:
                        self.spotify.set_volume(10)

                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()

                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)

                    # Wait for OS to release file lock
                    retries = 0
                    while retries < 10:
                        try:
                            os.remove(temp_path)
                            break
                        except PermissionError:
                            time.sleep(0.1)
                            retries += 1
                    else:
                        logger.warning("Unable to delete temp mp3 after 10 retries")

                except Exception as e:
                    logger.error(f"Error in speak_async: {str(e)}")
                finally:
                    if self.spotify:
                        self.spotify.set_volume(100)
                    self.is_speaking = False
                    loop.close()

            self.current_thread = threading.Thread(target=speak_async)
            self.current_thread.start()

        except Exception as e:
            logger.error(f"Error in speak method: {str(e)}")
            print("Jarvis: " + text)

    def stop(self):
        if self.is_speaking:
            self.is_speaking = False
            pygame.mixer.music.stop()
            if self.current_thread and self.current_thread.is_alive():
                self.current_thread.join(timeout=0.1)

    def cleanup(self):
        logger.info("Cleaning up Text-to-Speech resources...")
        self.stop()
        try:
            pygame.mixer.quit()
        except:
            pass
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join()
