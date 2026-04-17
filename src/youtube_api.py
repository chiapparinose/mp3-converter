"""
YouTube Data API v3 wrapper for metadata extraction
FREE: 10,000 quota/day (1 video = 1 quota)
NO rate limiting for metadata!
"""

import re
import logging
from typing import Optional
from .models import VideoMetadata


class YouTubeAPI:
    """YouTube Data API v3 client for metadata extraction."""
    
    def __init__(self, api_key: str):
        """
        Initialize YouTube API client.
        
        Args:
            api_key: YouTube Data API v3 key
        """
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_info(self, url: str) -> Optional[VideoMetadata]:
        """
        Get video metadata using YouTube Data API.
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoMetadata or None if failed
        """
        try:
            import requests
            
            # Extract video ID
            video_id = self.extract_video_id(url)
            if not video_id:
                self.logger.error(f"Could not extract video ID from URL: {url}")
                return None
            
            # API request
            api_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet,contentDetails',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('items'):
                self.logger.error(f"Video not found: {video_id}")
                return None
            
            item = data['items'][0]
            snippet = item['snippet']
            content_details = item['contentDetails']
            
            # Parse duration (ISO 8601: PT1H2M3S)
            duration = self._parse_duration(content_details['duration'])
            
            # Get best thumbnail
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_url = (
                thumbnails.get('maxres', {}).get('url') or
                thumbnails.get('high', {}).get('url') or
                thumbnails.get('medium', {}).get('url') or
                thumbnails.get('default', {}).get('url') or
                ''
            )
            
            return VideoMetadata(
                video_id=video_id,
                title=snippet['title'],
                channel=snippet['channelTitle'],
                duration=duration,
                thumbnail_url=thumbnail_url,
                upload_date=snippet['publishedAt'][:10].replace('-', ''),
                description=snippet.get('description', '')
            )
        
        except Exception as e:
            self.logger.error(f"API error: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> int:
        """
        Parse ISO 8601 duration to seconds.
        
        Args:
            duration_str: ISO 8601 duration (e.g., PT1H2M3S)
            
        Returns:
            Duration in seconds
        """
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
