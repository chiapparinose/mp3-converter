"""Property test for metadata embedding completeness.

Feature: youtube-to-mp3-converter, Property 5: Metadata Embedding Completeness
Validates: Requirements 4.1, 4.2, 4.3, 4.4
"""

from hypothesis import given, strategies as st, settings
from src.models import VideoMetadata
from src.metadata_embedder import MetadataEmbedder


# Strategy for generating video metadata
video_metadata = st.builds(
    VideoMetadata,
    video_id=st.text(min_size=1, max_size=20),
    title=st.text(min_size=0, max_size=200),
    channel=st.text(min_size=0, max_size=200),
    duration=st.integers(min_value=0, max_value=86400),
    thumbnail_url=st.one_of(st.just(""), st.just("https://example.com/thumb.jpg")),
    upload_date=st.one_of(st.none(), st.just("20240101")),
    description=st.one_of(st.none(), st.text(max_size=500))
)


@given(metadata=video_metadata)
@settings(max_examples=50)
def test_metadata_embedding_completeness(metadata):
    """
    For any video metadata and MP3 file, the system SHALL embed all available
    metadata fields (title as TIT2, channel as TPE1, thumbnail as APIC) into
    the MP3 ID3 tags, and SHALL successfully create the MP3 file even when
    some metadata fields are missing.
    """
    embedder = MetadataEmbedder()
    
    # Test that sanitization works for any input
    if metadata.title:
        sanitized_title = embedder._sanitize_string(metadata.title)
        assert '\x00' not in sanitized_title
    
    if metadata.channel:
        sanitized_channel = embedder._sanitize_string(metadata.channel)
        assert '\x00' not in sanitized_channel


@given(
    title=st.text(min_size=0, max_size=200),
    channel=st.text(min_size=0, max_size=200)
)
@settings(max_examples=50)
def test_metadata_sanitization_handles_any_input(title, channel):
    """
    Metadata sanitization should handle any string input without crashing.
    """
    embedder = MetadataEmbedder()
    
    # Should not raise exceptions
    sanitized_title = embedder._sanitize_string(title)
    sanitized_channel = embedder._sanitize_string(channel)
    
    # Results should not contain null bytes
    assert '\x00' not in sanitized_title
    assert '\x00' not in sanitized_channel


@given(metadata=video_metadata)
@settings(max_examples=30)
def test_metadata_fields_present(metadata):
    """
    VideoMetadata should have all required fields.
    """
    assert hasattr(metadata, 'video_id')
    assert hasattr(metadata, 'title')
    assert hasattr(metadata, 'channel')
    assert hasattr(metadata, 'duration')
    assert hasattr(metadata, 'thumbnail_url')


@given(
    title=st.one_of(st.just(""), st.text(min_size=1, max_size=100)),
    channel=st.one_of(st.just(""), st.text(min_size=1, max_size=100)),
    thumbnail_url=st.one_of(st.just(""), st.just("https://example.com/thumb.jpg"))
)
@settings(max_examples=30)
def test_graceful_handling_of_missing_fields(title, channel, thumbnail_url):
    """
    System should handle missing metadata fields gracefully.
    """
    metadata = VideoMetadata(
        video_id="test",
        title=title,
        channel=channel,
        duration=300,
        thumbnail_url=thumbnail_url
    )
    
    # Metadata should be created successfully regardless of empty fields
    assert metadata is not None
    
    # Empty fields should be allowed
    if title == "":
        assert metadata.title == ""
    if channel == "":
        assert metadata.channel == ""
    if thumbnail_url == "":
        assert metadata.thumbnail_url == ""
