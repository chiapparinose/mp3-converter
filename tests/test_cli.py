"""Unit tests for CLI component."""

import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from src.cli import main, format_progress, run_conversion


class TestCLI:
    """Tests for CLI functions."""
    
    def test_format_progress_zero(self):
        """Test progress formatting at 0%."""
        result = format_progress("download", 0.0)
        assert "0.0%" in result
        assert "Download" in result
    
    def test_format_progress_half(self):
        """Test progress formatting at 50%."""
        result = format_progress("conversion", 0.5)
        assert "50.0%" in result
        assert "Conversion" in result
    
    def test_format_progress_complete(self):
        """Test progress formatting at 100%."""
        result = format_progress("validation", 1.0)
        assert "100.0%" in result
    
    def test_main_with_no_args(self):
        """Test main with no arguments shows help."""
        with pytest.raises(SystemExit):
            main([])
    
    def test_main_with_help(self):
        """Test main with --help."""
        with pytest.raises(SystemExit):
            main(["--help"])
    
    def test_main_with_version(self):
        """Test main with --version."""
        with pytest.raises(SystemExit):
            main(["--version"])
    
    @patch('src.cli.ConversionPipeline')
    def test_run_conversion_success(self, mock_pipeline_class):
        """Test successful conversion run."""
        mock_pipeline = MagicMock()
        mock_mp3 = MagicMock()
        mock_mp3.file_path = "/output/test.mp3"
        mock_mp3.file_size_mb = 5.0
        mock_mp3.duration = 300
        mock_mp3.bitrate = 192
        
        mock_pipeline.convert.return_value = (mock_mp3, None)
        mock_pipeline_class.return_value = mock_pipeline
        
        result = run_conversion(
            url="https://youtube.com/watch?v=test",
            bitrate=192,
            output_dir="output",
            no_metadata=False,
            verbose=False
        )
        
        assert result == 0
    
    @patch('src.cli.ConversionPipeline')
    def test_run_conversion_failure(self, mock_pipeline_class):
        """Test failed conversion run."""
        mock_pipeline = MagicMock()
        mock_error = MagicMock()
        mock_error.error_message = "Test error"
        
        mock_pipeline.convert.return_value = (None, mock_error)
        mock_pipeline_class.return_value = mock_pipeline
        
        result = run_conversion(
            url="https://youtube.com/watch?v=test",
            bitrate=192,
            output_dir="output",
            no_metadata=False,
            verbose=False
        )
        
        assert result == 1


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""
    
    def test_parse_url_only(self):
        """Test parsing with URL only."""
        with patch('src.cli.run_conversion') as mock_run:
            mock_run.return_value = 0
            with pytest.raises(SystemExit):
                main(["https://youtube.com/watch?v=test"])
    
    def test_parse_with_bitrate(self):
        """Test parsing with bitrate option."""
        with patch('src.cli.run_conversion') as mock_run:
            mock_run.return_value = 0
            with pytest.raises(SystemExit):
                main(["https://youtube.com/watch?v=test", "--bitrate", "320"])
    
    def test_parse_with_output_dir(self):
        """Test parsing with output directory."""
        with patch('src.cli.run_conversion') as mock_run:
            mock_run.return_value = 0
            with pytest.raises(SystemExit):
                main(["https://youtube.com/watch?v=test", "-o", "/music"])
    
    def test_parse_with_verbose(self):
        """Test parsing with verbose flag."""
        with patch('src.cli.run_conversion') as mock_run:
            mock_run.return_value = 0
            with pytest.raises(SystemExit):
                main(["https://youtube.com/watch?v=test", "-v"])
    
    def test_parse_with_no_metadata(self):
        """Test parsing with no-metadata flag."""
        with patch('src.cli.run_conversion') as mock_run:
            mock_run.return_value = 0
            with pytest.raises(SystemExit):
                main(["https://youtube.com/watch?v=test", "--no-metadata"])
    
    def test_parse_invalid_bitrate(self):
        """Test parsing with invalid bitrate."""
        with pytest.raises(SystemExit):
            main(["https://youtube.com/watch?v=test", "--bitrate", "500"])
