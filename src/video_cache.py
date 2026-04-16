"""Video metadata caching system to reduce API requests."""

import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class VideoCache:
    """Cache for video metadata to reduce YouTube API requests."""
    
    def __init__(
        self, 
        cache_file: str = 'video_cache.json',
        cache_ttl: int = 604800,  # 7 days in seconds
        max_cache_size: int = 1000
    ):
        """
        Initialize video cache.
        
        Args:
            cache_file: Path to cache file
            cache_ttl: Time-to-live for cache entries in seconds (default: 7 days)
            max_cache_size: Maximum number of entries to keep
        """
        self.cache_file = Path(cache_file)
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        self.logger = logging.getLogger(__name__)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    self.logger.info(f"Loaded {len(cache)} entries from cache")
                    return cache
            except Exception as e:
                self.logger.warning(f"Failed to load cache: {e}")
                return {}
        return {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        try:
            # Clean expired entries before saving
            self._clean_expired()
            
            # Limit cache size
            if len(self.cache) > self.max_cache_size:
                self._trim_cache()
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Saved {len(self.cache)} entries to cache")
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")
    
    def _clean_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = []
        
        for video_id, entry in self.cache.items():
            cached_time = entry.get('cached_at', 0)
            if current_time - cached_time > self.cache_ttl:
                expired_keys.append(video_id)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.info(f"Removed {len(expired_keys)} expired entries")
    
    def _trim_cache(self) -> None:
        """Trim cache to max size by removing oldest entries."""
        if len(self.cache) <= self.max_cache_size:
            return
        
        # Sort by cached_at timestamp
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].get('cached_at', 0)
        )
        
        # Keep only the most recent entries
        entries_to_keep = sorted_entries[-self.max_cache_size:]
        self.cache = dict(entries_to_keep)
        
        removed_count = len(sorted_entries) - len(entries_to_keep)
        self.logger.info(f"Trimmed cache: removed {removed_count} oldest entries")
    
    def get(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached metadata for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Cached metadata dict or None if not found/expired
        """
        if video_id not in self.cache:
            return None
        
        entry = self.cache[video_id]
        cached_time = entry.get('cached_at', 0)
        current_time = time.time()
        
        # Check if expired
        if current_time - cached_time > self.cache_ttl:
            self.logger.debug(f"Cache expired for video {video_id}")
            del self.cache[video_id]
            return None
        
        self.logger.debug(f"Cache hit for video {video_id}")
        return entry.get('metadata')
    
    def set(self, video_id: str, metadata: Dict[str, Any]) -> None:
        """
        Cache metadata for a video.
        
        Args:
            video_id: YouTube video ID
            metadata: Video metadata to cache
        """
        self.cache[video_id] = {
            'metadata': metadata,
            'cached_at': time.time()
        }
        self._save_cache()
        self.logger.debug(f"Cached metadata for video {video_id}")
    
    def has(self, video_id: str) -> bool:
        """
        Check if video is in cache and not expired.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if video is cached and not expired
        """
        return self.get(video_id) is not None
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache = {}
        self._save_cache()
        self.logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not self.cache:
            return {
                'total_entries': 0,
                'cache_size_bytes': 0,
                'oldest_entry': None,
                'newest_entry': None
            }
        
        timestamps = [entry.get('cached_at', 0) for entry in self.cache.values()]
        oldest = min(timestamps)
        newest = max(timestamps)
        
        cache_size = 0
        if self.cache_file.exists():
            cache_size = self.cache_file.stat().st_size
        
        return {
            'total_entries': len(self.cache),
            'cache_size_bytes': cache_size,
            'cache_size_mb': cache_size / (1024 * 1024),
            'oldest_entry': datetime.fromtimestamp(oldest).isoformat() if oldest else None,
            'newest_entry': datetime.fromtimestamp(newest).isoformat() if newest else None,
            'ttl_days': self.cache_ttl / 86400
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or None if not found
        """
        import re
        
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
