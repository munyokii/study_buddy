"""Database and Hugging Face API Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the application."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    HUGGING_API_KEY = os.getenv("HUGGING_API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
