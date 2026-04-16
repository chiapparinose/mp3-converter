"""Integration tests for conversion pipeline."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.conversion_pipeline import ConversionPipeline
from src.models import MP3File, ErrorResponse, VideoMetadata


class TestConversionPipeline:
    """Tests for ConversionPipeline class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = ConversionPipeline(temp_dir="temp", output_dir="output")
    
    def test_initialization(self):
        """Test pipeline initialization."""
        assert self.pipeline.url_validator is not None
        assert self.pipeline.video_downloader is not None
        assert self.pipeline.audio_converter is not None
        assert self.pipeline.metadata_embedder is not None
        assert self.pipeline.file_manager is not None
        assert self.pipeline.error_handler is not None
        assert self.pipeline.progress_tracker is not None
    
    @patch('src.conversion_pipeline.VideoDownloader.get_video_info')
    @patch('src.conversion_pipeline.URLValidator.validate_format')
    def test_convert_invalid_url(self, mock_validate, mock_get_info):
        """Test conversion with invalid URL."""
        from src.models import ValidationResult
        
        mock_validate.return_value = ValidationResult(
            is_valid=False,
            video_metadata=None,
            error_message="Invalid URL format",
            validation_time=0.1
        )
        
        mp3_file, error = self.pipeline.convert("invalid_url")
        
        assert mp3_file is None
        assert error is not None
        assert error.success is False
    
    @patch('src.conversion_pipeline.VideoDownloader.get_video_info')
    @patch('src.conversion_pipeline.URLValidator.validate_format')
    def test_convert_valid_url_success(self, mock_validate, mock_get_info):
        """Test successful conversion with valid URL."""
        from src.models import ValidationResult, DownloadResult, ConversionResult
        
        # Mock validation
        mock_validate.return_value = ValidationResult(
            is_valid=True,
            video_metadata=None,
            error_message=None,
            validation_time=0.1
        )
        
        # Mock video info
        mock_get_info.return_value = VideoMetadata(
            video_id="test123",
            title="Test Video",
            channel="Test Channel",
            duration=300,
            thumbnail_url=""
        )
        
        # Mock download
        with patch.object(self.pipeline.video_downloader, 'download_audio') as mock_download:
            temp_file = Path("temp/test.webm")
            temp_file.parent.mkdir(exist_ok=True)
            temp_file.touch()
            
            mock_download.return_value = DownloadResult(
                success=True,
                audio_file_path=temp_file,
                format="webm",
                file_size=1000000,
                download_time=5.0
            )
            
            # Mock conversion
            with patch.object(self.pipeline.audio_converter, 'convert_to_mp3') as mock_convert:
                output_file = Path("output/test.mp3")
                output_file.parent.mkdir(exist_ok=True)
                output_file.touch()
                
                mock_convert.return_value = ConversionResult(
                    success=True,
                    mp3_file_path=output_file,
                    bitrate=192,
                    file_size=5000000,
                    conversion_time=10.0
                )
                
                # Mock metadata embedding
                with patch.object(self.pipeline.metadata_embedder, 'embed_metadata') as mock_embed:
                    mock_embed.return_value = True
                    
                    mp3_file, error = self.pipeline.convert("https://youtube.com/watch?v=test")
                    
                    # Should succeed
                    assert error is None or mp3_file is not None
    
    def test_progress_callback(self):
        """Test progress callback is called."""
        progress_updates = []
        
        def callback(stage, progress):
            progress_updates.append((stage, progress))
        
        # Progress callback should be callable
        self.pipeline.progress_tracker.subscribe(lambda u: None)


class TestConversionPipelineErrorHandling:
    """Tests for pipeline error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = ConversionPipeline(temp_dir="temp", output_dir="output")
    
    @patch('src.conversion_pipeline.VideoDownloader.get_video_info')
    @patch('src.conversion_pipeline.URLValidator.validate_format')
    def test_download_failure_handled(self, mock_validate, mock_get_info):
        """Test that download failure is handled properly."""
        from src.models import ValidationResult
        
        mock_validate.return_value = ValidationResult(
            is_valid=True,
            video_metadata=None,
            error_message=None,
            validation_time=0.1
        )
        
        mock_get_info.return_value = VideoMetadata(
            video_id="test",
            title="Test",
            channel="Test",
            duration=300,
            thumbnail_url=""
        )
        
        with patch.object(self.pipeline.video_downloader, 'download_audio') as mock_download:
            mock_download.return_value = MagicMock(
                success=False,
                audio_file_path=None
            )
            
            mp3_file, error = self.pipeline.convert("https://youtube.com/watch?v=test")
            
            assert mp3_file is None
            assert error is not None
    
    @patch('src.conversion_pipeline.VideoDownloader.get_video_info')
    @patch('src.conversion_pipeline.URLValidator.validate_format')
    def test_video_info_failure_handled(self, mock_validate, mock_get_info):
        """Test that video info failure is handled."""
        from src.models import ValidationResult
        
        mock_validate.return_value = ValidationResult(
            is_valid=True,
            video_metadata=None,
            error_message=None,
            validation_time=0.1
        )
        
        mock_get_info.return_value = None
        
        mp3_file, error = self.pipeline.convert("https://youtube.com/watch?v=test")
        
        assert mp3_file is None
        assert error is not None
