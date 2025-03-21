"""
Task Manager Module for Jarvis AI Assistant.
Handles scheduling, execution, and tracking of tasks.
"""

import threading
import time
from utils.logger import get_logger

logger = get_logger(__name__)

class TaskManager:
    """Manages tasks for Jarvis."""

    def __init__(self):
        logger.info("Initializing Task Manager...")
        self.tasks = []
        self.task_lock = threading.Lock()
        self.running = False

    def add_task(self, task_name, task_function, *args, **kwargs):
        """
        Add a new task to the queue.
        `task_function` should be a callable.
        """
        task = {
            "name": task_name,
            "function": task_function,
            "args": args,
            "kwargs": kwargs,
            "status": "pending"
        }
        with self.task_lock:
            self.tasks.append(task)
        logger.info(f"Task added: {task_name}")

    def execute_tasks(self):
        """Continuously execute tasks in the queue."""
        logger.info("Starting task execution loop...")
        self.running = True
        while self.running:
            with self.task_lock:
                pending_tasks = [t for t in self.tasks if t["status"] == "pending"]
            for task in pending_tasks:
                logger.info(f"Executing task: {task['name']}")
                try:
                    task["status"] = "in_progress"
                    result = task["function"](*task["args"], **task["kwargs"])
                    task["status"] = "completed"
                    task["result"] = result
                    logger.info(f"Task completed: {task['name']}")
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    logger.error(f"Task failed: {task['name']} with error: {str(e)}")
            time.sleep(1)  # Wait before processing the next batch

    def start(self):
        """Start the task manager in a separate thread."""
        threading.Thread(target=self.execute_tasks, daemon=True).start()
        logger.info("Task Manager started.")

    def stop(self):
        """Stop the task execution loop."""
        self.running = False
        logger.info("Task Manager stopped.")

    def get_tasks(self):
        """Return the list of tasks."""
        with self.task_lock:
            return list(self.tasks)
