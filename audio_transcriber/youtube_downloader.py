import yt_dlp
import os
import json
from pathlib import Path
from typing import Optional, List

class YouTubeDownloader:
    def __init__(self, output_dir: str = "data/videos", min_duration_minutes: float = 10.0):
        """Initialize YouTube downloader with output directory and minimum duration"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.min_duration_seconds = min_duration_minutes * 60

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

                    # Save metadata to JSON
                    metadata = {
                        'title': info.get('title', 'Unknown Title'),
                        'uploader': info.get('uploader', 'Unknown Uploader'),
                        'upload_date': info.get('upload_date', 'Unknown Date'),
                        'duration': duration,
                        'url': url
                    }
                    json_path = self.output_dir / f"{filename or info['title']}.json"
                    with open(json_path, 'w', encoding='utf-8') as json_file:
                        json.dump(metadata, json_file, ensure_ascii=False, indent=4)
                    print(f"Metadata saved to: {json_path}")

                    return str(file)

        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return None

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
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                    file_path = self.download_video(video_url)
                    if file_path:
                        downloaded_files.append(file_path)

        except Exception as e:
            print(f"Error searching for videos: {str(e)}")

        return downloaded_files


def main():
    # Initialize downloader
    downloader = YouTubeDownloader(min_duration_minutes=10.0)
    
    # Search and download French political interviews
    query = "Mathilde Panot interview politique France -live -direct"
    print(f"\nSearching for: {query}")
    downloaded_files = downloader.search_and_download(query, max_results=10)
    
    if downloaded_files:
        print("\nDownloaded files:")
        for file in downloaded_files:
            print(f"- {file}")
    else:
        print("\nNo videos were downloaded. Please check for errors above.")


if __name__ == "__main__":
    main()
