"""
Smart Video Downloader with Hybrid Proxy Strategy
Uses proxy only for metadata (rate-limited), direct connection for download (not rate-limited)
This saves 90%+ proxy bandwidth!
"""

import time
import logging
import random
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from .models import DownloadResult, VideoMetadata
from .video_downloader import VideoDownloader, USER_AGENTS


class SmartDownloader:
    """
    Smart downloader that uses proxy only for metadata extraction.
    Downloads video directly without proxy to save bandwidth.
    
    Bandwidth Savings:
    - Metadata via proxy: ~10-50 KB per video
    - Download direct: ~5-50 MB per video (NOT using proxy)
    - Savings: 90-99% proxy bandwidth!
    
    Example:
        100 videos with proxy for everything: ~1 GB proxy bandwidth
        100 videos with smart mode: ~5 MB proxy bandwidth (200x less!)
    """
    
    def __init__(
        self,
        temp_dir: str = "temp",
        proxy: Optional[str] = None,
        use_cookies: bool = False,
        cookies_browser: Optional[str] = None,
        rotate_user_agent: bool = True
    ):
        """
        Initialize SmartDownloader.
        
        Args:
            temp_dir: Directory for temporary downloads
            proxy: Proxy URL (used ONLY for metadata, not for download)
            use_cookies: Enable browser cookies
            cookies_browser: Browser to extract cookies from
            rotate_user_agent: Enable user agent rotation
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Downloader with proxy (for metadata only)
        self.metadata_downloader = VideoDownloader(
            temp_dir=temp_dir,
            use_cookies=use_cookies,
            cookies_browser=cookies_browser,
            rotate_user_agent=rotate_user_agent,
            proxy=proxy  # Proxy for metadata
        )
        
        # Downloader without proxy (for actual download)
        self.download_downloader = VideoDownloader(
            temp_dir=temp_dir,
            use_cookies=use_cookies,
            cookies_browser=cookies_browser,
            rotate_user_agent=rotate_user_agent,
            proxy=None  # NO proxy for download
        )
        
        self.proxy = proxy
        self._download_progress = 0.0
        self._cancelled = False
    
    def get_video_info(self, url: str) -> Optional[VideoMetadata]:
        """
        Get video metadata using proxy (to bypass rate limiting).
        
        This uses minimal bandwidth (~10-50 KB) via proxy.
        
        Args:
            url: YouTube video URL
            
        Returns:
            VideoMetadata or None if failed
        """
        self.logger.info(f"Getting metadata via proxy: {url}")
        return self.metadata_downloader.get_video_info(url)
    
    def download_audio(
        self,
        url: str,
        output_path: str,
        progress_callback: Optional[Callable[[float], None]] = None,
        warning_callback: Optional[Callable[[str], None]] = None
    ) -> DownloadResult:
        """
        Download audio WITHOUT proxy (direct connection).
        
        This saves proxy bandwidth since video download is NOT rate-limited,
        only metadata extraction is rate-limited.
        
        Strategy:
        1. Get metadata via proxy (bypass rate limit) - ~10-50 KB
        2. Download video direct (no rate limit) - ~5-50 MB
        3. Save 90%+ proxy bandwidth!
        
        Args:
            url: YouTube video URL
            output_path: Path for output file
            progress_callback: Optional callback for progress updates
            warning_callback: Optional callback for warnings
            
        Returns:
            DownloadResult with download information
        """
        self.logger.info(f"Downloading audio direct (no proxy): {url}")
        
        # Download without proxy (saves bandwidth!)
        result = self.download_downloader.download_audio(
            url=url,
            output_path=output_path,
            progress_callback=progress_callback,
            warning_callback=warning_callback
        )
        
        return result
    
    def get_progress(self) -> float:
        """Get current download progress."""
        return self.download_downloader.get_progress()
    
    def cancel_download(self) -> None:
        """Cancel ongoing download."""
        self.metadata_downloader.cancel_download()
        self.download_downloader.cancel_download()
    
    def get_bandwidth_stats(self, num_videos: int, avg_video_size_mb: float = 10) -> Dict[str, Any]:
        """
        Calculate bandwidth usage comparison.
        
        Args:
            num_videos: Number of videos to convert
            avg_video_size_mb: Average video size in MB
            
        Returns:
            Dictionary with bandwidth statistics
        """
        # Metadata size per video
        metadata_size_mb = 0.05  # ~50 KB
        
        # Full proxy mode (proxy for everything)
        full_proxy_bandwidth = num_videos * (metadata_size_mb + avg_video_size_mb)
        
        # Smart mode (proxy only for metadata)
        smart_proxy_bandwidth = num_videos * metadata_size_mb
        
        # Savings
        savings_mb = full_proxy_bandwidth - smart_proxy_bandwidth
        savings_percent = (savings_mb / full_proxy_bandwidth) * 100
        
        return {
            'num_videos': num_videos,
            'avg_video_size_mb': avg_video_size_mb,
            'full_proxy_bandwidth_mb': full_proxy_bandwidth,
            'smart_proxy_bandwidth_mb': smart_proxy_bandwidth,
            'savings_mb': savings_mb,
            'savings_percent': savings_percent,
            'full_proxy_cost_usd': full_proxy_bandwidth / 1024 * 1.75,  # $1.75/GB
            'smart_proxy_cost_usd': smart_proxy_bandwidth / 1024 * 1.75,
            'cost_savings_usd': savings_mb / 1024 * 1.75
        }
    
    def print_bandwidth_comparison(self, num_videos: int = 100):
        """
        Print bandwidth usage comparison.
        
        Args:
            num_videos: Number of videos to compare
        """
        stats = self.get_bandwidth_stats(num_videos)
        
        print("\n" + "="*70)
        print("BANDWIDTH USAGE COMPARISON")
        print("="*70)
        print(f"\nVideos: {stats['num_videos']}")
        print(f"Avg video size: {stats['avg_video_size_mb']:.1f} MB")
        print()
        print("Full Proxy Mode (proxy for everything):")
        print(f"  Bandwidth: {stats['full_proxy_bandwidth_mb']:.1f} MB ({stats['full_proxy_bandwidth_mb']/1024:.2f} GB)")
        print(f"  Cost: ${stats['full_proxy_cost_usd']:.2f}")
        print()
        print("Smart Mode (proxy only for metadata):")
        print(f"  Bandwidth: {stats['smart_proxy_bandwidth_mb']:.1f} MB ({stats['smart_proxy_bandwidth_mb']/1024:.2f} GB)")
        print(f"  Cost: ${stats['smart_proxy_cost_usd']:.2f}")
        print()
        print("Savings:")
        print(f"  Bandwidth: {stats['savings_mb']:.1f} MB ({stats['savings_mb']/1024:.2f} GB)")
        print(f"  Percentage: {stats['savings_percent']:.1f}%")
        print(f"  Cost: ${stats['cost_savings_usd']:.2f}")
        print("="*70 + "\n")


# Convenience function
def create_smart_downloader(proxy: str, **kwargs) -> SmartDownloader:
    """
    Create SmartDownloader with proxy.
    
    Args:
        proxy: Proxy URL (used only for metadata)
        **kwargs: Additional arguments for SmartDownloader
        
    Returns:
        SmartDownloader instance
    """
    return SmartDownloader(proxy=proxy, **kwargs)
