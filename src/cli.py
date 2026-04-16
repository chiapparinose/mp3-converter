"""Command-line interface for YouTube to MP3 Converter."""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional
from .conversion_pipeline import ConversionPipeline


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(levelname)s] %(message)s'
    )


def format_progress(stage: str, progress: float) -> str:
    """Format progress for display."""
    bar_length = 30
    filled = int(bar_length * progress)
    bar = '█' * filled + '░' * (bar_length - filled)
    return f"[{bar}] {stage.capitalize()}: {progress * 100:.1f}%"


def run_conversion(url: str, bitrate: int, output_dir: str, no_metadata: bool, verbose: bool) -> int:
    """
    Run the conversion process.
    
    Args:
        url: YouTube video URL
        bitrate: Target bitrate in kbps
        output_dir: Output directory
        no_metadata: Skip metadata embedding
        verbose: Enable verbose output
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    pipeline = ConversionPipeline(output_dir=output_dir)
    
    def progress_callback(stage: str, progress: float):
        print(f"\r{format_progress(stage, progress)}", end='', flush=True)
    
    print(f"Converting: {url}")
    print(f"Output directory: {output_dir}")
    print(f"Bitrate: {bitrate} kbps")
    print()
    
    mp3_file, error = pipeline.convert(url, bitrate, progress_callback)
    
    print()  # New line after progress
    
    if mp3_file:
        print(f"\n✓ Conversion complete!")
        print(f"  File: {mp3_file.file_path}")
        print(f"  Size: {mp3_file.file_size_mb:.2f} MB")
        print(f"  Duration: {mp3_file.duration // 60}:{mp3_file.duration % 60:02d}")
        print(f"  Bitrate: {mp3_file.bitrate} kbps")
        return 0
    else:
        print(f"\n✗ Conversion failed: {error.error_message if error else 'Unknown error'}")
        return 1


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for CLI.
    
    Args:
        args: Command-line arguments (defaults to sys.argv)
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description='Convert YouTube videos to MP3 audio files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s "https://youtu.be/dQw4w9WgXcQ" --bitrate 320
  %(prog)s "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o ./music
        '''
    )
    
    parser.add_argument(
        'url',
        help='YouTube video URL to convert'
    )
    
    parser.add_argument(
        '-b', '--bitrate',
        type=int,
        default=192,
        choices=range(128, 321),
        metavar='128-320',
        help='MP3 bitrate in kbps (default: 192, range: 128-320)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default='output',
        help='Output directory for MP3 files (default: output)'
    )
    
    parser.add_argument(
        '--no-metadata',
        action='store_true',
        help='Skip embedding metadata into MP3 file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    parsed_args = parser.parse_args(args)
    
    return run_conversion(
        url=parsed_args.url,
        bitrate=parsed_args.bitrate,
        output_dir=parsed_args.output_dir,
        no_metadata=parsed_args.no_metadata,
        verbose=parsed_args.verbose
    )


if __name__ == '__main__':
    sys.exit(main())
