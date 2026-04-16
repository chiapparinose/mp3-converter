"""Property test for duration warning logic.

Feature: youtube-to-mp3-converter, Property 2: Duration Warning Logic
Validates: Requirements 2.3
"""

from hypothesis import given, strategies as st, settings
from src.video_downloader import VideoDownloader


# Strategy for generating duration values (in seconds)
duration_seconds = st.integers(min_value=0, max_value=86400)  # 0 to 24 hours


@given(duration=duration_seconds)
@settings(max_examples=100)
def test_duration_warning_logic(duration):
    """
    For any video metadata with a duration value, the system SHALL issue
    a warning message if and only if the duration exceeds 2 hours (7200 seconds).
    """
    should_warn = VideoDownloader.check_duration_warning(duration)
    
    # Warning should be issued only if duration > 7200 seconds
    if duration > 7200:
        assert should_warn is True, f"Expected warning for {duration}s (> 7200s)"
    else:
        assert should_warn is False, f"Expected no warning for {duration}s (<= 7200s)"


@given(duration=st.integers(min_value=0, max_value=7200))
@settings(max_examples=50)
def test_no_warning_for_short_videos(duration):
    """
    Videos with duration <= 2 hours should not trigger warning.
    """
    assert VideoDownloader.check_duration_warning(duration) is False


@given(duration=st.integers(min_value=7201, max_value=86400))
@settings(max_examples=50)
def test_warning_for_long_videos(duration):
    """
    Videos with duration > 2 hours should trigger warning.
    """
    assert VideoDownloader.check_duration_warning(duration) is True


@given(hours=st.floats(min_value=0.0, max_value=24.0, allow_nan=False))
@settings(max_examples=50)
def test_duration_warning_with_fractional_hours(hours):
    """
    Test duration warning with fractional hour values.
    """
    duration_seconds = int(hours * 3600)
    should_warn = VideoDownloader.check_duration_warning(duration_seconds)
    
    # Warning if hours > 2
    if hours > 2.0:
        assert should_warn is True
    else:
        assert should_warn is False
