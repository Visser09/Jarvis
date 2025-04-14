import sounddevice as sd
import numpy as np
import torch
import torchaudio
from utils.logger import get_logger

logger = get_logger(__name__)

class VoiceDetector:
    def __init__(self, callback, sample_rate=16000, threshold=0.5):
        self.callback = callback
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.stream = None
        self.is_running = False
        
        try:
            # Check available audio devices
            devices = sd.query_devices()
            logger.info(f"Available audio devices: {devices}")
            
            # Try to find a suitable input device
            input_device = None
            for device in devices:
                if device['max_input_channels'] > 0:
                    input_device = device['index']
                    break
            
            if input_device is None:
                raise RuntimeError("No input audio device found")
            
            # Initialize VAD model
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                trust_repo=True
            )
            (self.get_speech_timestamps, self.save_audio, self.read_audio, _, _) = self.utils
            logger.info("VoiceDetector initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing VoiceDetector: {str(e)}")
            raise

    def start(self):
        if self.is_running:
            logger.warning("VoiceDetector is already running")
            return
            
        try:
            self.is_running = True
            self.stream = sd.InputStream(
                channels=1,
                callback=self._audio_callback,
                samplerate=self.sample_rate,
                blocksize=int(self.sample_rate * 0.5),  # 0.5 sec
                dtype=np.float32
            )
            self.stream.start()
            logger.info("VoiceDetector started (Silero Hub VAD)")
        except Exception as e:
            self.is_running = False
            logger.error(f"Error starting VoiceDetector: {str(e)}")
            raise

    def stop(self):
        if not self.is_running:
            return
            
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.is_running = False
            logger.info("VoiceDetector stopped")
        except Exception as e:
            logger.error(f"Error stopping VoiceDetector: {str(e)}")

    def _audio_callback(self, indata, frames, time_info, status):
        if not self.is_running:
            return
            
        if status:
            logger.warning(f"Audio callback status: {status}")

        try:
            audio = indata[:, 0]
            audio_tensor = torch.from_numpy(audio).float()

            # Reshape and normalize
            audio_tensor = audio_tensor.unsqueeze(0)
            audio_tensor = audio_tensor / (torch.max(torch.abs(audio_tensor)) + 1e-6)

            timestamps = self.get_speech_timestamps(audio_tensor, self.model, threshold=self.threshold)
            if timestamps:
                logger.debug("Voice detected")
                self.callback()
        except Exception as e:
            logger.error(f"VAD detection error: {str(e)}")
            # Don't re-raise the exception to keep the stream running
