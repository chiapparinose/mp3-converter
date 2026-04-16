"""Error handling component for centralized error management."""

import logging
from typing import Optional
from datetime import datetime
from .models import ErrorResponse, ErrorContext, Stage


# Custom exception classes
class ConverterError(Exception):
    """Base exception for converter errors."""
    pass


class InvalidURLFormatError(ConverterError):
    """Invalid YouTube URL format."""
    pass


class VideoNotFoundError(ConverterError):
    """Video not found."""
    pass


class VideoAccessRestrictedError(ConverterError):
    """Video is private or restricted."""
    pass


class ValidationTimeoutError(ConverterError):
    """Validation timed out."""
    pass


class DownloadFailedError(ConverterError):
    """Download failed after retries."""
    pass


class UnsupportedFormatError(ConverterError):
    """Unsupported video format."""
    pass


class InsufficientStorageError(ConverterError):
    """Insufficient storage space."""
    pass


class FFmpegNotFoundError(ConverterError):
    """FFmpeg not installed."""
    pass


class ConversionTimeoutError(ConverterError):
    """Conversion timed out."""
    pass


class AudioCorruptedError(ConverterError):
    """Audio stream corrupted."""
    pass


class FileAccessError(ConverterError):
    """File access error."""
    pass


class ErrorHandler:
    """Centralizes error handling and user messaging."""
    
    ERROR_MESSAGES = {
        InvalidURLFormatError: "Invalid YouTube URL format. Please check the URL and try again.",
        VideoNotFoundError: "The video could not be found. Please check the URL and try again.",
        VideoAccessRestrictedError: "This video is private or restricted. Authentication may be required.",
        ValidationTimeoutError: "Validation timed out. Please try again.",
        DownloadFailedError: "Download failed after multiple attempts. Please check your connection and try again.",
        UnsupportedFormatError: "This video format is not supported. Supported formats: MP4, WebM, M4A.",
        InsufficientStorageError: "Insufficient storage space. Please free up disk space and try again.",
        FFmpegNotFoundError: "FFmpeg is not installed. Please install FFmpeg to continue.",
        ConversionTimeoutError: "Conversion took too long. Please try a shorter video.",
        AudioCorruptedError: "The audio stream is corrupted. Please try a different video.",
        FileAccessError: "Unable to access file. Please check permissions.",
        ConverterError: "An unexpected error occurred during conversion.",
    }
    
    def __init__(self):
        """Initialize ErrorHandler."""
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """
        Handle an error and return standardized response.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            ErrorResponse with user-friendly message
        """
        self.log_error(error, context)
        
        error_code = type(error).__name__
        error_message = self.get_user_message(error)
        retry_possible = isinstance(error, (DownloadFailedError, ValidationTimeoutError))
        
        return ErrorResponse(
            success=False,
            error_code=error_code,
            error_message=error_message,
            stage=context.stage,
            timestamp=context.timestamp,
            retry_possible=retry_possible
        )
    
    def log_error(self, error: Exception, context: ErrorContext) -> None:
        """
        Log detailed error information.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
        """
        self.logger.error(
            f"[{context.stage.value}] {context.operation}: {type(error).__name__}: {str(error)}"
        )
    
    def get_user_message(self, error: Exception) -> str:
        """
        Get user-friendly error message.
        
        Args:
            error: The exception that occurred
            
        Returns:
            User-friendly error message
        """
        # Check for specific error types first
        for error_type, message in self.ERROR_MESSAGES.items():
            if isinstance(error, error_type):
                return message
        
        # For generic exceptions, check the error message content
        error_str = str(error).lower()
        if 'invalid url' in error_str or 'url format' in error_str:
            return "Invalid YouTube URL format. Please check the URL and try again."
        elif 'not found' in error_str or 'unavailable' in error_str:
            return "The video could not be found. Please check the URL and try again."
        elif 'private' in error_str or 'restricted' in error_str:
            return "This video is private or restricted. Authentication may be required."
        
        return "An unexpected error occurred. Please try again."
