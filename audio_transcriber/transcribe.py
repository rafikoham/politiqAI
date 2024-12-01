import whisper
import os
from tqdm import tqdm
import argparse
from pathlib import Path

class AudioTranscriber:
    def __init__(self, model_size='base'):
        """Initialize with specified Whisper model size
        Available sizes: tiny, base, small, medium, large
        """
        print(f"Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size)
        print("Model loaded successfully!")

    def transcribe_file(self, audio_path, output_dir=None):
        """Transcribe a single audio file"""
        try:
            # Verify file exists and is audio
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            if not audio_path.lower().endswith(('.mp3', '.mp4', '.wav', '.m4a')):
                raise ValueError("Unsupported audio format. Use MP3, MP4, WAV, or M4A files.")

            print(f"\nTranscribing: {audio_path}")
            result = self.model.transcribe(audio_path)
            transcript = result["text"]

            if not transcript.strip():
                print("Warning: No speech detected in audio")
                return None

            # Save transcript if output directory is specified
            if output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Create output filename
                audio_filename = Path(audio_path).stem
                output_path = output_dir / f"{audio_filename}_transcript.txt"
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print(f"Transcript saved to: {output_path}")

            return transcript

        except Exception as e:
            print(f"Error processing {audio_path}: {str(e)}")
            return None

    def transcribe_directory(self, input_dir, output_dir):
        """Transcribe all audio files in a directory"""
        input_dir = Path(input_dir)
        if not input_dir.exists():
            raise FileNotFoundError(f"Directory not found: {input_dir}")

        # Get all audio files
        audio_files = []
        for ext in ['.mp3', '.mp4', '.wav', '.m4a']:
            audio_files.extend(input_dir.glob(f"*{ext}"))

        if not audio_files:
            print("No audio files found in directory")
            return

        print(f"\nFound {len(audio_files)} audio files")
        
        # Process each file
        for audio_file in tqdm(audio_files, desc="Transcribing files"):
            self.transcribe_file(str(audio_file), output_dir)

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio files using Whisper')
    parser.add_argument('input', help='Input audio file or directory')
    parser.add_argument('--output', help='Output directory for transcripts', default='transcripts')
    parser.add_argument('--model', help='Whisper model size (tiny, base, small, medium, large)', default='base')
    
    args = parser.parse_args()
    
    # Initialize transcriber
    transcriber = AudioTranscriber(model_size=args.model)
    
    # Process input
    input_path = Path(args.input)
    if input_path.is_file():
        transcriber.transcribe_file(str(input_path), args.output)
    elif input_path.is_dir():
        transcriber.transcribe_directory(str(input_path), args.output)
    else:
        print(f"Error: {args.input} is not a valid file or directory")

if __name__ == "__main__":
    main()
