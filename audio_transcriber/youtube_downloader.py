import yt_dlp
import os
from pathlib import Path
from typing import Optional, List, Dict
from tqdm import tqdm

class YouTubeDownloader:
    def __init__(self, output_dir: str = "data/videos", min_duration_minutes: float = 3.0):
        """Initialize YouTube downloader with output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_duration_seconds = min_duration_minutes * 60
        print(f"\nVideos will be saved to: {self.output_dir.absolute()}")
        print(f"Minimum video duration: {min_duration_minutes} minutes")

    def download_video(self, url: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Download a single video from YouTube
        Args:
            url: YouTube video URL
            filename: Optional custom filename (without extension)
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/best[ext=mp4]/best',  # Prefer m4a audio, fallback to mp4
                'outtmpl': str(self.output_dir / (filename or '%(title)s')) + '.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._progress_hook],
                # Skip live streams
                'skip_download': False,
                'playlistrandom': False,
                'extract_flat': False,
            }

            # First check if it's a live video or too short
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info.get('is_live', False):
                    print(f"Skipping live video: {info.get('title', url)}")
                    return None
                
                duration = info.get('duration', 0)
                if duration < self.min_duration_seconds:
                    print(f"Skipping video '{info.get('title', url)}': Duration ({duration}s) is less than minimum required ({self.min_duration_seconds}s)")
                    return None
                
                # Download only if it meets the criteria
                print(f"\nDownloading: {info.get('title', url)} (Duration: {duration/60:.1f} minutes)")
                ydl.download([url])
                
                # Find the downloaded file
                for file in self.output_dir.glob(f"{filename or info['title']}.*"):
                    print(f"\nDownloaded to: {file}")
                    return str(file)

        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return None

    def download_playlist(self, url: str) -> List[str]:
        """
        Download all videos from a YouTube playlist
        Args:
            url: YouTube playlist URL
        Returns:
            List of paths to downloaded files
        """
        downloaded_files = []
        try:
            # First get playlist info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(url, download=False)
                entries = playlist_info.get('entries', [])
                
                print(f"\nFound {len(entries)} videos in playlist")
                for entry in tqdm(entries, desc="Downloading playlist"):
                    video_url = entry.get('url')
                    if video_url:
                        file_path = self.download_video(f"https://www.youtube.com/watch?v={video_url}")
                        if file_path:
                            downloaded_files.append(file_path)
                            
        except Exception as e:
            print(f"Error processing playlist {url}: {str(e)}")
            
        return downloaded_files

    def search_and_download(self, query: str, max_results: int = 5) -> List[str]:
        """
        Search YouTube for videos and download them
        Args:
            query: Search query
            max_results: Maximum number of videos to download
        Returns:
            List of paths to downloaded files
        """
        downloaded_files = []
        try:
            # Configure yt-dlp options for search
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch',
                'max_downloads': max_results
            }
            
            # First search for videos
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
                entries = search_results.get('entries', [])
                
                print(f"\nFound {len(entries)} videos matching search")
                for entry in entries:
                    video_url = entry.get('url')
                    if video_url:
                        file_path = self.download_video(f"https://www.youtube.com/watch?v={video_url}")
                        if file_path:
                            downloaded_files.append(file_path)
                            
        except Exception as e:
            print(f"Error searching for {query}: {str(e)}")
            
        return downloaded_files

    def _progress_hook(self, d: Dict):
        """Progress hook for yt-dlp to show download progress"""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                progress = (downloaded_bytes / total_bytes) * 100
                print(f"\rDownload progress: {progress:.1f}%", end='')

class AudioTranscriber:
    def transcribe_file(self, file_path: str):
        # TO DO: implement transcription logic here
        print(f"Transcribing file: {file_path}")

def main():
    # Initialize downloader and transcriber
    downloader = YouTubeDownloader(min_duration_minutes=3.0)
    transcriber = AudioTranscriber()
    
    # Search and download French political interviews
    query = "interview politique france macron assemblée nationale -live -direct site:youtube.com"
    print(f"\nSearching for: {query}")
    downloaded_files = downloader.search_and_download(query, max_results=3)
    
    if downloaded_files:
        print("\nSuccessfully downloaded videos:")
        for file in downloaded_files:
            print(f"- {file}")
            
        # Transcribe downloaded videos
        print("\nTranscribing downloaded videos...")
        for video_file in downloaded_files:
            transcriber.transcribe_file(video_file)
    else:
        print("\nNo videos were downloaded. Please check for errors above.")

if __name__ == "__main__":
    main()
