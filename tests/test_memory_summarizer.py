"""
Tests for the Memory Summarizer module.
"""
import pytest
from datetime import datetime, timedelta
from core.memory_summarizer import MemorySummarizer

@pytest.fixture
def memory_summarizer():
    """Create a MemorySummarizer instance for testing"""
    return MemorySummarizer(max_interactions=10, summary_threshold=5)

@pytest.fixture
def sample_interactions():
    """Create sample interactions for testing"""
    base_time = datetime.now()
    return [
        {
            "timestamp": (base_time - timedelta(days=i)).isoformat(),
            "speaker": "user" if i % 2 == 0 else "jarvis",
            "text": f"Test interaction {i}"
        }
        for i in range(15)
    ]

def test_summarize_interactions(memory_summarizer, sample_interactions):
    """Test interaction summarization"""
    summary = memory_summarizer.summarize_interactions(sample_interactions)
    
    assert "period" in summary
    assert "total_interactions" in summary
    assert "daily_summaries" in summary
    assert summary["total_interactions"] == len(sample_interactions)
    assert len(summary["daily_summaries"]) > 0

def test_cleanup_old_interactions(memory_summarizer, sample_interactions):
    """Test cleanup of old interactions"""
    cleaned, summaries = memory_summarizer.cleanup_old_interactions(
        sample_interactions,
        max_age_days=5
    )
    
    # Check that old interactions were removed
    assert len(cleaned) <= len(sample_interactions)
    
    # Check that summaries were created
    assert len(summaries) > 0
    
    # Check that we don't exceed max_interactions
    assert len(cleaned) <= memory_summarizer.max_interactions

def test_topic_extraction(memory_summarizer):
    """Test topic extraction from interactions"""
    interactions = [
        {
            "timestamp": datetime.now().isoformat(),
            "speaker": "user",
            "text": "What's the weather like today?"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "speaker": "jarvis",
            "text": "Let me check the weather for you."
        }
    ]
    
    summary = memory_summarizer.summarize_interactions(interactions)
    topics = summary["daily_summaries"][0]["topics"]
    
    assert "weather" in topics

def test_key_points_extraction(memory_summarizer):
    """Test key points extraction from interactions"""
    interactions = [
        {
            "timestamp": datetime.now().isoformat(),
            "speaker": "user",
            "text": "Remember to check the weather tomorrow"
        }
    ]
    
    summary = memory_summarizer.summarize_interactions(interactions)
    key_points = summary["daily_summaries"][0]["key_points"]
    
    assert len(key_points) > 0
    assert "Remember to check the weather tomorrow" in key_points

def test_save_load_summaries(memory_summarizer, sample_interactions, tmp_path):
    """Test saving and loading summaries"""
    # Create a summary
    summary = memory_summarizer.summarize_interactions(sample_interactions)
    
    # Save summary
    test_file = tmp_path / "test_summaries.json"
    memory_summarizer.save_summaries([summary], str(test_file))
    
    # Load summary
    loaded_summaries = memory_summarizer.load_summaries(str(test_file))
    
    assert len(loaded_summaries) == 1
    assert loaded_summaries[0]["total_interactions"] == summary["total_interactions"] 