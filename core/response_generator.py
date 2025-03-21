"""
Response Generator Module for Jarvis AI Assistant.
This module formats the responses from the AI Engine and prepares them for output.
"""

from utils.logger import get_logger

logger = get_logger(__name__)

class ResponseGenerator:
    """Formats and structures responses."""

    def __init__(self):
        logger.info("Initializing Response Generator...")

    def format_response(self, response):
        """
        Format the raw response text.
        You can add additional formatting (e.g. appending a signature, markdown formatting, etc.).
        """
        formatted_response = response.strip()
        logger.debug("Response formatted.")
        return formatted_response

    def generate_error_response(self, error_message):
        """
        Generate a standardized error response.
        """
        logger.error("Generating error response.")
        return f"Error: {error_message}"
