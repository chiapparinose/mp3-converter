"""File management component for temporary files and storage."""

import uuid
import re
import threading
import time
from pathlib import Path
from typing import Optional


class FileManager:
    """Manages temporary files and storage cleanup."""
    
    def __init__(self, temp_dir: str = "temp"):
        """
        Initialize FileManager.
        
        Args:
            temp_dir: Directory for temporary files
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def create_temp_file(self, prefix: str) -> Path:
        """
        Create a temporary file with unique identifier.
        
        Args:
            prefix: Prefix for the temporary file
            
        Returns:
            Path to the created temporary file
        """
        # Generate unique identifier using UUID
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{prefix}_{unique_id}"
        file_path = self.temp_dir / filename
        
        # Create the file (touch it)
        file_path.touch()
        
        return file_path
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """
        Remove invalid filename characters.
        
        Args:
            name: The filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters: < > : " / \ | ? *
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '', name)
        return sanitized
    
    def get_storage_usage(self) -> int:
        """
        Get current storage usage in bytes.
        
        Returns:
            Total size of temporary directory in bytes
        """
        total_size = 0
        
        # Iterate through all files in the temporary directory
        for file_path in self.temp_dir.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
    
    def cleanup_file(self, path: Path, delay_seconds: int = 60) -> None:
        """
        Delete a file after a specified delay.
        
        Args:
            path: Path to file to cleanup
            delay_seconds: Delay before cleanup in seconds (default: 60)
        """
        def delayed_cleanup():
            time.sleep(delay_seconds)
            try:
                if path.exists() and path.is_file():
                    path.unlink()
            except Exception:
                pass  # Silently ignore cleanup failures
        
        # Start cleanup in a background thread
        cleanup_thread = threading.Thread(target=delayed_cleanup, daemon=True)
        cleanup_thread.start()
    
    def cleanup_old_files(self) -> None:
        """Clean up oldest files when storage exceeds 4GB threshold."""
        max_storage_bytes = 4 * 1024 * 1024 * 1024  # 4 GB
        
        if self.get_storage_usage() <= max_storage_bytes:
            return
        
        # Get all files with their modification times
        files = []
        for file_path in self.temp_dir.rglob('*'):
            if file_path.is_file():
                try:
                    mtime = file_path.stat().st_mtime
                    files.append((file_path, mtime))
                except Exception:
                    pass
        
        # Sort by modification time (oldest first)
        files.sort(key=lambda x: x[1])
        
        # Delete oldest files until under threshold
        for file_path, _ in files:
            if self.get_storage_usage() <= max_storage_bytes:
                break
            try:
                file_path.unlink()
            except Exception:
                pass
    
    def enforce_storage_limit(self) -> bool:
        """
        Check if storage is within 5GB limit.
        
        Returns:
            True if under limit, False if over limit
        """
        max_storage_bytes = 5 * 1024 * 1024 * 1024  # 5 GB
        return self.get_storage_usage() <= max_storage_bytes
