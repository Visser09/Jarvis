"""
Settings for Jarvis AI Assistant.
"""

# General settings
DEBUG = True
LOG_LEVEL = "DEBUG"

# Audio settings
AUDIO = {
    "sample_rate": 44100,  # Changed from 16000 to 44100
    "chunk_size": 1024
}

# AI Engine settings
AI_ENGINE = {
    "model_name": "microsoft/phi-3-mini-4k-instruct",
    "max_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9
}

# Personality file location
PERSONALITY_FILE = "config/personality.json"
