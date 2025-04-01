import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'processed')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 