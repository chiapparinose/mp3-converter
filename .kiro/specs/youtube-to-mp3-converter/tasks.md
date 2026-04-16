# Implementation Plan: YouTube to MP3 Converter

## Overview

This implementation plan breaks down the YouTube to MP3 Converter into discrete coding tasks following the pipeline architecture: URL validation → video download → audio conversion → metadata embedding → file delivery → cleanup. The system uses Python with yt-dlp, FFmpeg, mutagen, and Hypothesis for property-based testing.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create Python project structure with appropriate directories (src, tests, temp)
  - Create requirements.txt with dependencies: yt-dlp>=2024.1.0, mutagen>=1.47.0, hypothesis>=6.90.0
  - Set up pytest configuration for unit and property-based tests
  - Create main package structure with component modules
  - _Requirements: All requirements (foundation)_

- [x] 2. Implement data models and core types
  - [x] 2.1 Create data model classes
    - Implement VideoMetadata, ValidationResult, DownloadResult, ConversionResult, MP3File dataclasses
    - Implement ProgressUpdate, ErrorResponse, ErrorContext dataclasses
    - Define Stage enum for pipeline stages
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1_
  
  - [x] 2.2 Write property test for file size calculation
    - **Property 8: File Size Calculation Accuracy**
    - **Validates: Requirements 6.3**
  
  - [x] 2.3 Write unit tests for data models
    - Test dataclass initialization and field validation
    - Test enum values for Stage
    - _Requirements: All requirements (foundation)_

