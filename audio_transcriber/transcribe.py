import whisper
import os
from tqdm import tqdm
import argparse
from pathlib import Path

class AudioTranscriber:
    def __init__(self, model_size='base', output_dir='data/transcripts'):
        """Initialize with specified Whisper model size and output directory
        Available sizes: tiny, base, small, medium, large
        """
        print(f"Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print("Model loaded successfully!")

    def transcribe_file(self, audio_path):
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

            # Create output filename based on the video name
            audio_filename = Path(audio_path).stem
            output_path = self.output_dir / f"{audio_filename}.txt"
            
            # Save transcript
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"Transcript saved to: {output_path}")

            return str(output_path)

        except Exception as e:
            print(f"Error processing {audio_path}: {str(e)}")
            return None

    def transcribe_directory(self, input_dir):
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
            return []

        print(f"\nFound {len(audio_files)} audio files")
        
        # Process each file
        transcribed_files = []
        for audio_file in tqdm(audio_files, desc="Transcribing files"):
            transcript_path = self.transcribe_file(str(audio_file))
            if transcript_path:
                transcribed_files.append(transcript_path)
        
        return transcribed_files

def main():
    parser = argparse.ArgumentParser(description='Transcribe audio files using Whisper')
    parser.add_argument('input', help='Input audio file or directory')
    parser.add_argument('--model', help='Whisper model size (tiny, base, small, medium, large)', default='base')
    parser.add_argument('--output', help='Output directory for transcripts', default='data/transcripts')
    
    args = parser.parse_args()
    
    # Initialize transcriber
    transcriber = AudioTranscriber(model_size=args.model, output_dir=args.output)
    
    # Process input
    input_path = Path(args.input)
    if input_path.is_file():
        transcriber.transcribe_file(str(input_path))
    elif input_path.is_dir():
        transcribed_files = transcriber.transcribe_directory(str(input_path))
        if transcribed_files:
            print("\nSuccessfully transcribed files:")
            for file in transcribed_files:
                print(f"- {file}")
    else:
        print(f"Error: {args.input} is not a valid file or directory")

if __name__ == "__main__":
    main()
