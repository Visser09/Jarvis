"""
Tests for the Security Manager module.
"""
import pytest
import os
from utils.security import SecurityManager

@pytest.fixture
def security_manager():
    """Create a SecurityManager instance for testing"""
    return SecurityManager()

def test_encryption_decryption(security_manager):
    """Test encryption and decryption of data"""
    test_data = "sensitive information"
    
    # Encrypt data
    encrypted = security_manager.encrypt_data(test_data)
    assert encrypted != test_data
    assert isinstance(encrypted, bytes)
    
    # Decrypt data
    decrypted = security_manager.decrypt_data(encrypted)
    assert decrypted == test_data

def test_api_key_management(security_manager, monkeypatch):
    """Test API key management and rotation"""
    # Set up test environment variables
    monkeypatch.setenv("TEST_SERVICE_API_KEY", "test_key_1")
    
    # Test initial key storage
    security_manager.rotate_api_key("test_service")
    key = security_manager.get_api_key("test_service")
    assert key == "test_key_1"
    
    # Test key rotation
    monkeypatch.setenv("TEST_SERVICE_API_KEY", "test_key_2")
    key = security_manager.get_api_key("test_service")
    assert key == "test_key_2"

def test_user_management(security_manager):
    """Test user creation and verification"""
    username = "test_user"
    password = "test_password"
    
    # Test user creation
    security_manager.create_user(username, password)
    
    # Test user verification
    assert security_manager.verify_user(username, password)
    assert not security_manager.verify_user(username, "wrong_password")
    assert not security_manager.verify_user("wrong_user", password)

def test_persistence(security_manager, tmp_path):
    """Test persistence of API keys"""
    # Create a test user
    security_manager.create_user("test_user", "test_password")
    
    # Save API keys
    security_manager._save_api_keys()
    
    # Create a new instance
    new_manager = SecurityManager(security_manager.encryption_key)
    
    # Verify data persistence
    assert new_manager.verify_user("test_user", "test_password") 