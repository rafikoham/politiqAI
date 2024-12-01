import yt_dlp
import os
from pathlib import Path
from typing import Optional, List, Dict
from tqdm import tqdm

class YouTubeDownloader:
    def __init__(self, output_dir: str = "data/videos"):
        """Initialize YouTube downloader with output directory"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nVideos will be saved to: {self.output_dir.absolute()}")

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
            }

            print(f"\nDownloading: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                for file in self.output_dir.glob(f"{filename or video_title}.*"):
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
            # Configure yt-dlp for search
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for videos
                search_query = f"ytsearch{max_results}:{query}"
                results = ydl.extract_info(search_query, download=False)
                entries = results.get('entries', [])
                
                print(f"\nFound {len(entries)} videos matching search: '{query}'")
                for entry in tqdm(entries, desc="Downloading videos"):
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    file_path = self.download_video(video_url)
                    if file_path:
                        downloaded_files.append(file_path)
                        
        except Exception as e:
            print(f"Error searching for '{query}': {str(e)}")
            
        return downloaded_files

    @staticmethod
    def _progress_hook(d: Dict):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                percentage = (downloaded_bytes / total_bytes) * 100
                print(f"\rProgress: {percentage:.1f}%", end='')

def main():
    # Initialize downloader with explicit output directory
    downloader = YouTubeDownloader("data/videos")
    print("\nSearching for French political interviews...")
    
    # Search and download French political interviews
    query = "interview politique france 2023"
    downloaded_files = downloader.search_and_download(query, max_results=5)
    
    if downloaded_files:
        print("\nSuccessfully downloaded videos:")
        for file in downloaded_files:
            print(f"- {file}")
    else:
        print("\nNo videos were downloaded. Please check for errors above.")

if __name__ == "__main__":
    main()
