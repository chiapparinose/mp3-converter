"""Property-based test for filename sanitization."""

import pytest
from hypothesis import given, strategies as st
from src.file_manager import FileManager


# Feature: youtube-to-mp3-converter, Property 7: Filename Sanitization
@pytest.mark.property
@given(st.text())
def test_filename_sanitization_removes_invalid_chars(title):
    r"""
    For any video title string, the filename sanitization function SHALL remove 
    all invalid filename characters (< > : " / \ | ? *) while preserving all 
    valid characters, producing a valid filename for the target filesystem.
    
    **Validates: Requirements 6.2**
    """
    # Sanitize the filename
    sanitized = FileManager.sanitize_filename(title)
    
    # Property 1: Result must be a string
    assert isinstance(sanitized, str), \
        "Sanitized filename must be a string"
    
    # Property 2: No invalid characters should remain
    invalid_chars = set('<>:"/\\|?*')
    for char in sanitized:
        assert char not in invalid_chars, \
            f"Invalid character '{char}' found in sanitized filename: {sanitized}"
    
    # Property 3: All valid characters from original should be preserved
    # (i.e., characters that are not in the invalid set should remain)
    valid_chars_in_original = [c for c in title if c not in invalid_chars]
    valid_chars_in_sanitized = list(sanitized)
    
    assert valid_chars_in_sanitized == valid_chars_in_original, \
        f"Valid characters not preserved. Original valid: {valid_chars_in_original}, Sanitized: {valid_chars_in_sanitized}"
    
    # Property 4: Length should be less than or equal to original
    assert len(sanitized) <= len(title), \
        f"Sanitized filename longer than original: {len(sanitized)} > {len(title)}"
    
    # Property 5: If original has no invalid chars, result should be identical
    if not any(c in invalid_chars for c in title):
        assert sanitized == title, \
            f"Filename without invalid chars was modified: '{title}' -> '{sanitized}'"


# Feature: youtube-to-mp3-converter, Property 7: Filename Sanitization (Known Invalid Chars)
@pytest.mark.property
@given(st.text(min_size=1).flatmap(
    lambda base: st.builds(
        lambda b, invalid: b + invalid,
        st.just(base),
        st.sampled_from(['<', '>', ':', '"', '/', '\\', '|', '?', '*'])
    )
))
def test_filename_sanitization_removes_each_invalid_char(filename_with_invalid):
    """
    For any filename containing at least one invalid character, the sanitization 
    function SHALL remove that character.
    
    **Validates: Requirements 6.2**
    """
    sanitized = FileManager.sanitize_filename(filename_with_invalid)
    
    # None of the invalid characters should remain
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        assert char not in sanitized, \
            f"Invalid character '{char}' not removed from: {sanitized}"


# Feature: youtube-to-mp3-converter, Property 7: Filename Sanitization (Only Invalid Chars)
@pytest.mark.property
@given(st.text(alphabet='<>:"/\\|?*', min_size=0, max_size=50))
def test_filename_sanitization_all_invalid_chars(all_invalid):
    """
    For any string containing only invalid characters, the sanitization function 
    SHALL return an empty string.
    
    **Validates: Requirements 6.2**
    """
    sanitized = FileManager.sanitize_filename(all_invalid)
    
    # Result should be empty string
    assert sanitized == "", \
        f"String with only invalid chars should become empty, got: '{sanitized}'"


# Feature: youtube-to-mp3-converter, Property 7: Filename Sanitization (Mixed Content)
@pytest.mark.property
@given(
    st.text(alphabet=st.characters(blacklist_categories=('Cc', 'Cs'), blacklist_characters='<>:"/\\|?*'), min_size=1, max_size=20),
    st.lists(st.sampled_from(['<', '>', ':', '"', '/', '\\', '|', '?', '*']), min_size=1, max_size=5)
)
def test_filename_sanitization_mixed_valid_invalid(valid_part, invalid_chars):
    """
    For any filename with mixed valid and invalid characters, the sanitization 
    function SHALL preserve only the valid characters in their original order.
    
    **Validates: Requirements 6.2**
    """
    # Create a mixed filename by interleaving valid and invalid characters
    mixed = valid_part + ''.join(invalid_chars)
    
    sanitized = FileManager.sanitize_filename(mixed)
    
    # Sanitized should equal the valid part only
    assert sanitized == valid_part, \
        f"Expected '{valid_part}', got '{sanitized}'"
    
    # No invalid characters should remain
    invalid_set = set('<>:"/\\|?*')
    assert not any(c in invalid_set for c in sanitized), \
        f"Invalid characters found in sanitized result: {sanitized}"


# Feature: youtube-to-mp3-converter, Property 7: Filename Sanitization (Idempotence)
@pytest.mark.property
@given(st.text())
def test_filename_sanitization_idempotent(title):
    """
    For any string, applying sanitization multiple times SHALL produce the same 
    result as applying it once (idempotence property).
    
    **Validates: Requirements 6.2**
    """
    sanitized_once = FileManager.sanitize_filename(title)
    sanitized_twice = FileManager.sanitize_filename(sanitized_once)
    sanitized_thrice = FileManager.sanitize_filename(sanitized_twice)
    
    # All results should be identical
    assert sanitized_once == sanitized_twice == sanitized_thrice, \
        f"Sanitization not idempotent: '{sanitized_once}' -> '{sanitized_twice}' -> '{sanitized_thrice}'"


# Feature: youtube-to-mp3-converter, Property 7: Filename Sanitization (Common Video Titles)
@pytest.mark.property
@given(st.sampled_from([
    "My Video: The Best Tutorial",
    "How to Code | Python Guide",
    "File/Path\\Example",
    "Question? Answer!",
    "Wildcards * and ? symbols",
    'Video with "quotes"',
    "Normal Video Title",
    "Video<tag>",
    "C:\\Users\\Videos\\file.mp4",
    "https://example.com/video",
]))
def test_filename_sanitization_common_titles(video_title):
    """
    For common video title patterns, the sanitization function SHALL remove 
    invalid characters while preserving the readable content.
    
    **Validates: Requirements 6.2**
    """
    sanitized = FileManager.sanitize_filename(video_title)
    
    # Should not contain any invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        assert char not in sanitized, \
            f"Invalid character '{char}' found in: {sanitized}"
    
    # Should not be None
    assert sanitized is not None
    
    # Should be a string
    assert isinstance(sanitized, str)
