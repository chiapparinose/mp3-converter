"""Unit tests for ErrorHandler component."""

import pytest
from datetime import datetime
from src.error_handler import (
    ErrorHandler, 
    InvalidURLFormatError,
    VideoNotFoundError,
    VideoAccessRestrictedError,
    DownloadFailedError,
    UnsupportedFormatError,
    FFmpegNotFoundError,
    ConversionTimeoutError
)
from src.models import ErrorContext, Stage


class TestErrorHandler:
    """Tests for ErrorHandler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = ErrorHandler()
    
    def test_handle_invalid_url_error(self):
        """Test handling of invalid URL format error."""
        error = InvalidURLFormatError("Invalid URL")
        context = ErrorContext(
            stage=Stage.VALIDATION,
            operation="validate_url",
            timestamp=datetime.now()
        )
        
        response = self.handler.handle_error(error, context)
        
        assert response.success is False
        assert response.error_code == "InvalidURLFormatError"
        assert "Invalid YouTube URL format" in response.error_message
        assert response.stage == Stage.VALIDATION
        assert response.retry_possible is False
    
    def test_handle_video_not_found_error(self):
        """Test handling of video not found error."""
        error = VideoNotFoundError("Video not found")
        context = ErrorContext(
            stage=Stage.VALIDATION,
            operation="check_video",
            timestamp=datetime.now()
        )
        
        response = self.handler.handle_error(error, context)
        
        assert response.success is False
        assert "could not be found" in response.error_message
    
    def test_handle_access_restricted_error(self):
        """Test handling of access restricted error."""
        error = VideoAccessRestrictedError("Private video")
        context = ErrorContext(
            stage=Stage.VALIDATION,
            operation="check_access",
            timestamp=datetime.now()
        )
        
        response = self.handler.handle_error(error, context)
        
        assert "private or restricted" in response.error_message
    
    def test_handle_download_failed_error(self):
        """Test handling of download failed error."""
        error = DownloadFailedError("Network error")
        context = ErrorContext(
            stage=Stage.DOWNLOAD,
            operation="download_audio",
            timestamp=datetime.now()
        )
        
        response = self.handler.handle_error(error, context)
        
        assert "Download failed" in response.error_message
        assert response.retry_possible is True
    
    def test_handle_unsupported_format_error(self):
        """Test handling of unsupported format error."""
        error = UnsupportedFormatError("Format not supported")
        context = ErrorContext(
            stage=Stage.DOWNLOAD,
            operation="download_audio",
            timestamp=datetime.now()
        )
        
        response = self.handler.handle_error(error, context)
        
        assert "format is not supported" in response.error_message
    
    def test_handle_ffmpeg_not_found_error(self):
        """Test handling of FFmpeg not found error."""
        error = FFmpegNotFoundError("FFmpeg not installed")
        context = ErrorContext(
            stage=Stage.CONVERSION,
            operation="convert_to_mp3",
            timestamp=datetime.now()
        )
        
        response = self.handler.handle_error(error, context)
        
        assert "FFmpeg is not installed" in response.error_message
    
    def test_handle_conversion_timeout_error(self):
        """Test handling of conversion timeout error."""
        error = ConversionTimeoutError("Conversion timed out")
        context = ErrorContext(
            stage=Stage.CONVERSION,
            operation="convert_to_mp3",
            timestamp=datetime.now()
        )
        
        response = self.handler.handle_error(error, context)
        
        assert "took too long" in response.error_message
    
    def test_get_user_message_for_unknown_error(self):
        """Test user message for unknown error type."""
        error = Exception("Unknown error")
        message = self.handler.get_user_message(error)
        
        assert "unexpected error" in message.lower()
    
    def test_error_context_creation(self):
        """Test error context dataclass."""
        context = ErrorContext(
            stage=Stage.DOWNLOAD,
            operation="test_operation",
            timestamp=datetime.now(),
            additional_info={"key": "value"}
        )
        
        assert context.stage == Stage.DOWNLOAD
        assert context.operation == "test_operation"
        assert context.additional_info == {"key": "value"}
