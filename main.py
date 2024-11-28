import os
import argparse
from typing import List, Dict
from tqdm import tqdm

from config import (
    DATA_DIR, AUDIO_DIR, TRANSCRIPT_DIR, VECTOR_DIR,
    WHISPER_MODEL, FASTTEXT_MODEL, VECTOR_DIMENSION
)
from utils.db_utils import DatabaseManager
from utils.text_utils import TextPreprocessor
from utils.vector_utils import VectorManager
from modules.structured_data import StructuredDataLoader
from modules.document_data import DocumentLoader
from modules.audio_data import AudioProcessor
from modules.xml_json_data import XMLJSONLoader

def process_files(
    file_paths: List[str],
    text_column: str = None,
    text_fields: List[str] = None,
    text_tags: List[str] = None
) -> Dict[str, List[str]]:
    """Process multiple files and return text IDs"""
    
    # Initialize managers and processors
    db_manager = DatabaseManager()
    structured_loader = StructuredDataLoader(db_manager)
    document_loader = DocumentLoader(db_manager)
    audio_processor = AudioProcessor(db_manager, WHISPER_MODEL)
    xml_json_loader = XMLJSONLoader(db_manager)
    
    results = {
        "success": [],
        "failed": []
    }
    
    for file_path in tqdm(file_paths, desc="Processing files"):
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.csv']:
                result = structured_loader.load_csv(file_path, text_column)
            elif file_ext in ['.xlsx', '.xls']:
                result = structured_loader.load_xlsx(file_path, text_column)
            elif file_ext == '.pdf':
                result = document_loader.load_pdf(file_path)
            elif file_ext == '.txt':
                result = document_loader.load_txt(file_path)
            elif file_ext in ['.mp3', '.mp4', '.wav', '.m4a']:
                result = audio_processor.transcribe_audio(file_path)
            elif file_ext == '.json':
                result = xml_json_loader.load_json(file_path, text_fields)
            elif file_ext in ['.xml', '.html']:
                result = xml_json_loader.load_xml(file_path, text_tags)
            else:
                result = {"status": "error", "message": f"Unsupported file type: {file_ext}"}
            
            if result["status"] == "success":
                results["success"].append(file_path)
            else:
                results["failed"].append((file_path, result["message"]))
                
        except Exception as e:
            results["failed"].append((file_path, str(e)))
    
    return results

def process_texts():
    """Process all unprocessed texts in the database"""
    db_manager = DatabaseManager()
    text_processor = TextPreprocessor()
    vector_manager = VectorManager(FASTTEXT_MODEL, VECTOR_DIMENSION)
    
    # Get unprocessed texts
    texts = db_manager.get_unprocessed_texts()
    if not texts:
        print("No unprocessed texts found")
        return
    
    print(f"Processing {len(texts)} texts...")
    for text in tqdm(texts):
        # Clean and preprocess text
        processed_text = text_processor.preprocess_text(text.content)
        
        # Update processed content in database
        db_manager.save_text_data(
            text_id=text.id,
            source_file=text.source_file,
            content=text.content,
            processed_content=processed_text
        )
        
        # Generate and save vector
        vector = vector_manager.text_to_vector(processed_text)
        vector_manager.add_to_index(vector.reshape(1, -1))
    
    # Save the FAISS index
    vector_manager.save_index(os.path.join(VECTOR_DIR, 'faiss_index'))
    print("Text processing and vectorization complete")

def main():
    parser = argparse.ArgumentParser(description='Data Processing Pipeline')
    parser.add_argument('--input_dir', type=str, help='Directory containing input files')
    parser.add_argument('--text_column', type=str, help='Column name for structured data files')
    parser.add_argument('--text_fields', type=str, nargs='+', help='Field names for JSON files')
    parser.add_argument('--text_tags', type=str, nargs='+', help='Tag names for XML files')
    
    args = parser.parse_args()
    
    if args.input_dir:
        # Get all files in input directory
        file_paths = []
        for root, _, files in os.walk(args.input_dir):
            for file in files:
                file_paths.append(os.path.join(root, file))
        
        # Process files
        results = process_files(
            file_paths,
            args.text_column,
            args.text_fields,
            args.text_tags
        )
        
        print(f"\nProcessed {len(results['success'])} files successfully")
        if results['failed']:
            print(f"Failed to process {len(results['failed'])} files:")
            for file_path, error in results['failed']:
                print(f"  {file_path}: {error}")
    
    # Process and vectorize texts
    process_texts()

if __name__ == "__main__":
    main()