- [x] 3. Implement URLValidator component
  - [x] 3.1 Create URLValidator class with format validation
    - Implement validate_format() method with regex patterns for YouTube URLs
    - Support watch, shorts, embed, and mobile URL formats
    - Enforce 2-second timeout for validation operations
    - _Requirements: 1.1, 1.4_
  
  - [x] 3.2 Write property test for URL format validation
    - **Property 1: URL Format Validation**
    - **Validates: Requirements 1.1, 1.4**
  
  - [x] 3.3 Implement video accessibility checking
    - Implement check_video_exists() using yt-dlp extract_info with download=False
    - Distinguish between non-existent, private, age-restricted, and available videos
    - Implement get_video_info() to extract VideoMetadata
    - _Requirements: 1.2, 1.3_
  
  - [x] 3.4 Write unit tests for URLValidator
    - Test valid YouTube URL formats (watch, shorts, embed, mobile)
    - Test invalid URL formats
    - Test timeout enforcement
    - Mock yt-dlp responses for video accessibility scenarios
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 4. Implement FileManager component
  - [x] 4.1 Create FileManager class with file operations
    - Implement create_temp_file() for unique temporary file creation
    - Implement sanitize_filename() to remove invalid characters (< > : " / \ | ? *)
    - Implement get_storage_usage() to monitor temporary directory size
    - _Requirements: 6.2, 8.3_
  
  - [ ] 4.2 Write property test for filename sanitization
    - **Property 7: Filename Sanitization**
    - **Validates: Requirements 6.2**
  
  - [x] 4.3 Implement storage management and cleanup
    - Implement cleanup_file() with delayed execution (60 seconds default)
    - Implement cleanup_old_files() to delete oldest files when storage exceeds 4 GB
    - Enforce 5 GB storage limit
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 4.4 Write property test for storage limit enforcement
    - **Property 10: Storage Limit Enforcement**
    - **Validates: Requirements 8.3**
  
  - [ ] 4.5 Write property test for cleanup prioritization
    - **Property 11: Cleanup Prioritization by Age**
    - **Validates: Requirements 8.4**
  
  - [ ] 4.6 Write unit tests for FileManager
    - Test temporary file creation with unique IDs
    - Test filename sanitization with various invalid characters
    - Test storage usage calculation
    - Test cleanup scheduling and execution
    - _Requirements: 6.2, 8.1, 8.2, 8.3, 8.4_

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement ErrorHandler component
  - [x] 6.1 Create ErrorHandler class with error categorization
    - Implement handle_error() to map exceptions to ErrorResponse
    - Implement get_user_message() for user-friendly error messages
    - Implement log_error() for detailed error logging
    - Define custom exception classes for each error category
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [ ] 6.2 Write property test for error message descriptiveness
    - **Property 9: Error Message Descriptiveness**
    - **Validates: Requirements 7.1, 7.3, 7.4**
  
  - [ ] 6.3 Write unit tests for ErrorHandler
    - Test error message mapping for each error category
    - Test error logging with context information
    - Test sanitization of sensitive information in error messages
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 7. Implement ProgressTracker component
  - [x] 7.1 Create ProgressTracker class with stage tracking
    - Implement update_stage() for thread-safe progress updates
    - Implement get_overall_progress() with weighted calculation (validation 5%, download 50%, conversion 35%, metadata 5%, delivery 5%)
    - Implement get_current_stage() to return active pipeline stage
    - Implement subscribe() for progress update callbacks
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ] 7.2 Write property test for progress monotonicity
    - **Property 6: Progress Tracking Monotonicity**
    - **Validates: Requirements 5.1, 5.2, 5.4**
  
  - [ ] 7.3 Write unit tests for ProgressTracker
    - Test progress updates across all stages
    - Test weighted overall progress calculation
    - Test update frequency (at least once per second)
    - Test thread-safety with concurrent updates
    - Test subscriber notification mechanism
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 8. Implement VideoDownloader component
  - [x] 8.1 Create VideoDownloader class with yt-dlp integration
    - Implement download_audio() with yt-dlp configuration (bestaudio/best format)
    - Configure yt-dlp options: format, output template, progress hooks
    - Implement get_progress() to report download progress
    - Implement cancel_download() for cancellation support
    - _Requirements: 2.1, 2.2_
  
  - [x] 8.2 Implement retry logic and duration warnings
    - Add retry logic with up to 3 attempts for network failures
    - Implement duration check to warn for videos exceeding 2 hours (7200 seconds)
    - Integrate with ProgressTracker for download progress reporting
    - _Requirements: 2.3, 2.4_
  
  - [ ] 8.3 Write property test for duration warning logic
    - **Property 2: Duration Warning Logic**
    - **Validates: Requirements 2.3**
  
  - [ ] 8.4 Write property test for retry logic
    - **Property 3: Retry Logic on Network Failure**
    - **Validates: Requirements 2.4**
  
  - [ ] 8.5 Write unit tests for VideoDownloader
    - Test successful download with progress tracking
    - Test network failure and retry logic (mock network errors)
    - Test duration warning for long videos
    - Test unsupported format handling
    - Test cancellation during download
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 9. Implement AudioConverter component
  - [x] 9.1 Create AudioConverter class with FFmpeg integration
    - Implement convert_to_mp3() using FFmpeg subprocess
    - Configure FFmpeg command: -vn -ar 44100 -ac 2 -b:a {bitrate}k -f mp3
    - Support bitrate range 128-320 kbps with default 192 kbps
    - Implement get_progress() by parsing FFmpeg output
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 9.2 Implement conversion timeout and progress tracking
    - Enforce 5-minute timeout for videos up to 1 hour duration
    - Parse FFmpeg output for time position to calculate progress percentage
    - Update progress at least once per second
    - Integrate with ProgressTracker for conversion progress reporting
    - _Requirements: 3.4, 5.2, 5.3_
  
  - [ ] 9.3 Write property test for bitrate range enforcement
    - **Property 4: Bitrate Range Enforcement**
    - **Validates: Requirements 3.2**
  
  - [ ] 9.4 Write unit tests for AudioConverter
    - Test MP3 encoding with various bitrates (128, 192, 256, 320 kbps)
    - Test conversion timeout enforcement
    - Test FFmpeg error handling (FFmpeg not found, corrupted audio)
    - Test progress calculation from FFmpeg output
    - Mock FFmpeg subprocess for testing
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement MetadataEmbedder component
  - [x] 11.1 Create MetadataEmbedder class with mutagen integration
    - Implement embed_metadata() to write ID3v2.4 tags using mutagen
    - Map video title to TIT2, channel name to TPE1, duration to TLEN
    - Implement download_thumbnail() to fetch thumbnail image
    - Implement embed_artwork() to embed thumbnail as APIC (JPEG format)
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 11.2 Implement graceful metadata handling
    - Handle missing metadata fields gracefully (skip unavailable fields)
    - Sanitize metadata strings for ID3 compatibility
    - Continue MP3 creation even when thumbnail download fails
    - _Requirements: 4.4_
  
  - [ ] 11.3 Write property test for metadata embedding completeness
    - **Property 5: Metadata Embedding Completeness**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
  
  - [ ] 11.4 Write unit tests for MetadataEmbedder
    - Test complete metadata embedding with all fields
    - Test partial metadata handling (missing title, channel, or thumbnail)
    - Test thumbnail download and embedding
    - Test ID3 tag format validation
    - Test metadata sanitization for invalid characters
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 12. Implement main conversion pipeline
  - [x] 12.1 Create ConversionPipeline orchestrator class
    - Implement convert() method that orchestrates all pipeline stages
    - Wire together: URLValidator → VideoDownloader → AudioConverter → MetadataEmbedder
    - Integrate ProgressTracker for overall progress reporting
    - Integrate ErrorHandler for error handling at each stage
    - Integrate FileManager for temporary file management
    - _Requirements: All requirements (integration)_
  
  - [x] 12.2 Implement pipeline error handling and cleanup
    - Handle errors at each stage and propagate to ErrorHandler
    - Trigger FileManager cleanup on success (60-second delay)
    - Trigger FileManager cleanup on failure (immediate)
    - Ensure progress reaches 100% on successful completion
    - _Requirements: 5.4, 6.1, 7.1, 8.1, 8.2_
  
  - [ ] 12.3 Write integration tests for conversion pipeline
    - Test complete conversion flow with valid URL
    - Test error scenarios (invalid URL, non-existent video, network failure)
    - Test progress tracking across all stages
    - Test resource cleanup after success and failure
    - Test timeout handling at each stage
    - Mock external dependencies (yt-dlp, FFmpeg) for integration tests
    - _Requirements: All requirements (end-to-end)_

