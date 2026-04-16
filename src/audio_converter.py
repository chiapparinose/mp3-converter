"""Audio conversion component using FFmpeg."""

import subprocess
import time
import re
import logging
import shutil
from pathlib import Path
from datetime import timedelta
from typing import Optional, Callable
from .models import ConversionResult


class AudioConverter:
    """Converts audio to MP3 format using FFmpeg."""
    
    MIN_BITRATE = 128
    MAX_BITRATE = 320
    DEFAULT_BITRATE = 192
    TIMEOUT_SECONDS = 300  # 5 minutes
    
    def __init__(self):
        """Initialize AudioConverter."""
        self._conversion_progress = 0.0
        self._duration = 0
        self.logger = logging.getLogger(__name__)
    
    def convert_to_mp3(
        self, 
        input_path: str, 
        output_path: str, 
        bitrate: int = 192,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> ConversionResult:
        """
        Convert audio file to MP3 format.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output MP3 file
            bitrate: Target bitrate in kbps (128-320)
            progress_callback: Optional callback for progress updates
            
        Returns:
            ConversionResult with conversion information
        """
        start_time = time.time()
        self._conversion_progress = 0.0
        
        # Clamp bitrate to valid range
        clamped_bitrate = self.clamp_bitrate(bitrate)
        
        # Check if FFmpeg is available
        if not shutil.which('ffmpeg'):
            self.logger.error("FFmpeg not found in PATH")
            return ConversionResult(
                success=False,
                mp3_file_path=None,
                bitrate=clamped_bitrate,
                file_size=0,
                conversion_time=time.time() - start_time
            )
        
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Get duration first for progress calculation
            self._get_duration(str(input_path))
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-vn',  # No video
                '-ar', '44100',  # Audio sample rate
                '-ac', '2',  # Stereo
                '-b:a', f'{clamped_bitrate}k',
                '-f', 'mp3',
                '-y',  # Overwrite
                str(output_path)
            ]
            
            self.logger.info(f"Running FFmpeg: {' '.join(cmd)}")
            
            # Run FFmpeg with timeout and progress tracking
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            try:
                # Read stderr in real-time for progress updates
                stderr_output = []
                last_update_time = time.time()
                
                while True:
                    # Check if process has finished
                    if process.poll() is not None:
                        # Read remaining output
                        remaining = process.stderr.read()
                        if remaining:
                            stderr_output.append(remaining)
                        break
                    
                    # Check for timeout
                    if time.time() - start_time > self.TIMEOUT_SECONDS:
                        process.kill()
                        self.logger.error("FFmpeg conversion timed out")
                        return ConversionResult(
                            success=False,
                            mp3_file_path=None,
                            bitrate=clamped_bitrate,
                            file_size=0,
                            conversion_time=time.time() - start_time
                        )
                    
                    # Read a line from stderr
                    line = process.stderr.readline()
                    if line:
                        stderr_output.append(line)
                        
                        # Parse progress from FFmpeg output
                        progress = self._parse_ffmpeg_progress(line)
                        if progress is not None and progress != self._conversion_progress:
                            self._conversion_progress = progress
                            
                            # Update callback at most once per second
                            current_time = time.time()
                            if progress_callback and (current_time - last_update_time >= 1.0):
                                progress_callback(progress)
                                last_update_time = current_time
                
                stderr = ''.join(stderr_output)
                
                if process.returncode == 0 and output_path.exists():
                    self._conversion_progress = 1.0
                    if progress_callback:
                        progress_callback(1.0)
                    
                    file_size = output_path.stat().st_size
                    conversion_time = time.time() - start_time
                    
                    return ConversionResult(
                        success=True,
                        mp3_file_path=output_path,
                        bitrate=clamped_bitrate,
                        file_size=file_size,
                        conversion_time=conversion_time
                    )
                else:
                    self.logger.error(f"FFmpeg failed: {stderr}")
                    return ConversionResult(
                        success=False,
                        mp3_file_path=None,
                        bitrate=clamped_bitrate,
                        file_size=0,
                        conversion_time=time.time() - start_time
                    )
                    
            except Exception as e:
                process.kill()
                self.logger.error(f"Error during FFmpeg execution: {e}")
                return ConversionResult(
                    success=False,
                    mp3_file_path=None,
                    bitrate=clamped_bitrate,
                    file_size=0,
                    conversion_time=time.time() - start_time
                )
                
        except Exception as e:
            self.logger.error(f"Conversion error: {e}")
            return ConversionResult(
                success=False,
                mp3_file_path=None,
                bitrate=clamped_bitrate,
                file_size=0,
                conversion_time=time.time() - start_time
            )
    
    def _get_duration(self, input_path: str) -> float:
        """Get duration of audio file in seconds."""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                input_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._duration = float(result.stdout.strip())
                return self._duration
        except Exception:
            pass
        return 0.0
    
    def _parse_ffmpeg_progress(self, line: str) -> Optional[float]:
        """
        Parse FFmpeg output line for progress information.
        
        FFmpeg outputs progress in the format: time=00:01:23.45
        
        Args:
            line: Line from FFmpeg stderr output
            
        Returns:
            Progress as float (0.0 to 1.0) or None if no progress found
        """
        if not self._duration or self._duration <= 0:
            return None
        
        # Look for time= pattern in FFmpeg output
        time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2))
            seconds = float(time_match.group(3))
            
            current_time = hours * 3600 + minutes * 60 + seconds
            progress = min(current_time / self._duration, 1.0)
            return progress
        
        return None
    
    def get_progress(self) -> float:
        """
        Get current conversion progress.
        
        Returns:
            Progress value (0.0 to 1.0)
        """
        return self._conversion_progress
    
    def estimate_completion_time(self) -> Optional[timedelta]:
        """
        Estimate time remaining for conversion.
        
        Returns:
            Estimated time remaining or None
        """
        if self._conversion_progress > 0 and self._duration > 0:
            # Rough estimate based on progress
            remaining_progress = 1.0 - self._conversion_progress
            estimated_seconds = remaining_progress * self._duration / 10  # Rough factor
            return timedelta(seconds=estimated_seconds)
        return None
    
    @classmethod
    def clamp_bitrate(cls, bitrate: int) -> int:
        """
        Clamp bitrate to valid range (128-320 kbps).
        
        Args:
            bitrate: Input bitrate
            
        Returns:
            Clamped bitrate
        """
        return max(cls.MIN_BITRATE, min(cls.MAX_BITRATE, bitrate))
