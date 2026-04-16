#!/usr/bin/env python3
"""
System Test Script - Verify all components work correctly
"""

import sys
from pathlib import Path

def test_imports():
    """Test all imports work correctly."""
    print("Testing imports...")
    try:
        from src.models import Stage, VideoMetadata, ValidationResult
        from src.url_validator import URLValidator
        from src.video_downloader import VideoDownloader
        from src.audio_converter import AudioConverter
        from src.metadata_embedder import MetadataEmbedder
        from src.file_manager import FileManager
        from src.error_handler import ErrorHandler
        from src.progress_tracker import ProgressTracker
        from src.conversion_pipeline import ConversionPipeline
        from src.cli import main
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_url_validation():
    """Test URL validation."""
    print("\nTesting URL validation...")
    from src.url_validator import URLValidator
    
    validator = URLValidator()
    
    # Test valid URLs
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    
    for url in valid_urls:
        result = validator.validate_format(url)
        if not result.is_valid:
            print(f"✗ Valid URL rejected: {url}")
            return False
    
    # Test invalid URLs
    invalid_urls = [
        "invalid-url",
        "https://example.com/video",
        "https://www.youtube.com/watch",
    ]
    
    for url in invalid_urls:
        result = validator.validate_format(url)
        if result.is_valid:
            print(f"✗ Invalid URL accepted: {url}")
            return False
    
    print("✓ URL validation working correctly")
    return True

def test_filename_sanitization():
    """Test filename sanitization."""
    print("\nTesting filename sanitization...")
    from src.file_manager import FileManager
    
    test_cases = [
        ("Test<>Video:Name", "TestVideoName"),
        ("File/Path\\Test", "FilePathTest"),
        ("Question?Mark*", "QuestionMark"),
        ("Normal_File-123.mp3", "Normal_File-123.mp3"),
    ]
    
    for input_name, expected in test_cases:
        result = FileManager.sanitize_filename(input_name)
        if result != expected:
            print(f"✗ Sanitization failed: '{input_name}' -> '{result}' (expected '{expected}')")
            return False
    
    print("✓ Filename sanitization working correctly")
    return True

def test_bitrate_clamping():
    """Test bitrate clamping."""
    print("\nTesting bitrate clamping...")
    from src.audio_converter import AudioConverter
    
    test_cases = [
        (100, 128),  # Below minimum
        (192, 192),  # Within range
        (500, 320),  # Above maximum
    ]
    
    for input_bitrate, expected in test_cases:
        result = AudioConverter.clamp_bitrate(input_bitrate)
        if result != expected:
            print(f"✗ Bitrate clamping failed: {input_bitrate} -> {result} (expected {expected})")
            return False
    
    print("✓ Bitrate clamping working correctly")
    return True

def test_progress_tracking():
    """Test progress tracking."""
    print("\nTesting progress tracking...")
    from src.progress_tracker import ProgressTracker
    from src.models import Stage
    
    tracker = ProgressTracker()
    
    # Test stage updates
    tracker.update_stage(Stage.VALIDATION, 1.0)
    tracker.update_stage(Stage.DOWNLOAD, 0.5)
    
    overall = tracker.get_overall_progress()
    expected = 0.05 + (0.5 * 0.5)  # 5% validation + 25% download
    
    if abs(overall - expected) > 0.01:
        print(f"✗ Progress calculation failed: {overall} (expected {expected})")
        return False
    
    print("✓ Progress tracking working correctly")
    return True

def test_error_handling():
    """Test error handling."""
    print("\nTesting error handling...")
    from src.error_handler import ErrorHandler, InvalidURLFormatError
    from src.models import ErrorContext, Stage
    from datetime import datetime
    
    handler = ErrorHandler()
    
    # Test custom error
    error = InvalidURLFormatError("Test error")
    context = ErrorContext(
        stage=Stage.VALIDATION,
        operation="test",
        timestamp=datetime.now()
    )
    
    response = handler.handle_error(error, context)
    
    if not response.error_message:
        print("✗ Error handling failed: No error message")
        return False
    
    if response.success:
        print("✗ Error handling failed: Success should be False")
        return False
    
    print("✓ Error handling working correctly")
    return True

def test_storage_management():
    """Test storage management."""
    print("\nTesting storage management...")
    from src.file_manager import FileManager
    import tempfile
    import shutil
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        manager = FileManager(temp_dir)
        
        # Test file creation
        file1 = manager.create_temp_file("test")
        if not file1.exists():
            print("✗ File creation failed")
            return False
        
        # Test storage usage
        file1.write_bytes(b"test data")
        usage = manager.get_storage_usage()
        if usage != 9:  # "test data" is 9 bytes
            print(f"✗ Storage usage calculation failed: {usage} (expected 9)")
            return False
        
        print("✓ Storage management working correctly")
        return True
    finally:
        shutil.rmtree(temp_dir)

def test_ffmpeg_availability():
    """Test FFmpeg availability."""
    print("\nTesting FFmpeg availability...")
    import shutil
    
    if not shutil.which('ffmpeg'):
        print("✗ FFmpeg not found in PATH")
        return False
    
    print("✓ FFmpeg is available")
    return True

def test_dependencies():
    """Test all dependencies are installed."""
    print("\nTesting dependencies...")
    
    try:
        import yt_dlp
        import mutagen
        import hypothesis
        print("✓ All dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("YouTube to MP3 Converter - System Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_dependencies,
        test_ffmpeg_availability,
        test_url_validation,
        test_filename_sanitization,
        test_bitrate_clamping,
        test_progress_tracking,
        test_error_handling,
        test_storage_management,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All tests passed! System is ready to use.")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed. Please fix the issues.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
