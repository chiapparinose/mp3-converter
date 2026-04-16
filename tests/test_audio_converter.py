"""Unit tests for AudioConverter component."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.audio_converter import AudioConverter
from src.models import ConversionResult


class TestAudioConverter:
    """Tests for AudioConverter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.converter = AudioConverter()
    
    def test_initial_state(self):
        """Test initial state of audio converter."""
        assert self.converter.get_progress() == 0.0
    
    def test_clamp_bitrate_minimum(self):
        """Test bitrate clamping to minimum."""
        result = AudioConverter.clamp_bitrate(50)
        assert result == 128
    
    def test_clamp_bitrate_maximum(self):
        """Test bitrate clamping to maximum."""
        result = AudioConverter.clamp_bitrate(500)
        assert result == 320
    
    def test_clamp_bitrate_valid_range(self):
        """Test bitrate within valid range."""
        result = AudioConverter.clamp_bitrate(192)
        assert result == 192
    
    def test_clamp_bitrate_exactly_minimum(self):
        """Test bitrate at exactly minimum."""
        result = AudioConverter.clamp_bitrate(128)
        assert result == 128
    
    def test_clamp_bitrate_exactly_maximum(self):
        """Test bitrate at exactly maximum."""
        result = AudioConverter.clamp_bitrate(320)
        assert result == 320
    
    @pytest.mark.parametrize("input_bitrate,expected", [
        (0, 128),
        (50, 128),
        (100, 128),
        (127, 128),
        (128, 128),
        (192, 192),
        (256, 256),
        (320, 320),
        (321, 320),
        (500, 320),
        (1000, 320),
    ])
    def test_clamp_bitrate_various_values(self, input_bitrate, expected):
        """Test bitrate clamping with various values."""
        result = AudioConverter.clamp_bitrate(input_bitrate)
        assert result == expected
    
    @patch('src.audio_converter.shutil.which')
    def test_convert_ffmpeg_not_found(self, mock_which):
        """Test conversion when FFmpeg is not installed."""
        mock_which.return_value = None
        
        result = self.converter.convert_to_mp3("input.webm", "output.mp3", 192)
        
        assert result.success is False
        assert result.mp3_file_path is None
    
    @patch('src.audio_converter.subprocess.run')
    @patch('src.audio_converter.shutil.which')
    @patch('src.audio_converter.subprocess.Popen')
    def test_convert_success(self, mock_popen, mock_which, mock_run):
        """Test successful conversion."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        # Mock ffprobe for duration
        mock_run.return_value = MagicMock(returncode=0, stdout="300.0")
        
        # Mock ffmpeg process
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Create mock output file
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'stat') as mock_stat:
                mock_stat.return_value = MagicMock(st_size=5000000)
                
                result = self.converter.convert_to_mp3("input.webm", "output.mp3", 192)
        
        assert result.success is True
        assert result.bitrate == 192
    
    def test_get_progress(self):
        """Test getting conversion progress."""
        self.converter._conversion_progress = 0.5
        assert self.converter.get_progress() == 0.5
    
    def test_estimate_completion_time_no_progress(self):
        """Test time estimation with no progress."""
        result = self.converter.estimate_completion_time()
        assert result is None


class TestAudioConverterBitrateRange:
    """Tests for bitrate range enforcement."""
    
    @pytest.mark.parametrize("bitrate", [128, 160, 192, 224, 256, 320])
    def test_valid_bitrates_accepted(self, bitrate):
        """Test that valid bitrates are accepted."""
        result = AudioConverter.clamp_bitrate(bitrate)
        assert result == bitrate
    
    def test_bitrate_below_minimum_clamped(self):
        """Test bitrate below minimum is clamped."""
        for bitrate in [0, 50, 100, 127]:
            result = AudioConverter.clamp_bitrate(bitrate)
            assert result == 128
    
    def test_bitrate_above_maximum_clamped(self):
        """Test bitrate above maximum is clamped."""
        for bitrate in [321, 400, 500, 1000]:
            result = AudioConverter.clamp_bitrate(bitrate)
            assert result == 320
