"""
Memory Summarization module for Jarvis AI Assistant.
"""
import json
from datetime import datetime, timedelta
from utils.logger import get_logger
import os

logger = get_logger(__name__)

class MemorySummarizer:
    """Handles memory summarization and cleanup"""
    
    def __init__(self, max_interactions=100, summary_threshold=50):
        """
        Initialize the memory summarizer
        Args:
            max_interactions (int): Maximum number of interactions to keep
            summary_threshold (int): Number of interactions before summarizing
        """
        self.max_interactions = max_interactions
        self.summary_threshold = summary_threshold
        logger.info("Memory Summarizer initialized")
    
    def summarize_interactions(self, interactions):
        """
        Summarize a list of interactions
        Args:
            interactions (list): List of interaction dictionaries
        Returns:
            dict: Summary of the interactions
        """
        try:
            if not interactions:
                return {}
            
            # Group interactions by date
            date_groups = {}
            for interaction in interactions:
                date = datetime.fromisoformat(interaction["timestamp"]).date()
                if date not in date_groups:
                    date_groups[date] = []
                date_groups[date].append(interaction)
            
            # Create summary
            summary = {
                "period": {
                    "start": min(date_groups.keys()).isoformat(),
                    "end": max(date_groups.keys()).isoformat()
                },
                "total_interactions": len(interactions),
                "daily_summaries": []
            }
            
            # Summarize each day
            for date, day_interactions in date_groups.items():
                day_summary = {
                    "date": date.isoformat(),
                    "interaction_count": len(day_interactions),
                    "topics": self._extract_topics(day_interactions),
                    "key_points": self._extract_key_points(day_interactions)
                }
                summary["daily_summaries"].append(day_summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing interactions: {str(e)}")
            return {}
    
    def _extract_topics(self, interactions):
        """Extract main topics from interactions"""
        topics = set()
        for interaction in interactions:
            # Simple topic extraction based on keywords
            text = interaction["text"].lower()
            if "weather" in text:
                topics.add("weather")
            if "time" in text or "schedule" in text:
                topics.add("time")
            if "search" in text or "look up" in text:
                topics.add("search")
            if "application" in text or "app" in text:
                topics.add("applications")
            if "screen" in text or "monitor" in text:
                topics.add("screen")
        return list(topics)
    
    def _extract_key_points(self, interactions):
        """Extract key points from interactions"""
        key_points = []
        for interaction in interactions:
            # Look for important commands or information
            text = interaction["text"].lower()
            if any(keyword in text for keyword in ["remember", "note", "important"]):
                key_points.append(interaction["text"])
        return key_points
    
    def cleanup_old_interactions(self, interactions, max_age_days=30):
        """
        Remove old interactions and create summaries
        Args:
            interactions (list): List of interaction dictionaries
            max_age_days (int): Maximum age of interactions to keep
        Returns:
            tuple: (cleaned_interactions, summaries)
        """
        try:
            current_date = datetime.now()
            cutoff_date = current_date - timedelta(days=max_age_days)
            
            # Separate old and new interactions
            old_interactions = []
            new_interactions = []
            
            for interaction in interactions:
                interaction_date = datetime.fromisoformat(interaction["timestamp"])
                if interaction_date < cutoff_date:
                    old_interactions.append(interaction)
                else:
                    new_interactions.append(interaction)
            
            # Create summaries for old interactions
            summaries = []
            if old_interactions:
                summary = self.summarize_interactions(old_interactions)
                if summary:
                    summaries.append(summary)
            
            # Ensure we don't exceed max_interactions
            if len(new_interactions) > self.max_interactions:
                # Keep the most recent interactions
                new_interactions = new_interactions[-self.max_interactions:]
            
            return new_interactions, summaries
            
        except Exception as e:
            logger.error(f"Error cleaning up old interactions: {str(e)}")
            return interactions, []
    
    def save_summaries(self, summaries, filepath="data/memory/summaries.json"):
        """Save memory summaries to file"""
        try:
            # Load existing summaries
            existing_summaries = []
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    existing_summaries = json.load(f)
            
            # Add new summaries
            existing_summaries.extend(summaries)
            
            # Save updated summaries
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(existing_summaries, f, indent=2)
            
            logger.info(f"Saved {len(summaries)} new summaries")
            
        except Exception as e:
            logger.error(f"Error saving summaries: {str(e)}")
    
    def load_summaries(self, filepath="data/memory/summaries.json"):
        """Load memory summaries from file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading summaries: {str(e)}")
            return [] 