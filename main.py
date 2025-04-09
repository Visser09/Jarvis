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
from core.ai_engine import AIEngine
from core.memory_manager import MemoryManager
from core.memory_summarizer import MemorySummarizer
from interfaces.voice.speech_to_text import SpeechToText
from interfaces.voice.text_to_speech import TextToSpeech
from interfaces.system.desktop_control import DesktopControl
from interfaces.system.screen_reader import ScreenReader
from interfaces.system.spotify_control import SpotifyControl
from utils.security import SecurityManager
from utils.logger import setup_logger

# Ensure stdout uses UTF-8 to avoid Unicode logging errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = setup_logger()

class Jarvis:
    """Main Jarvis controller class"""
    
    def __init__(self):
        logger.info("Initializing Jarvis AI Assistant...")
        
        # Initialize security manager (for API key encryption only)
        self.security = SecurityManager()
        
        # Initialize core components
        self.memory = MemoryManager()
        self.memory_summarizer = MemorySummarizer()
        self.ai_engine = AIEngine(self.memory)
        
        # Initialize interfaces
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.desktop = DesktopControl()
        self.screen_reader = ScreenReader()  # For screen monitoring
        self.spotify = SpotifyControl()  # Add Spotify control
        
        # Wake word settings
        self.wake_words = ["jarvis", "hey jarvis"]
        self.wake_word_enabled = True
        self.is_listening = False
        logger.info("Wake word detection enabled")
        
        # Variable for continuous screen monitoring thread
        self.screen_monitoring_thread = None
        
        # State variable
        self.running = False
        
        logger.info("Jarvis initialization complete.")
    
    def start(self):
        """Start Jarvis"""
        self.running = True
        logger.info("Jarvis is now running.")
        
        # Welcome message
        welcome_message = "Jarvis AI Assistant is online and ready to assist you, sir."
        logger.info(welcome_message)
        self.tts.speak(welcome_message)
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop Jarvis gracefully"""
        self.running = False
        logger.info("Shutting down Jarvis...")
        self.tts.speak("Shutting down. Goodbye, sir.")
        
        # Clean up resources
        self.memory.save()
        self.tts.cleanup()
        self.stt.cleanup()
        
        # Stop continuous screen monitoring if active
        if self.screen_monitoring_thread and self.screen_monitoring_thread.is_alive():
            self.screen_reader.stop_monitoring()
            self.screen_monitoring_thread.join()
        
        logger.info("Jarvis has been shut down.")
    
    def _get_user_input(self):
        """
        Listen for a command.
        Returns empty string if no command is captured or wake word not detected.
        """
        if not self.is_listening:
            if not hasattr(self, 'last_log_time') or time.time() - self.last_log_time > 5:  # Log every 5 seconds
                logger.info("Waiting for wake word...")
                self.last_log_time = time.time()
            command = self.stt.listen()
            if command:
                lower_cmd = command.lower()
                # Check if command contains wake word
                for wake_word in self.wake_words:
                    if wake_word in lower_cmd:
                        # Get everything after the wake word
                        parts = lower_cmd.split(wake_word, 1)
                        if len(parts) > 1:
                            command = parts[1].strip()
                            if command:  # If there's a command after wake word
                                self.is_listening = True
                                return command
                        # If no command after wake word, just start listening
                        self.is_listening = True
                        return ""
                # If no wake word but we're already in listening mode, process the command
                if self.is_listening:
                    return command
            return ""
        
        logger.info("Listening for command...")
        self.tts.stop()  # Interrupt any ongoing TTS
        command = self.stt.listen()
        
        if not command:
            self.is_listening = False
            return ""
            
        return command
    
    def _main_loop(self):
        """
        Main processing loop.
        Jarvis waits for wake word before listening for commands.
        """
        last_response = None
        while self.running:
            # Get command
            user_input = self._get_user_input()
            if user_input:
                # Only process if it's not empty and not the same as last response
                if user_input.strip() and user_input != last_response:
                    response = self._process_command(user_input)
                    if response and response != last_response:
                        logger.info("Jarvis: %s", response)
                        self.tts.speak(response)
                        last_response = response
            time.sleep(0.1)
    
    def _process_command(self, command):
        """Process user command and return a response"""
        logger.info("User: %s", command)
        self.memory.add_interaction("user", command)
        
        lower_cmd = command.lower()
        
        # --- Spotify Commands ---
        if "spotify" in lower_cmd or "music" in lower_cmd:
            if "next" in lower_cmd:
                if self.spotify.next_track():
                    return "Playing next track, sir."
                return "I couldn't skip to the next track, sir."
            elif "previous" in lower_cmd:
                if self.spotify.previous_track():
                    return "Playing previous track, sir."
                return "I couldn't go to the previous track, sir."
            elif "pause" in lower_cmd:
                if self.spotify.pause():
                    return "Paused music, sir."
                return "I couldn't pause the music, sir."
            elif "play" in lower_cmd:
                # Ask for confirmation before playing music
                return "Do you want me to play music on Spotify? Please specify the song name."
            else:
                # Handle song name requests
                words = lower_cmd.split()
                words = [w for w in words if w not in ["play", "spotify", "music", "on", "the"]]
                song_name = " ".join(words).strip()  # Ensure no leading/trailing spaces
                
                if song_name:
                    logger.info(f"Attempting to play song: {song_name}")
                    if self.spotify.search_and_play(song_name):
                        return f"Playing {song_name} on Spotify, sir."
                    return f"I couldn't play {song_name}, sir."
                else:
                    return "Please specify a song name to play."
        
        # Handle volume control
        if "volume" in lower_cmd:
            try:
                volume = int(''.join(filter(str.isdigit, lower_cmd)))
                if self.spotify.set_volume(volume):
                    return f"Set Spotify volume to {volume}%, sir."
                return "I couldn't set the volume, sir."
            except:
                return "Please specify a volume level between 0 and 100, sir."
        
        # --- Screen Reader Commands ---
        if "start continuous screen monitoring" in lower_cmd or "start screen monitoring" in lower_cmd:
            if self.screen_monitoring_thread and self.screen_monitoring_thread.is_alive():
                return "Screen monitoring is already running."
            def monitor_callback(screenshot):
                ocr_text = self.screen_reader.read_text_from_screen()
                logger.info("Monitored Screen OCR: %s", ocr_text)
            def monitor():
                self.screen_reader.monitor_for_changes(callback=monitor_callback)
            self.screen_monitoring_thread = threading.Thread(target=monitor, daemon=True)
            self.screen_monitoring_thread.start()
            return "Continuous screen monitoring started."
        
        if "stop continuous screen monitoring" in lower_cmd or "stop screen monitoring" in lower_cmd:
            if self.screen_monitoring_thread and self.screen_monitoring_thread.is_alive():
                self.screen_reader.stop_monitoring()
                self.screen_monitoring_thread.join()
                return "Continuous screen monitoring stopped."
            return "Screen monitoring is not running."
        # --- End Screen Reader Commands ---

        # Desktop control command - more natural language handling
        if "open" in lower_cmd or "launch" in lower_cmd or "start" in lower_cmd:
            # Remove common words and get the app name
            words = lower_cmd.split()
            words = [w for w in words if w not in ["open", "launch", "start", "the", "app", "application"]]
            app_name = " ".join(words)
            
            if app_name:
                try:
                    self.desktop.open_application(app_name)
                    return f"Opening {app_name} for you, sir."
                except Exception as e:
                    logger.error(f"Error opening application: {str(e)}")
                    return f"I couldn't open {app_name}, sir."
            else:
                return "Which application would you like me to open, sir?"
        
        # Process command via AI Engine
        response = self.ai_engine.process(command)
        self.memory.add_interaction("jarvis", response)
        return response

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Interrupt received, shutting down...")
    if jarvis and jarvis.running:
        jarvis.stop()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    jarvis = Jarvis()
    jarvis.start()
