import whisper
import os
import uuid
from typing import Dict, Any
from utils.db_utils import DatabaseManager

class AudioProcessor:
    def __init__(self, db_manager: DatabaseManager, model_size: str = 'base'):
        """Initialize with specified Whisper model size"""
        self.model = whisper.load_model(model_size)
        self.db_manager = db_manager

    def transcribe_audio(self, file_path: str, save_transcript: bool = True) -> Dict[str, Any]:
        """Transcribe audio file using Whisper"""
        try:
            # Check if file exists and is audio
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            if not file_path.lower().endswith(('.mp3', '.mp4', '.wav', '.m4a')):
                raise ValueError("Unsupported audio format")

            # Transcribe audio
            result = self.model.transcribe(file_path)
            transcript = result["text"]

            if not transcript.strip():
                return {"status": "error", "message": "No speech detected in audio"}

            # Save transcript if requested
            if save_transcript:
                # Generate unique ID for this transcript
                text_id = str(uuid.uuid4())
                
                # Save to database
                self.db_manager.save_text_data(
                    text_id=text_id,
                    source_file=file_path,
                    content=transcript
                )

                return {
                    "status": "success",
                    "text_id": text_id,
                    "transcript": transcript
                }
            
            return {
                "status": "success",
                "transcript": transcript
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
