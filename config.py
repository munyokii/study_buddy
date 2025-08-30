"""Database and Hugging Face API Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the application."""
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    HUGGING_API_KEY = os.getenv("HUGGING_API_KEY")
    HUGGING_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

    SECRET_KEY = os.getenv("SECRET_KEY")
