"""
Memory Manager for Jarvis AI
"""
import os
import json
import time
import sqlite3
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

class MemoryManager:
    """Manages both short-term and long-term memory for Jarvis"""
    
    def __init__(self):
        """Initialize the memory systems"""
        logger.info("Initializing Memory Manager...")
        
        # Ensure directories exist
        os.makedirs("data/memory", exist_ok=True)
        
        # Initialize short-term memory (JSON-based)
        self.short_term_file = "data/memory/short_term.json"
        self.short_term_memory = self._load_short_term_memory()
        
        # Initialize long-term memory (SQLite-based)
        self.long_term_db = "data/memory/long_term.db"
        self._initialize_long_term_memory()
        
        logger.info("Memory Manager initialized successfully.")
    
    def _load_short_term_memory(self):
        """Load short-term memory from JSON file"""
        try:
            with open(self.short_term_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("Creating new short-term memory file.")
            return {
                "interactions": [],
                "user_preferences": {},
                "active_tasks": []
            }
    
    def _initialize_long_term_memory(self):
        """Initialize long-term memory database"""
        try:
            conn = sqlite3.connect(self.long_term_db)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    speaker TEXT,
                    text TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learned_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT,
                    source TEXT,
                    timestamp TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
    
    def add_interaction(self, speaker, text):
        """Add a new interaction to memory"""
        timestamp = datetime.now().isoformat()
        
        # Add to short-term memory
        self.short_term_memory["interactions"].append({
            "timestamp": timestamp,
            "speaker": speaker,
            "text": text
        })
        
        # Keep short-term memory at a reasonable size
        if len(self.short_term_memory["interactions"]) > 50:
            self.short_term_memory["interactions"] = self.short_term_memory["interactions"][-50:]
        
        # Save to short-term memory file
        self._save_short_term_memory()
        
        # Add to long-term memory
        try:
            conn = sqlite3.connect(self.long_term_db)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO interactions (timestamp, speaker, text) VALUES (?, ?, ?)",
                (timestamp, speaker, text)
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
    
    def get_recent_interactions(self, count=5):
        """Get the most recent interactions"""
        return self.short_term_memory["interactions"][-count:]
    
    def save_user_preference(self, key, value):
        """Save a user preference"""
        timestamp = datetime.now().isoformat()
        
        # Update in short-term memory
        self.short_term_memory["user_preferences"][key] = {
            "value": value,
            "timestamp": timestamp
        }
        
        # Save to short-term memory file
        self._save_short_term_memory()
        
        # Update in long-term memory
        try:
            conn = sqlite3.connect(self.long_term_db)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value, timestamp) VALUES (?, ?, ?)",
                (key, json.dumps(value), timestamp)
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
    
    def get_user_preference(self, key, default=None):
        """Get a user preference"""
        if key in self.short_term_memory["user_preferences"]:
            return self.short_term_memory["user_preferences"][key]["value"]
        return default
    
    def learn_fact(self, fact, source="user"):
        """Store a learned fact in long-term memory"""
        timestamp = datetime.now().isoformat()
        
        try:
            conn = sqlite3.connect(self.long_term_db)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO learned_facts (fact, source, timestamp) VALUES (?, ?, ?)",
                (fact, source, timestamp)
            )
            conn.commit()
            conn.close()
            logger.info(f"Learned new fact: {fact}")
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
    
    def _save_short_term_memory(self):
        """Save short-term memory to JSON file"""
        try:
            with open(self.short_term_file, "w") as f:
                json.dump(self.short_term_memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving short-term memory: {str(e)}")
    
    def search_memory(self, query, limit=10):
        """Search long-term memory for relevant information"""
        try:
            conn = sqlite3.connect(self.long_term_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT timestamp, speaker, text FROM interactions WHERE text LIKE ? ORDER BY timestamp DESC LIMIT ?",
                (f"%{query}%", limit)
            )
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "timestamp": row[0],
                    "speaker": row[1],
                    "text": row[2]
                }
                for row in results
            ]
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
            return []
    
    def save(self):
        """Save all memory data"""
        self._save_short_term_memory()
        logger.info("Memory saved successfully.")