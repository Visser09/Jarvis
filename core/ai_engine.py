"""
AI Engine - GPT-3.5-turbo Integration
"""
import os
import json
import time
import openai
from utils.logger import get_logger

logger = get_logger(__name__)

class AIEngine:
    """AI Engine using GPT-3.5-turbo via OpenAI's API for natural language processing"""
    
    def __init__(self, memory_manager):
        """Initialize the AI Engine using the OpenAI API"""
        logger.info("Initializing AI Engine with GPT-3.5-turbo...")
        self.memory_manager = memory_manager
        
        # Load personality traits from configuration
        self.personality = self._load_personality()
        
        # Set the model name to GPT-3.5-turbo
        self.model_name = "gpt-3.5-turbo"
        
        # Set up OpenAI API key (should be in your environment variables)
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            logger.error("OpenAI API key not found in environment variables!")
        else:
            logger.info("OpenAI API key loaded successfully.")
        
        logger.info("AI Engine initialization complete.")
    
    def _load_personality(self):
        """Load Jarvis personality traits from the configuration file"""
        try:
            with open("config/personality.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Personality file not found. Using default personality.")
            return {
                "name": "Jarvis",
                "tone": "friendly and professional",
                "style": "concise and engaging",
                "address_user_as": "sir",
                "common_phrases": [
                    "At your service, sir.",
                    "How may I assist you?",
                    "Certainly, sir.",
                    "As you wish, sir."
                ]
            }
    
    def process(self, text):
        """Process user input and generate a response using GPT-3.5-turbo"""
        start_time = time.time()
        
        # Retrieve recent conversation history (last 5 interactions)
        history = self.memory_manager.get_recent_interactions(5)
        
        # Prepare messages for the ChatCompletion API
        messages = self._prepare_messages(text, history)
        
        # Get response from OpenAI
        response = self._generate_response(messages)
        
        processing_time = time.time() - start_time
        logger.debug(f"AI response generated in {processing_time:.2f} seconds")
        return response
    
    def _prepare_messages(self, text, history):
        """
        Prepare a list of messages for the ChatCompletion API.
        The list includes:
          - a system message with instructions and personality,
          - any conversation history,
          - and the current user message.
        """
        # System message defines the assistant's behavior
        system_message = (
            f"You are Jarvis, a friendly, helpful, and professional AI assistant. "
            f"Your tone is {self.personality.get('tone', 'friendly')}, "
            f"and you speak in a {self.personality.get('style', 'concise and engaging')} manner. "
            f"Always address the user as '{self.personality.get('address_user_as', 'sir')}'."
        )
        
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history if available
        for entry in history:
            role = "user" if entry["speaker"].lower() == "user" else "assistant"
            messages.append({"role": role, "content": entry["text"]})
        
        # Add the current user message
        messages.append({"role": "user", "content": text})
        return messages
    
    def _generate_response(self, messages):
        """Call OpenAI's ChatCompletion API to generate a response"""
        try:
            completion = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=150  # adjust as needed
            )
            # Extract the assistant's response
            response = completion.choices[0].message["content"].strip()
            return response
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble processing that request at the moment."
    
    def fine_tune(self, training_data):
        """Placeholder for fine-tuning functionality (not applicable with OpenAI API)"""
        logger.info("Fine-tuning functionality not implemented for GPT-3.5-turbo.")
        pass
