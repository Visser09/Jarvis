"""
Security Manager for Jarvis
Handles API key encryption and decryption
"""
import os
import json
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from utils.logger import get_logger

logger = get_logger(__name__)

class SecurityManager:
    def __init__(self):
        """Initialize the security manager"""
        logger.info("Initializing Security Manager...")
        self.key_file = "config/security.key"
        self.api_file = "config/api_keys.json"
        self.fernet = None
        self._initialize_encryption()
        logger.info("Security Manager initialized")

    def _initialize_encryption(self):
        """Initialize encryption key"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    self.fernet = Fernet(f.read())
            else:
                # Generate new key if none exists
                self.fernet = Fernet.generate_key()
                os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
                with open(self.key_file, 'wb') as f:
                    f.write(self.fernet)
                self.fernet = Fernet(self.fernet)
        except Exception as e:
            logger.error(f"Error initializing encryption: {str(e)}")
            self.fernet = None

    def save_api_key(self, service, key):
        """Save an API key"""
        try:
            if not self.fernet:
                logger.error("Encryption not initialized")
                return False

            # Load existing keys
            keys = self.load_api_keys()
            if not keys:
                keys = {}

            # Encrypt and save the new key
            keys[service] = self.fernet.encrypt(key.encode()).decode()
            
            # Save to file
            os.makedirs(os.path.dirname(self.api_file), exist_ok=True)
            with open(self.api_file, 'w') as f:
                json.dump(keys, f)
            return True
        except Exception as e:
            logger.error(f"Error saving API key: {str(e)}")
            return False

    def load_api_keys(self):
        """Load all API keys"""
        try:
            if not self.fernet:
                logger.error("Encryption not initialized")
                return {}

            if not os.path.exists(self.api_file):
                return {}

            with open(self.api_file, 'r') as f:
                encrypted_keys = json.load(f)

            # Decrypt all keys
            decrypted_keys = {}
            for service, key in encrypted_keys.items():
                try:
                    decrypted_keys[service] = self.fernet.decrypt(key.encode()).decode()
                except Exception as e:
                    logger.error(f"Error decrypting key for {service}: {str(e)}")
                    continue

            return decrypted_keys
        except Exception as e:
            logger.error(f"Error loading API keys: {str(e)}")
            return {}

    def get_api_key(self, service):
        """Get a specific API key"""
        try:
            keys = self.load_api_keys()
            return keys.get(service)
        except Exception as e:
            logger.error(f"Error getting API key for {service}: {str(e)}")
            return None

    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        try:
            f = Fernet(self.fernet)
            if isinstance(data, str):
                data = data.encode()
            return f.encrypt(data)
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            f = Fernet(self.fernet)
            decrypted = f.decrypt(encrypted_data)
            return decrypted.decode() if isinstance(encrypted_data, bytes) else decrypted
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            raise
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        try:
            # In a real implementation, you would:
            # 1. Hash the password
            # 2. Compare with stored hash
            # 3. Implement proper session management
            # This is a simplified example
            stored_hash = self.load_api_keys().get("user_credentials", {}).get(username)
            if not stored_hash:
                return False
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            return hmac.compare_digest(password_hash, stored_hash)
            
        except Exception as e:
            logger.error(f"Error verifying user: {str(e)}")
            return False
    
    def create_user(self, username, password):
        """Create a new user"""
        try:
            if "user_credentials" not in self.load_api_keys():
                self.load_api_keys()["user_credentials"] = {}
            
            if username in self.load_api_keys()["user_credentials"]:
                raise ValueError("Username already exists")
            
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Store user credentials
            self.load_api_keys()["user_credentials"][username] = password_hash
            self.save_api_key("user_credentials", self.load_api_keys()["user_credentials"])
            
            logger.info(f"User {username} created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise 