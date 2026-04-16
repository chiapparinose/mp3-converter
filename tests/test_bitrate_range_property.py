"""Property test for bitrate range enforcement.

Feature: youtube-to-mp3-converter, Property 4: Bitrate Range Enforcement
Validates: Requirements 3.2
"""

from hypothesis import given, strategies as st, settings
from src.audio_converter import AudioConverter


# Strategy for generating arbitrary bitrate values
bitrate_values = st.integers(min_value=0, max_value=10000)


@given(bitrate=bitrate_values)
@settings(max_examples=100)
def test_bitrate_range_enforcement(bitrate):
    """
    For any bitrate value provided for MP3 encoding, the system SHALL enforce
    that the final encoded bitrate falls within the range of 128 kbps to 320 kbps,
    clamping values outside this range.
    """
    result = AudioConverter.clamp_bitrate(bitrate)
    
    # Result must be within valid range
    assert 128 <= result <= 320, f"Bitrate {result} not in range [128, 320]"


@given(bitrate=st.integers(min_value=128, max_value=320))
@settings(max_examples=50)
def test_valid_bitrate_unchanged(bitrate):
    """
    Bitrate values within the valid range should remain unchanged.
    """
    result = AudioConverter.clamp_bitrate(bitrate)
    assert result == bitrate


@given(bitrate=st.integers(min_value=0, max_value=127))
@settings(max_examples=50)
def test_low_bitrate_clamped_to_minimum(bitrate):
    """
    Bitrate values below 128 should be clamped to 128.
    """
    result = AudioConverter.clamp_bitrate(bitrate)
    assert result == 128


@given(bitrate=st.integers(min_value=321, max_value=10000))
@settings(max_examples=50)
def test_high_bitrate_clamped_to_maximum(bitrate):
    """
    Bitrate values above 320 should be clamped to 320.
    """
    result = AudioConverter.clamp_bitrate(bitrate)
    assert result == 320


@given(bitrate=st.integers(min_value=-1000, max_value=-1))
@settings(max_examples=30)
def test_negative_bitrate_clamped(bitrate):
    """
    Negative bitrate values should be clamped to minimum.
    """
    result = AudioConverter.clamp_bitrate(bitrate)
    assert result == 128
