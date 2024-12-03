from transformers import pipeline,AutoTokenizer
from loguru import logger
from pathlib import Path

import os
import whisper
import argparse

class AudioTranscriberV2:
    def __init__(self, model_size='base', output_dir='data/transcripts'):
        """Initialize with specified Whisper model size and output directory
        Available sizes: tiny, base, small, medium, large
        """
        logger.info(f"Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Model loaded successfully!")

        # Initialize Hugging Face transformers pipeline for NER
        self.tokenizer= AutoTokenizer.from_pretrained("cmarkea/distilcamembert-base-ner")

        self.ner_pipeline = pipeline(
            task='ner',
            model="cmarkea/distilcamembert-base-ner",
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"
        )

    def transcribe_file(self, audio_path):
        """Transcribe a single audio file and extract participants using transformers"""
        try:
            # Verify file exists and is audio
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            if not audio_path.lower().endswith(('.mp3', '.mp4', '.wav', '.m4a')):
                logger.error("Unsupported audio format. Use MP3, MP4, WAV, or M4A files.")
                raise ValueError("Unsupported audio format. Use MP3, MP4, WAV, or M4A files.")

            logger.info(f"\nTranscribing: {audio_path}")
            result = self.model.transcribe(audio_path)
            transcript = result["text"]

            if not transcript.strip():
                logger.warning("No speech detected in audio")
                return None

            # Extract participants using transformers NER
            ner_results = self.ner_pipeline(transcript)
            participants = [entity['word'] for entity in ner_results if entity['entity_group'] == 'PER']
            logger.info(f"Extracted participants: {participants}")  # Log the participants
            # Create output filename based on the video name
            audio_filename = Path(audio_path).stem
            output_path = self.output_dir / f"{audio_filename}.txt"
            
            # Save transcript
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("Participants: " + ", ".join(set(participants)) + "\n\n")  # Save participants at the beginning
                f.write(transcript)
            logger.info(f"Transcript saved to: {output_path}")

            return {
                'transcript_path': str(output_path),
                'participants': list(set(participants))  # Return unique names
            }

        except Exception as e:
            logger.error(f"Error processing {audio_path}: {str(e)}")
            return None

    def transcribe_directory(self, input_dir):
        """Transcribe all audio files in a specified directory"""
        transcribed_files = []
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(('.mp3', '.mp4', '.wav', '.m4a')):
                audio_path = os.path.join(input_dir, filename)
                result = self.transcribe_file(audio_path)
                if result:
                    transcribed_files.append(filename)
        return transcribed_files

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio files using Whisper')
    parser.add_argument('input', help='Input audio file or directory')
    parser.add_argument('--model', help='Whisper model size (tiny, base, small, medium, large)', default='base')
    parser.add_argument('--output', help='Output directory for transcripts', default='data/transcripts_v2')
    
    args = parser.parse_args()
    
    # Initialize transcriber
    transcriber = AudioTranscriberV2(model_size=args.model, output_dir=args.output)
    
    # Process input
    input_path = Path(args.input)
    if input_path.is_file():
        transcriber.transcribe_file(str(input_path))
    elif input_path.is_dir():
        transcribed_files = transcriber.transcribe_directory(str(input_path))
        if transcribed_files:
            logger.info("\nSuccessfully transcribed files:")
            for file in transcribed_files:
                logger.info(f"- {file}")
    else:
        logger.error(f"Error: {args.input} is not a valid file or directory")

if __name__ == "__main__":
    main()
