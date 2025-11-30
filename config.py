"""
Configuration Module
Stores configuration settings and environment variables.
"""

import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Gmail Summarizer."""
    
    # OpenAI API Key
    API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Gmail API credentials
    CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
    TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'token.pickle')
    
    # Email fetch settings
    MAX_EMAILS = int(os.getenv('MAX_EMAILS', '10'))
    
    # Email filter query (e.g., 'is:unread', 'from:example@email.com')
    EMAIL_QUERY = os.getenv('EMAIL_QUERY', '')
    
    # Summarizer settings
    SUMMARY_MAX_LENGTH = int(os.getenv('SUMMARY_MAX_LENGTH', '150'))
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in .env file."
            )
        
        if not os.path.exists(cls.CREDENTIALS_FILE):
            print(f"Warning: Gmail credentials file '{cls.CREDENTIALS_FILE}' not found.")
            print("You'll need to download it from Google Cloud Console.")
