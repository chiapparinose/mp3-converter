"""Unit tests for URLValidator component."""

import pytest
from unittest.mock import patch, MagicMock
from src.url_validator import URLValidator
from src.models import ValidationResult, VideoMetadata


class TestURLValidator:
    """Test suite for URLValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = URLValidator()
    
    def test_valid_watch_url(self):
        """Test validation of standard watch URL format."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
        assert result.validation_time < URLValidator.VALIDATION_TIMEOUT
    
    def test_valid_watch_url_without_www(self):
        """Test validation of watch URL without www."""
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_watch_url_with_additional_params(self):
        """Test validation of watch URL with additional query parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s&list=PLtest"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_short_url(self):
        """Test validation of short URL format (youtu.be)."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_short_url_with_params(self):
        """Test validation of short URL with query parameters."""
        url = "https://youtu.be/dQw4w9WgXcQ?t=10"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_embed_url(self):
        """Test validation of embed URL format."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_embed_url_without_www(self):
        """Test validation of embed URL without www."""
        url = "https://youtube.com/embed/dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_mobile_url(self):
        """Test validation of mobile URL format."""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_shorts_url(self):
        """Test validation of shorts URL format."""
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_shorts_url_without_www(self):
        """Test validation of shorts URL without www."""
        url = "https://youtube.com/shorts/dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_http_protocol_accepted(self):
        """Test that HTTP protocol is accepted (not just HTTPS)."""
        url = "http://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_invalid_url_wrong_domain(self):
        """Test rejection of URL with wrong domain."""
        url = "https://www.notyoutube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert "does not match any supported YouTube URL pattern" in result.error_message
    
    def test_invalid_url_missing_video_id(self):
        """Test rejection of URL without video ID."""
        url = "https://www.youtube.com/watch"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert result.error_message is not None
    
    def test_invalid_url_wrong_video_id_length(self):
        """Test rejection of URL with incorrect video ID length (not 11 characters)."""
        url = "https://www.youtube.com/watch?v=short"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert result.error_message is not None
    
    def test_invalid_url_not_youtube(self):
        """Test rejection of non-YouTube URL."""
        url = "https://www.example.com/video"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert result.error_message is not None
    
    def test_invalid_url_empty_string(self):
        """Test rejection of empty string."""
        url = ""
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert "cannot be empty" in result.error_message
    
    def test_invalid_url_whitespace_only(self):
        """Test rejection of whitespace-only string."""
        url = "   "
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert "cannot be empty" in result.error_message
    
    def test_invalid_url_not_string(self):
        """Test rejection of non-string input."""
        url = 12345
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert "must be a string" in result.error_message
    
    def test_invalid_url_none(self):
        """Test rejection of None input."""
        url = None
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert "must be a string" in result.error_message
    
    def test_validation_timeout_enforcement(self):
        """Test that validation time is tracked and within timeout."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.validation_time < URLValidator.VALIDATION_TIMEOUT
        assert result.validation_time >= 0
    
    def test_validation_result_structure(self):
        """Test that ValidationResult has correct structure."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'video_metadata')
        assert hasattr(result, 'error_message')
        assert hasattr(result, 'validation_time')
    
    def test_valid_url_no_metadata_in_format_validation(self):
        """Test that format validation doesn't populate metadata (that's for get_video_info)."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.video_metadata is None  # Metadata extraction is separate
    
    def test_invalid_url_special_characters(self):
        """Test rejection of URL with invalid special characters in video ID."""
        url = "https://www.youtube.com/watch?v=invalid@#$%"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is False
        assert result.error_message is not None
    
    def test_valid_url_video_id_with_underscore_and_dash(self):
        """Test acceptance of video ID with valid characters (alphanumeric, underscore, dash)."""
        url = "https://www.youtube.com/watch?v=abc_123-XYZ"
        result = self.validator.validate_format(url)
        
        assert result.is_valid is True
        assert result.error_message is None


