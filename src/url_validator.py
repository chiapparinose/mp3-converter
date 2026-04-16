"""URL validation component for YouTube URLs."""

import re
import time
from typing import Optional
from .models import ValidationResult, VideoMetadata


class URLValidator:
    """Validates YouTube URLs and checks video accessibility."""
    
    # Regex patterns for different YouTube URL formats
    # Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
    WATCH_PATTERN = r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]{11}(&.*)?$'
    
    # Short URL: https://youtu.be/VIDEO_ID
    SHORT_PATTERN = r'^https?://youtu\.be/[\w-]{11}(\?.*)?$'
    
    # Embed URL: https://www.youtube.com/embed/VIDEO_ID
    EMBED_PATTERN = r'^https?://(www\.)?youtube\.com/embed/[\w-]{11}(\?.*)?$'
    
    # Mobile URL: https://m.youtube.com/watch?v=VIDEO_ID
    MOBILE_PATTERN = r'^https?://m\.youtube\.com/watch\?v=[\w-]{11}(&.*)?$'
    
    # Shorts URL: https://www.youtube.com/shorts/VIDEO_ID
    SHORTS_PATTERN = r'^https?://(www\.)?youtube\.com/shorts/[\w-]{11}(\?.*)?$'
    
    # Timeout for validation operations (2 seconds as per requirements)
    VALIDATION_TIMEOUT = 2.0
    
    def validate_format(self, url: str) -> ValidationResult:
        """
        Validate YouTube URL format with 2-second timeout enforcement.
        
        Supports the following URL formats:
        - Standard watch: https://www.youtube.com/watch?v=VIDEO_ID
        - Short: https://youtu.be/VIDEO_ID
        - Embed: https://www.youtube.com/embed/VIDEO_ID
        - Mobile: https://m.youtube.com/watch?v=VIDEO_ID
        - Shorts: https://www.youtube.com/shorts/VIDEO_ID
        
        Args:
            url: The URL to validate
            
        Returns:
            ValidationResult with validation status and timing information
        """
        start_time = time.time()
        
        try:
            # Check if validation exceeds timeout
            if time.time() - start_time > self.VALIDATION_TIMEOUT:
                return ValidationResult(
                    is_valid=False,
                    video_metadata=None,
                    error_message="Validation timeout exceeded",
                    validation_time=time.time() - start_time
                )
            
            # Validate URL is a string
            if not isinstance(url, str):
                return ValidationResult(
                    is_valid=False,
                    video_metadata=None,
                    error_message="Invalid URL format: URL must be a string",
                    validation_time=time.time() - start_time
                )
            
            # Check if URL is empty
            if not url or not url.strip():
                return ValidationResult(
                    is_valid=False,
                    video_metadata=None,
                    error_message="Invalid URL format: URL cannot be empty",
                    validation_time=time.time() - start_time
                )
            
            # Check against all supported patterns
            patterns = [
                self.WATCH_PATTERN,
                self.SHORT_PATTERN,
                self.EMBED_PATTERN,
                self.MOBILE_PATTERN,
                self.SHORTS_PATTERN
            ]
            
            is_valid = any(re.match(pattern, url) for pattern in patterns)
            
            validation_time = time.time() - start_time
            
            # Ensure we don't exceed timeout
            if validation_time > self.VALIDATION_TIMEOUT:
                return ValidationResult(
                    is_valid=False,
                    video_metadata=None,
                    error_message="Validation timeout exceeded",
                    validation_time=validation_time
                )
            
            if is_valid:
                return ValidationResult(
                    is_valid=True,
                    video_metadata=None,  # Metadata extraction happens in get_video_info()
                    error_message=None,
                    validation_time=validation_time
                )
            else:
                return ValidationResult(
                    is_valid=False,
                    video_metadata=None,
                    error_message="Invalid URL format: URL does not match any supported YouTube URL pattern",
                    validation_time=validation_time
                )
                
        except Exception as e:
            validation_time = time.time() - start_time
            return ValidationResult(
                is_valid=False,
                video_metadata=None,
                error_message=f"Validation error: {str(e)}",
                validation_time=validation_time
            )
    
    def check_video_exists(self, url: str) -> str:
        """
        Check if video exists and is accessible using yt-dlp.
        
        Distinguishes between different types of video accessibility:
        - "available": Video exists and is accessible
        - "not_found": Video does not exist
        - "private": Video is private
        - "age_restricted": Video is age-restricted
        
        Args:
            url: The YouTube URL to check
            
        Returns:
            String indicating video accessibility status
        """
        try:
            import yt_dlp
            
            # Configure yt-dlp to extract info without downloading
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    
                    # If we got info, video is available
                    if info:
                        # Check for age restriction
                        if info.get('age_limit', 0) > 0:
                            return "age_restricted"
                        return "available"
                    else:
                        return "not_found"
                        
                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e).lower()
                    
                    # Check for specific error types
                    if 'private video' in error_msg or 'this video is private' in error_msg:
                        return "private"
                    elif 'video unavailable' in error_msg or 'video not available' in error_msg:
                        return "not_found"
                    elif 'age' in error_msg and 'restrict' in error_msg:
                        return "age_restricted"
                    else:
                        # Default to not found for other download errors
                        return "not_found"
                        
        except ImportError:
            raise ImportError("yt-dlp is required but not installed")
        except Exception as e:
            # For unexpected errors, return not_found
            return "not_found"
    
    def get_video_info(self, url: str) -> Optional[VideoMetadata]:
        """
        Extract video metadata from URL using yt-dlp.
        
        Args:
            url: The YouTube URL
            
        Returns:
            VideoMetadata if successful, None otherwise
        """
        try:
            import yt_dlp
            
            # Configure yt-dlp to extract info without downloading
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    
                    if not info:
                        return None
                    
                    # Extract metadata from yt-dlp info dict
                    video_id = info.get('id', '')
                    title = info.get('title', 'Unknown Title')
                    channel = info.get('uploader', info.get('channel', 'Unknown Channel'))
                    duration = info.get('duration', 0)
                    
                    # Get thumbnail URL (prefer maxresdefault, fallback to default)
                    thumbnail_url = ''
                    if 'thumbnails' in info and info['thumbnails']:
                        # Get the highest quality thumbnail
                        thumbnail_url = info['thumbnails'][-1].get('url', '')
                    elif 'thumbnail' in info:
                        thumbnail_url = info.get('thumbnail', '')
                    
                    # Optional fields
                    upload_date = info.get('upload_date')
                    description = info.get('description')
                    
                    return VideoMetadata(
                        video_id=video_id,
                        title=title,
                        channel=channel,
                        duration=duration,
                        thumbnail_url=thumbnail_url,
                        upload_date=upload_date,
                        description=description
                    )
                    
                except yt_dlp.utils.DownloadError:
                    # Video not accessible
                    return None
                    
        except ImportError:
            raise ImportError("yt-dlp is required but not installed")
        except Exception:
            # For unexpected errors, return None
            return None
