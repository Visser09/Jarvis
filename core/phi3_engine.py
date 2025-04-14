import os
from llama_cpp import Llama
from utils.logger import get_logger

logger = get_logger(__name__)

class Phi3Engine:
    def __init__(self, memory_manager):
        logger.info("Initializing Phi-3 Engine...")
        self.memory_manager = memory_manager

        self.model_path = "D:\\models\\Phi-3-mini-4k-instruct-q4.gguf"  # Update if stored elsewhere
        self.max_tokens = 200
        self.temperature = 0.7
        self.context_window = 4096

        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=self.context_window,
            verbose=False
        )

        logger.info("Phi-3 Engine loaded successfully.")

    def process(self, text):
        logger.info(f"Processing input: {text}")
        history = self.memory_manager.get_recent_interactions(3)

        messages = self._build_messages(text, history)

        response = self.llm.create_chat_completion(
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        reply = response["choices"][0]["message"]["content"].strip()
        logger.info(f"Phi-3 response: {reply}")
        return reply

    def _build_messages(self, user_input, history):
        # Build the system prompt
        system_prompt = {
            "role": "system",
            "content": (
                "You are Jarvis, a highly intelligent, fast, and respectful AI assistant. "
                "You speak clearly, briefly, and always address the user as 'sir'. "
                "Respond like a human assistant would, but never exceed 2 sentences unless asked."
            )
        }

        # Format memory
        chat = [system_prompt]
        for entry in history[-2:]:
            role = "user" if entry["speaker"].lower() == "user" else "assistant"
            chat.append({"role": role, "content": entry["text"]})

        # Append the current input
        chat.append({"role": "user", "content": user_input})
        return chat
