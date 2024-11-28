import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Union
import uuid
from utils.db_utils import DatabaseManager

class XMLJSONLoader:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def load_json(self, file_path: str, text_fields: Union[str, list]) -> Dict[str, Any]:
        """Load and process JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(text_fields, str):
                text_fields = [text_fields]

            processed_texts = []
            
            def extract_text_fields(obj, current_path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{current_path}.{key}" if current_path else key
                        if key in text_fields:
                            if isinstance(value, str):
                                processed_texts.append(value)
                        extract_text_fields(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_path = f"{current_path}[{i}]"
                        extract_text_fields(item, new_path)

            extract_text_fields(data)

            if not processed_texts:
                return {"status": "error", "message": f"No text found in fields: {text_fields}"}

            # Save each text to database
            text_ids = []
            for text in processed_texts:
                text_id = str(uuid.uuid4())
                self.db_manager.save_text_data(
                    text_id=text_id,
                    source_file=file_path,
                    content=text
                )
                text_ids.append(text_id)

            return {"status": "success", "text_ids": text_ids}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def load_xml(self, file_path: str, text_tags: Union[str, list]) -> Dict[str, Any]:
        """Load and process XML file"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            if isinstance(text_tags, str):
                text_tags = [text_tags]

            processed_texts = []
            
            def extract_text_from_element(element):
                if element.tag in text_tags:
                    text = element.text
                    if text and text.strip():
                        processed_texts.append(text.strip())
                for child in element:
                    extract_text_from_element(child)

            extract_text_from_element(root)

            if not processed_texts:
                return {"status": "error", "message": f"No text found in tags: {text_tags}"}

            # Save each text to database
            text_ids = []
            for text in processed_texts:
                text_id = str(uuid.uuid4())
                self.db_manager.save_text_data(
                    text_id=text_id,
                    source_file=file_path,
                    content=text
                )
                text_ids.append(text_id)

            return {"status": "success", "text_ids": text_ids}

        except Exception as e:
            return {"status": "error", "message": str(e)}
