import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'data_pipeline')
}

# File paths
DATA_DIR = 'data'
AUDIO_DIR = os.path.join(DATA_DIR, 'audio')
TRANSCRIPT_DIR = os.path.join(DATA_DIR, 'transcripts')
VECTOR_DIR = os.path.join(DATA_DIR, 'vectors')

# Ensure directories exist
for dir_path in [DATA_DIR, AUDIO_DIR, TRANSCRIPT_DIR, VECTOR_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Model configurations
WHISPER_MODEL = 'base'
FASTTEXT_MODEL = 'cc.en.300.bin'
VECTOR_DIMENSION = 300

# Processing configurations
BATCH_SIZE = 32
MAX_TEXT_LENGTH = 10000
