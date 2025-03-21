"""
Helper functions for Jarvis AI Assistant.
"""

import os
import json

def load_json(file_path):
    """Load JSON data from a file."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(data, file_path):
    """Save JSON data to a file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def ensure_dir(directory):
    """Ensure that a directory exists; create it if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)
