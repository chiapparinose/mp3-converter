"""Main conversion pipeline orchestrator."""

import logging
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
from .models import MP3File, ErrorResponse, ErrorContext, Stage, VideoMetadata
from .url_validator import URLValidator
from .video_downloader import VideoDownloader
from .audio_converter import AudioConverter
from .metadata_embedder import MetadataEmbedder
from .file_manager import FileManager
from .error_handler import ErrorHandler, DownloadFailedError, ConversionTimeoutError
from .progress_tracker import ProgressTracker


class ConversionPipeline:
    """Orchestrates the complete YouTube to MP3 conversion process."""
    
    def __init__(
        self, 
        temp_dir: str = "temp", 
        output_dir: str = "output",
        downloader: Optional[VideoDownloader] = None
    ):
        """
        Initialize ConversionPipeline.
        
        Args:
            temp_dir: Directory for temporary files
            output_dir: Directory for output MP3 files
            downloader: Optional custom VideoDownloader instance (for rate limiting bypass)
        """
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.url_validator = URLValidator()
        self.video_downloader = downloader or VideoDownloader(temp_dir)
        self.audio_converter = AudioConverter()
        self.metadata_embedder = MetadataEmbedder()
        self.file_manager = FileManager(temp_dir)
        self.error_handler = ErrorHandler()
        self.progress_tracker = ProgressTracker()
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        Path(output_dir).mkdir(exist_ok=True)
    
    def convert(self, url: str, bitrate: int = 192, progress_callback: Optional[Callable[[str, float], None]] = None) -> tuple[Optional[MP3File], Optional[ErrorResponse]]:
        """
        Convert YouTube video to MP3.
        
        Args:
            url: YouTube video URL
            bitrate: Target MP3 bitrate in kbps
            progress_callback: Optional callback(stage_name, progress)
            
        Returns:
            Tuple of (MP3File, ErrorResponse) - one will be None
        """
        self.progress_tracker.reset()
        temp_files = []
        
        try:
            # Stage 1: Validation
            self.progress_tracker.update_stage(Stage.VALIDATION, 0.0)
            if progress_callback:
                progress_callback("validation", 0.0)
            
            validation_result = self.url_validator.validate_format(url)
            if not validation_result.is_valid:
                error_context = ErrorContext(
                    stage=Stage.VALIDATION,
                    operation="validate_url",
                    timestamp=datetime.now()
                )
                return None, self.error_handler.handle_error(
                    Exception(validation_result.error_message or "Invalid URL"),
                    error_context
                )
            
            self.progress_tracker.update_stage(Stage.VALIDATION, 1.0)
            if progress_callback:
                progress_callback("validation", 1.0)
            
            # Get video info
            video_info = self.video_downloader.get_video_info(url)
            if not video_info:
                error_context = ErrorContext(
                    stage=Stage.VALIDATION,
                    operation="get_video_info",
                    timestamp=datetime.now()
                )
                return None, self.error_handler.handle_error(
                    Exception("Could not retrieve video information"),
                    error_context
                )
            
            # Check duration warning
            if VideoDownloader.check_duration_warning(video_info.duration):
                self.logger.warning(f"Video duration ({video_info.duration}s) exceeds 2 hours")
            
            # Stage 2: Download
            self.progress_tracker.update_stage(Stage.DOWNLOAD, 0.0)
            if progress_callback:
                progress_callback("download", 0.0)
            
            def download_progress(p):
                self.progress_tracker.update_stage(Stage.DOWNLOAD, p)
                if progress_callback:
                    progress_callback("download", p)
            
            download_result = self.video_downloader.download_audio(url, str(self.temp_dir), download_progress)
            
            if not download_result.success or not download_result.audio_file_path:
                error_context = ErrorContext(
                    stage=Stage.DOWNLOAD,
                    operation="download_audio",
                    timestamp=datetime.now()
                )
                return None, self.error_handler.handle_error(
                    DownloadFailedError("Download failed after retries"),
                    error_context
                )
            
            temp_files.append(download_result.audio_file_path)
            self.progress_tracker.update_stage(Stage.DOWNLOAD, 1.0)
            if progress_callback:
                progress_callback("download", 1.0)
            
            # Stage 3: Conversion
            self.progress_tracker.update_stage(Stage.CONVERSION, 0.0)
            if progress_callback:
                progress_callback("conversion", 0.0)
            
            # Generate output filename
            sanitized_title = self.file_manager.sanitize_filename(video_info.title)
            output_filename = f"{sanitized_title}.mp3"
            output_path = Path(self.output_dir) / output_filename
            
            def conversion_progress(p):
                self.progress_tracker.update_stage(Stage.CONVERSION, p)
                if progress_callback:
                    progress_callback("conversion", p)
            
            conversion_result = self.audio_converter.convert_to_mp3(
                str(download_result.audio_file_path),
                str(output_path),
                bitrate,
                conversion_progress
            )
            
            if not conversion_result.success or not conversion_result.mp3_file_path:
                error_context = ErrorContext(
                    stage=Stage.CONVERSION,
                    operation="convert_to_mp3",
                    timestamp=datetime.now()
                )
                return None, self.error_handler.handle_error(
                    ConversionTimeoutError("Conversion failed"),
                    error_context
                )
            
            self.progress_tracker.update_stage(Stage.CONVERSION, 1.0)
            if progress_callback:
                progress_callback("conversion", 1.0)
            
            # Stage 4: Metadata
            self.progress_tracker.update_stage(Stage.METADATA, 0.0)
            if progress_callback:
                progress_callback("metadata", 0.0)
            
            self.metadata_embedder.embed_metadata(str(output_path), video_info)
            
            self.progress_tracker.update_stage(Stage.METADATA, 1.0)
            if progress_callback:
                progress_callback("metadata", 1.0)
            
            # Stage 5: Delivery
            self.progress_tracker.update_stage(Stage.DELIVERY, 0.0)
            if progress_callback:
                progress_callback("delivery", 0.0)
            
            # Get final file info
            final_size = output_path.stat().st_size
            file_size_mb = final_size / (1024 * 1024)
            
            mp3_file = MP3File(
                file_path=output_path,
                file_size=final_size,
                file_size_mb=file_size_mb,
                filename=output_filename,
                bitrate=conversion_result.bitrate,
                duration=video_info.duration,
                metadata=video_info
            )
            
            self.progress_tracker.update_stage(Stage.DELIVERY, 1.0)
            if progress_callback:
                progress_callback("delivery", 1.0)
            
            # Ensure progress reaches 100% on successful completion
            overall_progress = self.progress_tracker.get_overall_progress()
            if overall_progress < 1.0:
                self.logger.warning(f"Progress not at 100% ({overall_progress * 100:.1f}%), forcing to 100%")
                self.progress_tracker.update_stage(Stage.DELIVERY, 1.0)
            
            # Schedule cleanup on success (60-second delay)
            for temp_file in temp_files:
                self.file_manager.cleanup_file(temp_file, delay_seconds=60)
            
            self.logger.info(f"Conversion completed successfully: {output_filename}")
            return mp3_file, None
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            error_context = ErrorContext(
                stage=self.progress_tracker.get_current_stage(),
                operation="convert",
                timestamp=datetime.now()
            )
            
            # Cleanup on failure (immediate - 0 second delay)
            for temp_file in temp_files:
                self.file_manager.cleanup_file(temp_file, delay_seconds=0)
            
            return None, self.error_handler.handle_error(e, error_context)
