#!/usr/bin/env python3
"""
Jarvis AI Assistant - Main Entry Point
"""

import os
import sys
import signal
import time
import threading
import re
from core.phi3_engine import Phi3Engine
from core.memory_manager import MemoryManager
from core.memory_summarizer import MemorySummarizer
from interfaces.voice.speech_to_text import SpeechToText
from interfaces.voice.text_to_speech import TextToSpeech
from interfaces.system.desktop_control import DesktopControl
from interfaces.system.screen_reader import ScreenReader
from interfaces.system.spotify_control import SpotifyControl
from utils.security import SecurityManager
from utils.logger import setup_logger

# Ensure stdout uses UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = setup_logger()

class Jarvis:
    def __init__(self):
        logger.info("Initializing Jarvis AI Assistant...")

        self.security = SecurityManager()
        self.memory = MemoryManager()
        self.memory_summarizer = MemorySummarizer()
        self.ai_engine = Phi3Engine(self.memory)
        self.expecting_followup = False

        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.desktop = DesktopControl()
        self.screen_reader = ScreenReader()
        self.spotify = SpotifyControl()

        self.wake_words = ["jarvis", "hey jarvis"]
        self.wake_word_enabled = True
        self.is_listening = False
        self.screen_monitoring_thread = None
        self.running = False

        logger.info("Wake word detection enabled")
        logger.info("Jarvis initialization complete.")

    def start(self):
        self.running = True
        logger.info("Jarvis is now running.")
        self.tts.speak("Jarvis AI Assistant is online and ready to assist you, sir.")

        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        self.tts.speak("Shutting down. Goodbye, sir.")
        self.memory.save()
        self.tts.cleanup()
        self.stt.cleanup()

        if self.screen_monitoring_thread and self.screen_monitoring_thread.is_alive():
            self.screen_reader.stop_monitoring()
            self.screen_monitoring_thread.join()

        logger.info("Jarvis has been shut down.")

    def _get_user_input(self):
        if not self.is_listening:
            if self.expecting_followup:
                self.is_listening = True
                return ""

            if not hasattr(self, 'last_log_time') or time.time() - self.last_log_time > 5:
                logger.info("Waiting for wake word...")
                self.last_log_time = time.time()

            command = self.stt.listen()
            if command:
                lower_cmd = command.lower()
                for wake_word in self.wake_words:
                    if wake_word in lower_cmd:
                        parts = lower_cmd.split(wake_word, 1)
                        if len(parts) > 1:
                            command = parts[1].strip()
                            if command:
                                self.is_listening = True
                                return command
                        self.is_listening = True
                        return ""
                if self.is_listening:
                    return command
            return ""

        logger.info("Listening for command...")
        self.tts.stop()
        command = self.stt.listen()
        if not command:
            self.is_listening = False
            return ""
        return command

    def _main_loop(self):
        last_response = None
        while self.running:
            user_input = self._get_user_input()
            if user_input or self.expecting_followup:
                if user_input.strip() and user_input != last_response:
                    response, expecting_followup = self._process_command(user_input)
                    self.expecting_followup = expecting_followup
                    if response and response != last_response:
                        logger.info("Jarvis: %s", response)
                        self.tts.speak(response)
                        last_response = response
            time.sleep(0.1)

    def _process_command(self, command):
        logger.info("User: %s", command)
        self.memory.add_interaction("user", command)
        lower_cmd = command.lower()

        # Spotify
        if "spotify" in lower_cmd or "music" in lower_cmd:
            if "next" in lower_cmd:
                if self.spotify.next_track():
                    return "Playing next track, sir.", False
                return "I couldn't skip to the next track, sir.", False
            elif "previous" in lower_cmd:
                if self.spotify.previous_track():
                    return "Playing previous track, sir.", False
                return "I couldn't go to the previous track, sir.", False
            elif "pause" in lower_cmd:
                if self.spotify.pause():
                    return "Paused music, sir.", False
                return "I couldn't pause the music, sir.", False
            elif "play" in lower_cmd:
                return "Do you want me to play music on Spotify? Please specify the song name.", True
            else:
                words = lower_cmd.split()
                words = [w for w in words if w not in ["play", "spotify", "music", "on", "the"]]
                song_name = " ".join(words).strip()
                if song_name:
                    if self.spotify.search_and_play(song_name):
                        return f"Playing {song_name} on Spotify, sir.", False
                    return f"I couldn't play {song_name}, sir.", False
                return "Please specify a song name to play.", True

        if "volume" in lower_cmd:
            try:
                volume = int(''.join(filter(str.isdigit, lower_cmd)))
                if self.spotify.set_volume(volume):
                    return f"Set Spotify volume to {volume}%, sir.", False
                return "I couldn't set the volume, sir.", False
            except:
                return "Please specify a volume level between 0 and 100, sir.", False

        # Screen Reader
        if "start screen monitoring" in lower_cmd:
            if self.screen_monitoring_thread and self.screen_monitoring_thread.is_alive():
                return "Screen monitoring is already running.", False
            def monitor_callback(screenshot):
                ocr_text = self.screen_reader.read_text_from_screen()
                logger.info("Monitored Screen OCR: %s", ocr_text)
            def monitor():
                self.screen_reader.monitor_for_changes(callback=monitor_callback)
            self.screen_monitoring_thread = threading.Thread(target=monitor, daemon=True)
            self.screen_monitoring_thread.start()
            return "Continuous screen monitoring started.", False

        if "stop screen monitoring" in lower_cmd:
            if self.screen_monitoring_thread and self.screen_monitoring_thread.is_alive():
                self.screen_reader.stop_monitoring()
                self.screen_monitoring_thread.join()
                return "Continuous screen monitoring stopped.", False
            return "Screen monitoring is not running.", False

        # Desktop Control
        if "open" in lower_cmd or "launch" in lower_cmd or "start" in lower_cmd:
            words = lower_cmd.split()
            words = [w for w in words if w not in ["open", "launch", "start", "the", "app", "application"]]
            app_name = " ".join(words).strip()
            if not app_name:
                return "Which application would you like me to open, sir?", True
            try:
                self.desktop.open_application(app_name)
                return f"Opening {app_name} for you, sir.", False
            except Exception as e:
                logger.error(f"Error opening application: {str(e)}")
                return f"I couldn't open {app_name}, sir.", False

        # Default: AI Engine (Phi-3)
        response = self.ai_engine.process(command)
        self.memory.add_interaction("jarvis", response)
        return response, False


def signal_handler(sig, frame):
    logger.info("Interrupt received, shutting down...")
    if jarvis and jarvis.running:
        jarvis.stop()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    jarvis = Jarvis()
    jarvis.start()