- [ ] 13. Create command-line interface
  - [x] 13.1 Implement CLI with argument parsing
    - Create main entry point with argparse for URL input
    - Add optional arguments: --bitrate, --output-dir, --no-metadata
    - Implement progress display in terminal (percentage and stage)
    - Display final MP3 file information (filename, size, duration)
    - _Requirements: 5.1, 5.2, 6.1, 6.3_
  
  - [x] 13.2 Implement CLI error handling and user feedback
    - Display user-friendly error messages from ErrorHandler
    - Show conversion progress updates in real-time
    - Provide clear success message with file location
    - _Requirements: 5.3, 7.1_
  
  - [ ] 13.3 Write unit tests for CLI
    - Test argument parsing with various inputs
    - Test progress display formatting
    - Test error message display
    - Mock ConversionPipeline for CLI testing
    - _Requirements: 5.1, 5.2, 5.3, 6.1, 6.3, 7.1_

- [ ] 14. Final checkpoint - Ensure all tests pass and system is ready
  - Run complete test suite (unit tests and property-based tests)
  - Verify FFmpeg is installed and accessible
  - Test end-to-end conversion with real YouTube URL
  - Verify temporary file cleanup works correctly
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests use Hypothesis with minimum 100 iterations per property
- Unit tests mock external dependencies (yt-dlp, FFmpeg, mutagen) for isolation
- Integration tests verify end-to-end functionality with mocked external services
- Checkpoints ensure incremental validation at key milestones
- The system requires FFmpeg to be installed and available in PATH
- Temporary storage requires minimum 5 GB free disk space