class TestVideoAccessibility:
    """Test suite for video accessibility checking."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = URLValidator()
    
    @patch('yt_dlp.YoutubeDL')
    def test_check_video_exists_available(self, mock_ydl_class):
        """Test check_video_exists returns 'available' for accessible video."""
        # Mock yt-dlp to return video info
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {
            'id': 'dQw4w9WgXcQ',
            'title': 'Test Video',
            'age_limit': 0
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = self.validator.check_video_exists(url)
        
        assert result == "available"
        mock_ydl.extract_info.assert_called_once_with(url, download=False)
    
    @patch('yt_dlp.YoutubeDL')
    def test_check_video_exists_age_restricted(self, mock_ydl_class):
        """Test check_video_exists returns 'age_restricted' for age-restricted video."""
        # Mock yt-dlp to return video info with age limit
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {
            'id': 'test123',
            'title': 'Age Restricted Video',
            'age_limit': 18
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=test123"
        result = self.validator.check_video_exists(url)
        
        assert result == "age_restricted"
    
    @patch('yt_dlp.YoutubeDL')
    def test_check_video_exists_private(self, mock_ydl_class):
        """Test check_video_exists returns 'private' for private video."""
        # Mock yt-dlp to raise DownloadError for private video
        mock_ydl = MagicMock()
        import yt_dlp
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("This video is private")
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=private123"
        result = self.validator.check_video_exists(url)
        
        assert result == "private"
    
    @patch('yt_dlp.YoutubeDL')
    def test_check_video_exists_not_found(self, mock_ydl_class):
        """Test check_video_exists returns 'not_found' for non-existent video."""
        # Mock yt-dlp to raise DownloadError for unavailable video
        mock_ydl = MagicMock()
        import yt_dlp
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Video unavailable")
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=notfound123"
        result = self.validator.check_video_exists(url)
        
        assert result == "not_found"
    
    @patch('yt_dlp.YoutubeDL')
    def test_check_video_exists_age_restricted_error(self, mock_ydl_class):
        """Test check_video_exists returns 'age_restricted' when error mentions age restriction."""
        # Mock yt-dlp to raise DownloadError with age restriction message
        mock_ydl = MagicMock()
        import yt_dlp
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Age restricted content")
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=age123"
        result = self.validator.check_video_exists(url)
        
        assert result == "age_restricted"
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info_success(self, mock_ydl_class):
        """Test get_video_info extracts metadata successfully."""
        # Mock yt-dlp to return complete video info
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {
            'id': 'dQw4w9WgXcQ',
            'title': 'Test Video Title',
            'uploader': 'Test Channel',
            'duration': 212,
            'thumbnail': 'https://example.com/thumb.jpg',
            'upload_date': '20240101',
            'description': 'Test description'
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        metadata = self.validator.get_video_info(url)
        
        assert metadata is not None
        assert isinstance(metadata, VideoMetadata)
        assert metadata.video_id == 'dQw4w9WgXcQ'
        assert metadata.title == 'Test Video Title'
        assert metadata.channel == 'Test Channel'
        assert metadata.duration == 212
        assert metadata.thumbnail_url == 'https://example.com/thumb.jpg'
        assert metadata.upload_date == '20240101'
        assert metadata.description == 'Test description'
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info_with_thumbnails_array(self, mock_ydl_class):
        """Test get_video_info extracts thumbnail from thumbnails array."""
        # Mock yt-dlp to return video info with thumbnails array
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {
            'id': 'test123',
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'duration': 100,
            'thumbnails': [
                {'url': 'https://example.com/thumb_low.jpg'},
                {'url': 'https://example.com/thumb_high.jpg'}
            ]
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=test123"
        metadata = self.validator.get_video_info(url)
        
        assert metadata is not None
        assert metadata.thumbnail_url == 'https://example.com/thumb_high.jpg'
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info_with_channel_fallback(self, mock_ydl_class):
        """Test get_video_info uses 'channel' field when 'uploader' is missing."""
        # Mock yt-dlp to return video info without uploader
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {
            'id': 'test123',
            'title': 'Test Video',
            'channel': 'Test Channel Name',
            'duration': 100,
            'thumbnail': 'https://example.com/thumb.jpg'
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=test123"
        metadata = self.validator.get_video_info(url)
        
        assert metadata is not None
        assert metadata.channel == 'Test Channel Name'
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info_missing_optional_fields(self, mock_ydl_class):
        """Test get_video_info handles missing optional fields gracefully."""
        # Mock yt-dlp to return minimal video info
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {
            'id': 'test123',
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'duration': 100,
            'thumbnail': 'https://example.com/thumb.jpg'
            # No upload_date or description
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=test123"
        metadata = self.validator.get_video_info(url)
        
        assert metadata is not None
        assert metadata.upload_date is None
        assert metadata.description is None
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info_defaults_for_missing_fields(self, mock_ydl_class):
        """Test get_video_info provides defaults for missing required fields."""
        # Mock yt-dlp to return incomplete video info
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {
            'id': 'test123'
            # Missing most fields
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=test123"
        metadata = self.validator.get_video_info(url)
        
        assert metadata is not None
        assert metadata.video_id == 'test123'
        assert metadata.title == 'Unknown Title'
        assert metadata.channel == 'Unknown Channel'
        assert metadata.duration == 0
        assert metadata.thumbnail_url == ''
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info_returns_none_on_error(self, mock_ydl_class):
        """Test get_video_info returns None when video is not accessible."""
        # Mock yt-dlp to raise DownloadError
        mock_ydl = MagicMock()
        import yt_dlp
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Video unavailable")
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=notfound123"
        metadata = self.validator.get_video_info(url)
        
        assert metadata is None
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info_returns_none_when_no_info(self, mock_ydl_class):
        """Test get_video_info returns None when extract_info returns None."""
        # Mock yt-dlp to return None
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = None
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        
        url = "https://www.youtube.com/watch?v=test123"
        metadata = self.validator.get_video_info(url)
        
        assert metadata is None
