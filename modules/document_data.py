from pdfminer.high_level import extract_text
import uuid
from typing import Dict, Any
from utils.db_utils import DatabaseManager

class DocumentLoader:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def load_pdf(self, file_path: str) -> Dict[str, Any]:
        """Load and process PDF file"""
        try:
            # Extract text from PDF
            text = extract_text(file_path)
            
            if not text.strip():
                return {"status": "error", "message": "No text content found in PDF"}
            
            # Save to database
            text_id = str(uuid.uuid4())
            self.db_manager.save_text_data(
                text_id=text_id,
                source_file=file_path,
                content=text
            )
            
            return {"status": "success", "text_id": text_id}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def load_txt(self, file_path: str) -> Dict[str, Any]:
        """Load and process text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if not text.strip():
                return {"status": "error", "message": "Empty text file"}
            
            # Save to database
            text_id = str(uuid.uuid4())
            self.db_manager.save_text_data(
                text_id=text_id,
                source_file=file_path,
                content=text
            )
            
            return {"status": "success", "text_id": text_id}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
