"""
Proactive Assistance Module for Jarvis AI Assistant.
Provides proactive suggestions and assistance based on context.
"""

import threading
import time
from utils.logger import get_logger

logger = get_logger(__name__)

class ProactiveAssistant:
    """Provides proactive assistance."""

    def __init__(self, task_manager):
        """
        Initialize with a reference to the Task Manager to schedule tasks.
        """
        self.task_manager = task_manager
        self.running = False

    def start_monitoring(self):
        """Start monitoring in a separate thread."""
        self.running = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        logger.info("Proactive Assistant monitoring started.")

    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.running = False
        logger.info("Proactive Assistant monitoring stopped.")

    def _monitor_loop(self):
        """
        Monitor conditions to provide proactive assistance.
        For demonstration, we simulate a condition check.
        """
        while self.running:
            # For example, every 30 seconds, check for a condition.
            time.sleep(30)
            self._check_conditions()

    def _check_conditions(self):
        """
        Check conditions and add a proactive task if needed.
        This is a simulated check—for instance, suggesting a morning briefing.
        """
        logger.info("Proactive Assistant checking conditions...")
        current_hour = time.localtime().tm_hour
        if current_hour == 9:
            # Propose a morning briefing task
            self.task_manager.add_task(
                "Morning Briefing",
                self._morning_briefing_task
            )
            logger.info("Proactive task added: Morning Briefing")

    def _morning_briefing_task(self):
        """
        A sample proactive task: generate a morning briefing.
        """
        # Simulate task processing
        time.sleep(2)
        briefing = "Good morning, sir. Here is your briefing for the day: All systems are operational."
        logger.info("Morning Briefing task executed.")
        return briefing

