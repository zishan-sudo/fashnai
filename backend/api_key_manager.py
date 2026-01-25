"""
API Key Manager for rotating multiple Gemini API keys
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class APIKeyManager:
    """Manages rotation of multiple Gemini API keys to avoid rate limits"""
    
    def __init__(self):
        self.keys: List[str] = []
        self.current_index = 0
        
        # Load all available API keys
        for i in range(1, 10):  # Support up to 9 keys
            key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if key:
                self.keys.append(key)
        
        # Fallback to single key if no numbered keys found
        if not self.keys:
            single_key = os.getenv("GOOGLE_API_KEY")
            if single_key:
                self.keys.append(single_key)
        
        if not self.keys:
            raise ValueError("No GOOGLE_API_KEY found in environment variables")
    
    def get_next_key(self) -> str:
        """Get the next API key in rotation"""
        if not self.keys:
            raise ValueError("No API keys available")
        
        key = self.keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.keys)
        return key
    
    def get_key_for_agent(self, agent_name: str) -> str:
        """Get a specific key for an agent (round-robin distribution)"""
        if not self.keys:
            raise ValueError("No API keys available")
        
        # Hash agent name to consistently assign same key
        agent_hash = hash(agent_name) % len(self.keys)
        return self.keys[agent_hash]
    
    @property
    def total_keys(self) -> int:
        """Total number of available keys"""
        return len(self.keys)


# Global instance
api_key_manager = APIKeyManager()
