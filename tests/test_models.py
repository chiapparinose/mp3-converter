"""Unit tests for data models."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from src.models import (
    Stage, VideoMetadata, ValidationResult, DownloadResult,
    ConversionResult, MP3File, ProgressUpdate, ErrorContext, ErrorResponse
)


@pytest.mark.unit
class TestDataModels:
    """Test data model classes."""
    
    def test_stage_enum_values(self):
        """Test Stage enum has all required values."""
        assert Stage.VALIDATION.value == "validation"
        assert Stage.DOWNLOAD.value == "download"
        assert Stage.CONVERSION.value == "conversion"
        assert Stage.METADATA.value == "metadata"
        assert Stage.DELIVERY.value == "delivery"
        assert Stage.CLEANUP.value == "cleanup"
        assert Stage.ERROR.value == "error"
    
    def test_video_metadata_initialization(self):
        """Test VideoMetadata dataclass initialization."""
        metadata = VideoMetadata(
            video_id="test123",
            title="Test Video",
            channel="Test Channel",
            duration=180,
            thumbnail_url="https://example.com/thumb.jpg"
        )
        assert metadata.video_id == "test123"
        assert metadata.title == "Test Video"
        assert metadata.channel == "Test Channel"
        assert metadata.duration == 180
        assert metadata.thumbnail_url == "https://example.com/thumb.jpg"
        assert metadata.upload_date is None
        assert metadata.description is None
    
    def test_validation_result_initialization(self):
        """Test ValidationResult dataclass initialization."""
        metadata = VideoMetadata(
            video_id="test123",
            title="Test",
            channel="Channel",
            duration=100,
            thumbnail_url="https://example.com/thumb.jpg"
        )
        result = ValidationResult(
            is_valid=True,
            video_metadata=metadata,
            error_message=None,
            validation_time=0.5
        )
        assert result.is_valid is True
        assert result.video_metadata == metadata
        assert result.error_message is None
        assert result.validation_time == 0.5
    
    def test_download_result_initialization(self):
        """Test DownloadResult dataclass initialization."""
        result = DownloadResult(
            success=True,
            audio_file_path=Path("temp/audio.webm"),
            format="webm",
            file_size=5242880,
            download_time=10.5
        )
        assert result.success is True
        assert result.audio_file_path == Path("temp/audio.webm")
        assert result.format == "webm"
        assert result.file_size == 5242880
        assert result.download_time == 10.5
    
    def test_conversion_result_initialization(self):
        """Test ConversionResult dataclass initialization."""
        result = ConversionResult(
            success=True,
            mp3_file_path=Path("output/audio.mp3"),
            bitrate=192,
            file_size=3932160,
            conversion_time=5.2
        )
        assert result.success is True
        assert result.mp3_file_path == Path("output/audio.mp3")
        assert result.bitrate == 192
        assert result.file_size == 3932160
        assert result.conversion_time == 5.2
    
    def test_mp3_file_initialization(self):
        """Test MP3File dataclass initialization."""
        metadata = VideoMetadata(
            video_id="test123",
            title="Test",
            channel="Channel",
            duration=180,
            thumbnail_url="https://example.com/thumb.jpg"
        )
        mp3_file = MP3File(
            file_path=Path("output/test.mp3"),
            file_size=3932160,
            file_size_mb=3.75,
            filename="test.mp3",
            bitrate=192,
            duration=180,
            metadata=metadata
        )
        assert mp3_file.file_path == Path("output/test.mp3")
        assert mp3_file.file_size == 3932160
        assert mp3_file.file_size_mb == 3.75
        assert mp3_file.filename == "test.mp3"
        assert mp3_file.bitrate == 192
        assert mp3_file.duration == 180
        assert mp3_file.metadata == metadata
    
    def test_progress_update_initialization(self):
        """Test ProgressUpdate dataclass initialization."""
        update = ProgressUpdate(
            stage=Stage.DOWNLOAD,
            stage_progress=0.5,
            overall_progress=0.3,
            estimated_time_remaining=timedelta(seconds=30),
            message="Downloading audio..."
        )
        assert update.stage == Stage.DOWNLOAD
        assert update.stage_progress == 0.5
        assert update.overall_progress == 0.3
        assert update.estimated_time_remaining == timedelta(seconds=30)
        assert update.message == "Downloading audio..."
    
    def test_error_context_initialization(self):
        """Test ErrorContext dataclass initialization."""
        context = ErrorContext(
            stage=Stage.DOWNLOAD,
            operation="download_audio",
            timestamp=datetime.now(),
            additional_info={"url": "https://youtube.com/watch?v=test"}
        )
        assert context.stage == Stage.DOWNLOAD
        assert context.operation == "download_audio"
        assert isinstance(context.timestamp, datetime)
        assert context.additional_info["url"] == "https://youtube.com/watch?v=test"
    
    def test_error_response_initialization(self):
        """Test ErrorResponse dataclass initialization."""
        response = ErrorResponse(
            success=False,
            error_code="DOWNLOAD_FAILED",
            error_message="Failed to download video",
            stage=Stage.DOWNLOAD,
            retry_possible=True
        )
        assert response.success is False
        assert response.error_code == "DOWNLOAD_FAILED"
        assert response.error_message == "Failed to download video"
        assert response.stage == Stage.DOWNLOAD
        assert isinstance(response.timestamp, datetime)
        assert response.retry_possible is True
    
    def test_error_response_default_timestamp(self):
        """Test ErrorResponse sets timestamp automatically."""
        response = ErrorResponse()
        assert isinstance(response.timestamp, datetime)
        # Timestamp should be recent (within last second)
        assert (datetime.now() - response.timestamp).total_seconds() < 1
