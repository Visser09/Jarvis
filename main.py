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
from interfaces.voice.speech_to_text import SpeechToText
from interfaces.voice.text_to_speech import TextToSpeech
from interfaces.system.desktop_control import DesktopControl
from interfaces.system.screen_reader import ScreenReader
from utils.logger import setup_logger

# Ensure stdout uses UTF-8 to avoid Unicode logging errors
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = setup_logger()

class Jarvis:
    """Main Jarvis controller class"""
    
    def __init__(self):
        logger.info("Initializing Jarvis AI Assistant...")
        
        # Initialize core components
        self.memory = MemoryManager()
        self.ai_engine = AIEngine(self.memory)
        
        # Initialize interfaces
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.desktop = DesktopControl()
        self.screen_reader = ScreenReader()  # For screen monitoring
        
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
        This method logs that it is waiting once, then calls stt.listen() once.
        If no command is captured, it returns an empty string.
        """
        logger.info("Listening for command...")
        self.tts.stop()  # Interrupt any ongoing TTS
        command = self.stt.listen()
        return command
    
    def _main_loop(self):
        """
        Main processing loop.
        Jarvis continuously listens for commands and processes them.
        """
        while self.running:
            user_input = self._get_user_input()
            if user_input:
                response = self._process_command(user_input)
                if response:
                    logger.info("Jarvis: %s", response)
                    self.tts.speak(response)
            # If no command was captured, just continue the loop without extra logging.
            time.sleep(0.1)
    
    def _process_command(self, command):
        """Process user command and return a response"""
        logger.info("User: %s", command)
        self.memory.add_interaction("user", command)
        
        lower_cmd = command.lower()
        
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

        # Desktop control command
        if "open" in lower_cmd and "application" in lower_cmd:
            # Use regex to extract the app name between "open" and "application"
            match = re.search(r'open\s+(.*?)\s+application', lower_cmd)
            if match:
                app_name = match.group(1).strip()
                self.desktop.open_application(app_name)
                return f"Opening {app_name} for you, sir."
            else:
                logger.error("Could not parse application name from command: %s", lower_cmd)
                return "Sorry, I couldn't determine which application to open."

        
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
