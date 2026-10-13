import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
load_dotenv(Path(__file__).resolve().parents[2] / '.env')
SERPAPI_KEY = os.getenv('SERPAPI_API_KEY', '')
LLM_KEY = os.getenv('LLM_API_KEY', '')
LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
LLM_MODEL = os.getenv('LLM_MODEL', '')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./scamshield.db')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
MAX_UPLOAD = 5 * 1024 * 1024
