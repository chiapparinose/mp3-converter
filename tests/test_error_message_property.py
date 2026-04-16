"""Property test for error message descriptiveness.

Feature: youtube-to-mp3-converter, Property 9: Error Message Descriptiveness
Validates: Requirements 7.1, 7.3, 7.4
"""

from hypothesis import given, strategies as st, settings
from datetime import datetime
from src.error_handler import (
    ErrorHandler,
    InvalidURLFormatError,
    VideoNotFoundError,
    VideoAccessRestrictedError,
    ValidationTimeoutError,
    DownloadFailedError,
    UnsupportedFormatError,
    InsufficientStorageError,
    FFmpegNotFoundError,
    ConversionTimeoutError,
    AudioCorruptedError,
    FileAccessError,
    ConverterError
)
from src.models import ErrorContext, Stage


# Strategy for generating error types
error_types = st.sampled_from([
    InvalidURLFormatError,
    VideoNotFoundError,
    VideoAccessRestrictedError,
    ValidationTimeoutError,
    DownloadFailedError,
    UnsupportedFormatError,
    InsufficientStorageError,
    FFmpegNotFoundError,
    ConversionTimeoutError,
    AudioCorruptedError,
    FileAccessError,
])

# Strategy for generating stages
stages = st.sampled_from([
    Stage.VALIDATION,
    Stage.DOWNLOAD,
    Stage.CONVERSION,
    Stage.METADATA,
    Stage.DELIVERY,
])


@given(error_type=error_types, stage=stages, message=st.text(min_size=1, max_size=100))
@settings(max_examples=50)
def test_error_message_descriptiveness(error_type, stage, message):
    """
    For any error that occurs during conversion, the system SHALL return a
    descriptive error message that identifies the stage and nature of the failure.
    """
    handler = ErrorHandler()
    
    # Create error of the given type
    error = error_type(message)
    
    # Create context
    context = ErrorContext(
        stage=stage,
        operation="test_operation",
        timestamp=datetime.now()
    )
    
    # Handle error
    response = handler.handle_error(error, context)
    
    # Verify response structure
    assert response.success is False
    assert len(response.error_message) > 0
    assert response.stage == stage
    assert len(response.error_code) > 0
    
    # Verify message is descriptive (not empty, not just the exception name)
    assert response.error_message != ""
    assert len(response.error_message) > 10  # Reasonably descriptive


@given(error_type=error_types)
@settings(max_examples=30)
def test_error_message_identifies_stage(error_type):
    """
    Error response should identify the stage where error occurred.
    """
    handler = ErrorHandler()
    error = error_type("Test error")
    
    for stage in [Stage.VALIDATION, Stage.DOWNLOAD, Stage.CONVERSION, Stage.METADATA]:
        context = ErrorContext(
            stage=stage,
            operation="test",
            timestamp=datetime.now()
        )
        response = handler.handle_error(error, context)
        assert response.stage == stage


@given(message=st.text(min_size=1, max_size=200))
@settings(max_examples=30)
def test_generic_error_handling(message):
    """
    Unexpected errors should return a generic message to users.
    """
    handler = ErrorHandler()
    
    # Create a generic exception
    error = Exception(message)
    context = ErrorContext(
        stage=Stage.CONVERSION,
        operation="test",
        timestamp=datetime.now()
    )
    
    response = handler.handle_error(error, context)
    
    # Should have a message
    assert len(response.error_message) > 0
    # Should not expose internal details
    assert response.success is False
