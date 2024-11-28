import pandas as pd
from typing import Union, Dict, Any
from utils.db_utils import DatabaseManager
import uuid

class StructuredDataLoader:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def load_csv(self, file_path: str, text_column: str) -> Dict[str, Any]:
        """Load and process CSV file"""
        try:
            df = pd.read_csv(file_path)
            if text_column not in df.columns:
                raise ValueError(f"Column {text_column} not found in CSV file")
            
            # Process each text entry
            for _, row in df.iterrows():
                text_id = str(uuid.uuid4())
                self.db_manager.save_text_data(
                    text_id=text_id,
                    source_file=file_path,
                    content=row[text_column]
                )
            
            return {"status": "success", "rows_processed": len(df)}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def load_xlsx(self, file_path: str, text_column: str, sheet_name: Union[str, int] = 0) -> Dict[str, Any]:
        """Load and process Excel file"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            if text_column not in df.columns:
                raise ValueError(f"Column {text_column} not found in Excel file")
            
            # Process each text entry
            for _, row in df.iterrows():
                text_id = str(uuid.uuid4())
                self.db_manager.save_text_data(
                    text_id=text_id,
                    source_file=file_path,
                    content=row[text_column]
                )
            
            return {"status": "success", "rows_processed": len(df)}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
