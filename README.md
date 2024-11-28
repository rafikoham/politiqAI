# Data Processing Pipeline

This project implements a comprehensive data processing pipeline that:
1. Loads various data formats (CSV, XLSX, XML, JSON, PDF, TXT)
2. Transcribes audio files (MP3, MP4) using OpenAI Whisper
3. Processes and cleans text data
4. Creates vector embeddings using FastText
5. Stores vectors in FAISS

## Setup
1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your database configuration:
```
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=your_db_name
```

3. Download FastText model:
```python
python -c "import fasttext.util; fasttext.util.download_model('en', if_exists='ignore')"
```

## Usage
Run the main script:
```bash
python main.py
```

## Project Structure
- `main.py`: Main execution script
- `modules/`: Contains modules for different data types
  - `structured_data.py`: CSV and XLSX processing
  - `document_data.py`: PDF and TXT processing
  - `audio_data.py`: MP3 and MP4 processing
  - `xml_json_data.py`: XML and JSON processing
- `utils/`: Utility functions
  - `db_utils.py`: Database operations
  - `text_utils.py`: Text processing utilities
  - `vector_utils.py`: Vector operations
- `config.py`: Configuration settings
