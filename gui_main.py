import tkinter as tk
from tkinter import scrolledtext, END, messagebox
import threading
import time

from core.memory_manager import MemoryManager
from core.phi3_engine import Phi3Engine
from utils.logger import setup_logger

from interfaces.voice.text_to_speech import TextToSpeech
from interfaces.voice.speech_to_text import SpeechToText
from interfaces.system.spotify_control import SpotifyControl
from interfaces.voice.voice_detector import VoiceDetector

logger = setup_logger()

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis AI Assistant")
        self.root.geometry("960x640")
        self.root.configure(bg="#1e1e1e")

        self.memory = MemoryManager()
        self.ai_engine = Phi3Engine(self.memory)
        self.spotify = SpotifyControl()
        self.tts = TextToSpeech(self.spotify)
        self.stt = SpeechToText()

        self.is_listening = False
        self.voice_detector = None

        # Try to initialize voice detection
        try:
            self.voice_detector = VoiceDetector(callback=self._on_voice_detected)
            self.voice_detector.start()
            logger.info("Voice detection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize voice detection: {str(e)}")
            messagebox.showwarning(
                "Voice Detection Warning",
                "Voice detection could not be initialized. You can still use text input."
            )

        self._build_gui()

    def _build_gui(self):
        self.output_display = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, height=20,
            bg="#2d2d2d", fg="#dcdcdc", insertbackground="#dcdcdc"
        )
        self.output_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        entry_frame = tk.Frame(self.root, bg="#1e1e1e")
        entry_frame.pack(pady=5)

        self.command_entry = tk.Entry(
            entry_frame, width=80,
            bg="#2d2d2d", fg="#dcdcdc", insertbackground="#dcdcdc"
        )
        self.command_entry.pack(side=tk.LEFT, padx=5)
        self.command_entry.bind("<Return>", self.send_command)

        tk.Button(entry_frame, text="Send", command=self.send_command, bg="#2d2d2d", fg="#dcdcdc").pack(side=tk.LEFT)
        tk.Button(entry_frame, text="🎤 Speak", command=self.listen_command, bg="#2d2d2d", fg="#dcdcdc").pack(side=tk.LEFT)

        self.status_bar = tk.Label(
            self.root, text="🟢 Jarvis is standing by",
            bd=1, relief=tk.SUNKEN, anchor=tk.W,
            bg="#1e1e1e", fg="#aaaaaa"
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def send_command(self, event=None):
        user_input = self.command_entry.get()
        self.command_entry.delete(0, END)
        if not user_input.strip():
            return
        self._handle_input(user_input)

    def listen_command(self):
        def capture():
            self.status_bar.config(text="🎤 Listening...")
            self.output_display.insert(END, "System: Listening...\n")
            self.output_display.see(END)
            result = self.stt.listen()
            if result and len(result.strip()) > 2:
                self._handle_input(result)
            else:
                self.output_display.insert(END, "System: No valid speech detected.\n")
                self.output_display.see(END)
            self.status_bar.config(text="🟢 Jarvis is standing by")

        threading.Thread(target=capture, daemon=True).start()

    def _handle_input(self, user_input):
        self.output_display.insert(END, f"You: {user_input}\n")
        self.output_display.see(END)
        self.status_bar.config(text="🧠 Thinking...")

        threading.Thread(target=self._get_response, args=(user_input,), daemon=True).start()

    def _get_response(self, command):
        self.memory.add_interaction("user", command)
        response = self.ai_engine.process(command)
        self.memory.add_interaction("jarvis", response)

        self.output_display.insert(END, f"Jarvis: {response}\n")
        self.output_display.see(END)

        self.tts.speak(response)
        self.status_bar.config(text="🟢 Jarvis is standing by")

    def _on_voice_detected(self):
        if not self.is_listening and self.voice_detector:
            self.is_listening = True
            self.status_bar.config(text="🎤 Detected voice... Listening...")
            self.listen_command()
            self.root.after(5000, lambda: setattr(self, "is_listening", False))

    def cleanup(self):
        """Clean up resources when closing"""
        if self.voice_detector:
            try:
                self.voice_detector.stop()
            except Exception as e:
                logger.error(f"Error stopping voice detector: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()
