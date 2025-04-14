import pvporcupine
import pyaudio
import struct
from utils.logger import get_logger

logger = get_logger(__name__)

class WakeWordDetector:
    def __init__(self, wake_word="jarvis", sensitivity=0.6):
        self.keyword = wake_word
        self.sensitivity = sensitivity
        self.porcupine = None
        self.pa = None
        self.stream = None

        try:
            access_key = "KTGO/VRkPtNm86VsdjeBMPEjCP8LKhRKNC2+MG4wEif3yBbMZg1zQQ=="
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=[self.keyword],
                sensitivities=[self.sensitivity]
            )
            self.pa = pyaudio.PyAudio()
            logger.info(f"Wake word detector initialized for '{wake_word}'")
        except Exception as e:
            logger.error(f"Error initializing wake word engine: {str(e)}")

    def _open_stream(self):
        if not self.stream or self.stream.is_stopped():
            self.stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

    def listen(self, timeout=0.1):
        """Listen for the wake word — returns True if detected"""
        try:
            self._open_stream()
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
            result = self.porcupine.process(pcm)
            return result >= 0
        except Exception as e:
            logger.error(f"Error in wake word detection: {str(e)}")
            return False

    def cleanup(self):
        """Cleanly shut down mic and Porcupine"""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.porcupine:
                self.porcupine.delete()
            if self.pa:
                self.pa.terminate()
            logger.info("Wake word detector shut down cleanly")
        except Exception as e:
            logger.error(f"Error cleaning up wake word: {str(e)}")
