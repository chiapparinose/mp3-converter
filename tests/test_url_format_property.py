"""Property-based test for URL format validation."""

import pytest
from hypothesis import given, strategies as st, assume
from src.url_validator import URLValidator


# Feature: youtube-to-mp3-converter, Property 1: URL Format Validation
@pytest.mark.property
@given(st.text())
def test_url_format_validation(url_input):
    """
    For any string input, the URL validator SHALL correctly identify whether it 
    matches valid YouTube URL patterns and reject invalid formats with an error 
    message returned within 2 seconds.
    
    **Validates: Requirements 1.1, 1.4**
    """
    validator = URLValidator()
    
    # Validate the URL format
    result = validator.validate_format(url_input)
    
    # Property 1: Validation must complete within 2 seconds
    assert result.validation_time <= 2.0, \
        f"Validation took {result.validation_time}s, exceeding 2 second timeout"
    
    # Property 2: Result must have a boolean is_valid field
    assert isinstance(result.is_valid, bool), \
        "ValidationResult.is_valid must be a boolean"
    
    # Property 3: If invalid, must have an error message
    if not result.is_valid:
        assert result.error_message is not None, \
            "Invalid URLs must have an error message"
        assert isinstance(result.error_message, str), \
            "Error message must be a string"
        assert len(result.error_message) > 0, \
            "Error message must not be empty"
    
    # Property 4: If valid, must match at least one YouTube URL pattern
    if result.is_valid:
        # Valid URLs should match one of the supported patterns
        patterns = [
            validator.WATCH_PATTERN,
            validator.SHORT_PATTERN,
            validator.EMBED_PATTERN,
            validator.MOBILE_PATTERN,
            validator.SHORTS_PATTERN
        ]
        import re
        matches_pattern = any(re.match(pattern, url_input) for pattern in patterns)
        assert matches_pattern, \
            f"URL marked as valid but doesn't match any pattern: {url_input}"
    
    # Property 5: Validation time must be non-negative
    assert result.validation_time >= 0, \
        "Validation time cannot be negative"


# Feature: youtube-to-mp3-converter, Property 1: URL Format Validation (Known Valid URLs)
@pytest.mark.property
@given(st.sampled_from([
    "https://www.youtube.com/watch?v=",
    "https://youtube.com/watch?v=",
    "https://youtu.be/",
    "https://www.youtube.com/embed/",
    "https://youtube.com/embed/",
    "https://m.youtube.com/watch?v=",
    "https://www.youtube.com/shorts/",
    "https://youtube.com/shorts/",
    "http://www.youtube.com/watch?v=",
    "http://youtu.be/",
]).flatmap(lambda base: st.builds(
    lambda b, vid: b + vid,
    st.just(base),
    st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'), min_size=11, max_size=11)
)))
def test_valid_youtube_url_patterns_accepted(valid_url):
    """
    For any valid YouTube URL pattern with an 11-character video ID, the validator 
    SHALL accept it as valid.
    
    **Validates: Requirements 1.1**
    """
    validator = URLValidator()
    result = validator.validate_format(valid_url)
    
    # Valid YouTube URLs should be accepted
    assert result.is_valid is True, \
        f"Valid YouTube URL rejected: {valid_url}"
    
    # Should not have an error message
    assert result.error_message is None, \
        f"Valid URL should not have error message: {result.error_message}"
    
    # Must complete within timeout
    assert result.validation_time <= 2.0


# Feature: youtube-to-mp3-converter, Property 1: URL Format Validation (Known Invalid URLs)
@pytest.mark.property
@given(st.sampled_from([
    "https://www.notyoutube.com/watch?v=dQw4w9WgXcQ",  # Wrong domain
    "https://www.youtube.com/watch",  # Missing video ID
    "https://www.youtube.com/watch?v=short",  # Video ID too short
    "https://www.youtube.com/watch?v=toolongvideoid123",  # Video ID too long
    "https://example.com/video",  # Not YouTube
    "",  # Empty string
    "   ",  # Whitespace only
    "not a url at all",  # Plain text
    "ftp://youtube.com/watch?v=dQw4w9WgXcQ",  # Wrong protocol
    "https://www.youtube.com/watch?id=dQw4w9WgXcQ",  # Wrong parameter name
]))
def test_invalid_url_patterns_rejected(invalid_url):
    """
    For any invalid URL pattern, the validator SHALL reject it with an error message.
    
    **Validates: Requirements 1.1, 1.4**
    """
    validator = URLValidator()
    result = validator.validate_format(invalid_url)
    
    # Invalid URLs should be rejected
    assert result.is_valid is False, \
        f"Invalid URL accepted: {invalid_url}"
    
    # Must have an error message
    assert result.error_message is not None, \
        "Invalid URL must have an error message"
    assert len(result.error_message) > 0, \
        "Error message must not be empty"
    
    # Must complete within timeout
    assert result.validation_time <= 2.0


# Feature: youtube-to-mp3-converter, Property 1: URL Format Validation (Non-string inputs)
@pytest.mark.property
@given(st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.none(),
    st.lists(st.text()),
    st.dictionaries(st.text(), st.text())
))
def test_non_string_inputs_rejected(non_string_input):
    """
    For any non-string input, the validator SHALL reject it with an appropriate error message.
    
    **Validates: Requirements 1.1, 1.4**
    """
    validator = URLValidator()
    result = validator.validate_format(non_string_input)
    
    # Non-string inputs should be rejected
    assert result.is_valid is False, \
        f"Non-string input accepted: {type(non_string_input)}"
    
    # Must have an error message mentioning string requirement
    assert result.error_message is not None
    assert "string" in result.error_message.lower(), \
        f"Error message should mention string requirement: {result.error_message}"
    
    # Must complete within timeout
    assert result.validation_time <= 2.0
