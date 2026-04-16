"""Metadata embedding component using mutagen."""

import logging
import urllib.request
import urllib.error
from typing import Optional
from pathlib import Path
from .models import VideoMetadata


class MetadataEmbedder:
    """Embeds video metadata into MP3 ID3 tags."""
    
    def __init__(self):
        """Initialize MetadataEmbedder."""
        self.logger = logging.getLogger(__name__)
    
    def embed_metadata(self, mp3_path: str, metadata: VideoMetadata) -> bool:
        """
        Embed metadata into MP3 file.
        
        Args:
            mp3_path: Path to MP3 file
            metadata: Video metadata to embed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3, TIT2, TPE1, TLEN, APIC, ID3NoHeaderError
            
            mp3_file = Path(mp3_path)
            if not mp3_file.exists():
                self.logger.error(f"MP3 file not found: {mp3_path}")
                return False
            
            # Load or create ID3 tags
            try:
                audio = MP3(mp3_path, ID3=ID3)
            except ID3NoHeaderError:
                audio = MP3(mp3_path)
                audio.add_tags()
            
            # Embed title (TIT2)
            if metadata.title:
                title = self._sanitize_string(metadata.title)
                audio.tags.add(TIT2(encoding=3, text=title))
            
            # Embed artist/channel (TPE1)
            if metadata.channel:
                channel = self._sanitize_string(metadata.channel)
                audio.tags.add(TPE1(encoding=3, text=channel))
            
            # Embed duration (TLEN)
            if metadata.duration:
                duration_ms = str(metadata.duration * 1000)
                audio.tags.add(TLEN(encoding=3, text=duration_ms))
            
            # Try to embed thumbnail
            if metadata.thumbnail_url:
                image_data = self.download_thumbnail(metadata.thumbnail_url)
                if image_data:
                    self.embed_artwork(mp3_path, image_data, audio)
            
            audio.save()
            self.logger.info(f"Metadata embedded successfully: {mp3_path}")
            return True
            
        except ImportError:
            self.logger.warning("mutagen not installed, skipping metadata embedding")
            return False
        except Exception as e:
            self.logger.error(f"Failed to embed metadata: {e}")
            return False
    
    def download_thumbnail(self, thumbnail_url: str) -> Optional[bytes]:
        """
        Download thumbnail image.
        
        Args:
            thumbnail_url: URL of thumbnail image
            
        Returns:
            Image data as bytes or None if download fails
        """
        try:
            request = urllib.request.Request(
                thumbnail_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.read()
        except urllib.error.URLError as e:
            self.logger.warning(f"Failed to download thumbnail: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Thumbnail download error: {e}")
            return None
    
    def embed_artwork(self, mp3_path: str, image_data: bytes, audio=None) -> bool:
        """
        Embed artwork into MP3 file.
        
        Args:
            mp3_path: Path to MP3 file
            image_data: Image data as bytes
            audio: Optional pre-loaded MP3 object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3, APIC, ID3NoHeaderError
            
            if audio is None:
                try:
                    audio = MP3(mp3_path, ID3=ID3)
                except ID3NoHeaderError:
                    audio = MP3(mp3_path)
                    audio.add_tags()
            
            # Determine image type
            mime_type = 'image/jpeg'
            if image_data[:8] == b'\x89PNG\r\n\x1a\n':
                mime_type = 'image/png'
            
            audio.tags.add(APIC(
                encoding=3,
                mime=mime_type,
                type=3,  # Cover (front)
                desc='Cover',
                data=image_data
            ))
            
            if audio is None:
                audio.save()
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to embed artwork: {e}")
            return False
    
    @staticmethod
    def _sanitize_string(text: str) -> str:
        """
        Sanitize string for ID3 compatibility.
        
        Args:
            text: Input text
            
        Returns:
            Sanitized text
        """
        # Remove null bytes and other problematic characters
        return text.replace('\x00', '').strip()
