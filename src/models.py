"""Data models and core types for the YouTube to MP3 Converter."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Callable


class Stage(Enum):
    """Pipeline stages for the conversion process."""
    VALIDATION = "validation"
    DOWNLOAD = "download"
    CONVERSION = "conversion"
    METADATA = "metadata"
    DELIVERY = "delivery"
    CLEANUP = "cleanup"
    ERROR = "error"


@dataclass
class VideoMetadata:
    """Metadata extracted from a YouTube video."""
    video_id: str
    title: str
    channel: str
    duration: int  # seconds
    thumbnail_url: str
    upload_date: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of URL validation."""
    is_valid: bool
    video_metadata: Optional[VideoMetadata]
    error_message: Optional[str]
    validation_time: float  # seconds


@dataclass
class DownloadResult:
    """Result of video download operation."""
    success: bool
    audio_file_path: Optional[Path]
    format: str  # e.g., "webm", "m4a"
    file_size: int  # bytes
    download_time: float  # seconds


@dataclass
class ConversionResult:
    """Result of audio conversion to MP3."""
    success: bool
    mp3_file_path: Optional[Path]
    bitrate: int  # kbps
    file_size: int  # bytes
    conversion_time: float  # seconds


@dataclass
class MP3File:
    """Final MP3 file information."""
    file_path: Path
    file_size: int  # bytes
    file_size_mb: float
    filename: str
    bitrate: int  # kbps
    duration: int  # seconds
    metadata: VideoMetadata


@dataclass
class ProgressUpdate:
    """Progress update information."""
    stage: Stage
    stage_progress: float  # 0.0 to 1.0
    overall_progress: float  # 0.0 to 1.0
    estimated_time_remaining: Optional[timedelta]
    message: str


@dataclass
class ErrorContext:
    """Context information for error handling."""
    stage: Stage
    operation: str
    timestamp: datetime
    additional_info: Optional[dict] = None


@dataclass
class ErrorResponse:
    """Standardized error response."""
    success: bool = False
    error_code: str = ""
    error_message: str = ""  # User-friendly message
    stage: Stage = Stage.ERROR
    timestamp: datetime = None
    retry_possible: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
