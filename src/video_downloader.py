"""Video download component using yt-dlp."""

import time
import logging
import random
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from .models import DownloadResult, VideoMetadata


# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
]


class VideoDownloader:
    """Downloads YouTube videos and extracts audio streams with rate limiting bypass."""
    
    def __init__(
        self, 
        temp_dir: str = "temp",
        use_cookies: bool = True,
        cookies_browser: Optional[str] = None,
        cookies_file: Optional[str] = None,
        rotate_user_agent: bool = True
    ):
        """
        Initialize VideoDownloader with rate limiting bypass options.
        
        Args:
            temp_dir: Directory for temporary downloads
            use_cookies: Enable browser cookies (recommended for higher limits)
            cookies_browser: Browser to extract cookies from ('chrome', 'firefox', 'edge', etc.)
            cookies_file: Path to cookies.txt file (alternative to browser extraction)
            rotate_user_agent: Enable user agent rotation
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self._download_progress = 0.0
        self._cancelled = False
        self._retry_count = 0
        self._duration_warning_issued = False
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting bypass options
        self.use_cookies = use_cookies
        self.cookies_browser = cookies_browser or 'chrome'  # Default to Chrome
        self.cookies_file = cookies_file
        self.rotate_user_agent = rotate_user_agent
    
    def _get_ydl_opts(self, progress_hook: Callable) -> Dict[str, Any]:
        """
        Get yt-dlp options with rate limiting bypass features.
        
        Args:
            progress_hook: Progress callback function
            
        Returns:
            Dictionary of yt-dlp options
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.temp_dir / '%(id)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'retries': 3,
            'fragment_retries': 3,
            'quiet': True,
            'no_warnings': True,
        }
        
        # Add browser cookies for higher rate limits (BEST method)
        if self.use_cookies:
            if self.cookies_file:
                ydl_opts['cookiefile'] = self.cookies_file
                self.logger.info(f"Using cookies from file: {self.cookies_file}")
            else:
                try:
                    ydl_opts['cookiesfrombrowser'] = (self.cookies_browser,)
                    self.logger.info(f"Using cookies from browser: {self.cookies_browser}")
                except Exception as e:
                    self.logger.warning(f"Failed to load cookies from browser: {e}")
        
        # Add user agent rotation
        if self.rotate_user_agent:
            user_agent = random.choice(USER_AGENTS)
            ydl_opts['user_agent'] = user_agent
            self.logger.debug(f"Using user agent: {user_agent[:50]}...")
        
        return ydl_opts
    
    def download_audio(
        self, 
        url: str, 
        output_path: str, 
        progress_callback: Optional[Callable[[float], None]] = None,
        warning_callback: Optional[Callable[[str], None]] = None
    ) -> DownloadResult:
        """
        Download audio from YouTube video with retry logic, duration warnings, and rate limiting bypass.
        
        Args:
            url: YouTube video URL
            output_path: Path for output file
            progress_callback: Optional callback for progress updates (0.0 to 1.0)
            warning_callback: Optional callback for warnings (e.g., long duration)
            
        Returns:
            DownloadResult with download information
        """
        start_time = time.time()
        self._cancelled = False
        self._download_progress = 0.0
        self._duration_warning_issued = False
        
        try:
            import yt_dlp
            
            def progress_hook(d: Dict[str, Any]) -> None:
                """Hook for yt-dlp progress updates."""
                if self._cancelled:
                    raise Exception("Download cancelled")
                
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0:
                        self._download_progress = downloaded / total
                        if progress_callback:
                            progress_callback(self._download_progress)
                elif d['status'] == 'finished':
                    self._download_progress = 1.0
                    if progress_callback:
                        progress_callback(1.0)
            
            # Retry logic with exponential backoff: up to 5 attempts
            max_retries = 5
            last_error = None
            
            for attempt in range(max_retries):
                self._retry_count = attempt
                try:
                    # Get yt-dlp options with rate limiting bypass
                    ydl_opts = self._get_ydl_opts(progress_hook)
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # First, get video info to check duration
                        info = ydl.extract_info(url, download=False)
                        
                        # Check duration and issue warning if exceeds 2 hours (7200 seconds)
                        duration = info.get('duration', 0)
                        if duration > 7200 and not self._duration_warning_issued and warning_callback:
                            warning_callback(
                                f"Warning: Video duration is {duration // 60} minutes "
                                f"({duration // 3600}h {(duration % 3600) // 60}m). "
                                f"This may take a while to download and convert."
                            )
                            self._duration_warning_issued = True
                            self.logger.warning(f"Long video detected: {duration} seconds")
                        
                        # Now download the video
                        info = ydl.extract_info(url, download=True)
                        
                        # Get the downloaded file
                        video_id = info['id']
                        ext = info.get('ext', 'webm')
                        downloaded_file = self.temp_dir / f"{video_id}.{ext}"
                        
                        if downloaded_file.exists():
                            file_size = downloaded_file.stat().st_size
                            download_time = time.time() - start_time
                            
                            self.logger.info(
                                f"Download successful: {downloaded_file.name} "
                                f"({file_size / (1024 * 1024):.2f} MB) "
                                f"in {download_time:.2f}s"
                            )
                            
                            return DownloadResult(
                                success=True,
                                audio_file_path=downloaded_file,
                                format=ext,
                                file_size=file_size,
                                download_time=download_time
                            )
                        else:
                            last_error = Exception("Downloaded file not found")
                            
                except Exception as e:
                    last_error = e
                    error_msg = str(e).lower()
                    
                    # Check if it's a rate limit error
                    is_rate_limit = any(keyword in error_msg for keyword in [
                        'rate limit', 'too many requests', 'bot', 'captcha', '429'
                    ])
                    
                    if is_rate_limit:
                        self.logger.warning(
                            f"Rate limit detected on attempt {attempt + 1}/{max_retries}: {str(e)}"
                        )
                    else:
                        self.logger.warning(
                            f"Download attempt {attempt + 1}/{max_retries} failed: {str(e)}"
                        )
                    
                    # Exponential backoff with jitter before retry
                    if attempt < max_retries - 1:
                        # Exponential backoff: 2^attempt + random jitter
                        base_wait = 2 ** attempt
                        jitter = random.uniform(0, 1)
                        wait_time = base_wait + jitter
                        
                        # For rate limit errors, wait longer
                        if is_rate_limit:
                            wait_time *= 2
                            self.logger.warning(
                                f"Rate limit detected. Waiting {wait_time:.1f}s before retry..."
                            )
                        else:
                            self.logger.info(f"Retrying in {wait_time:.1f} seconds...")
                        
                        time.sleep(wait_time)
            
            # All retries failed
            download_time = time.time() - start_time
            error_msg = f"Download failed after {max_retries} attempts: {str(last_error)}"
            self.logger.error(error_msg)
            
            return DownloadResult(
                success=False,
                audio_file_path=None,
                format="",
                file_size=0,
                download_time=download_time
            )
            
        except ImportError:
            self.logger.error("yt-dlp not installed")
            return DownloadResult(
                success=False,
                audio_file_path=None,
                format="",
                file_size=0,
                download_time=time.time() - start_time
            )
    
    def get_video_info(self, url: str, use_cache: bool = True) -> Optional[VideoMetadata]:
        """
        Get video information without downloading (with optional caching).
        
        Args:
            url: YouTube video URL
            use_cache: Whether to use cached metadata (not implemented yet)
            
        Returns:
            VideoMetadata or None if failed
        """
        try:
            import yt_dlp
            
            # Create minimal options for info extraction
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            # Add cookies if enabled
            if self.use_cookies:
                if self.cookies_file:
                    ydl_opts['cookiefile'] = self.cookies_file
                else:
                    try:
                        ydl_opts['cookiesfrombrowser'] = (self.cookies_browser,)
                    except Exception:
                        pass
            
            # Add user agent rotation
            if self.rotate_user_agent:
                ydl_opts['user_agent'] = random.choice(USER_AGENTS)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return VideoMetadata(
                    video_id=info.get('id', ''),
                    title=info.get('title', 'Unknown'),
                    channel=info.get('uploader', 'Unknown'),
                    duration=info.get('duration', 0),
                    thumbnail_url=info.get('thumbnail', ''),
                    upload_date=info.get('upload_date'),
                    description=info.get('description')
                )
        except Exception as e:
            self.logger.error(f"Failed to get video info: {e}")
            return None
    
    def get_progress(self) -> float:
        """
        Get current download progress.
        
        Returns:
            Progress value (0.0 to 1.0)
        """
        return self._download_progress
    
    def cancel_download(self) -> None:
        """Cancel ongoing download."""
        self._cancelled = True
    
    def get_retry_count(self) -> int:
        """Get number of retry attempts made."""
        return self._retry_count
    
    @staticmethod
    def check_duration_warning(duration_seconds: int) -> bool:
        """
        Check if duration exceeds 2 hours.
        
        Args:
            duration_seconds: Video duration in seconds
            
        Returns:
            True if duration exceeds 2 hours (7200 seconds)
        """
        return duration_seconds > 7200
