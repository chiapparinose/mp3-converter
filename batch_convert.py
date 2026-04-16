#!/usr/bin/env python3
"""
Safe Batch Converter with Rate Limiting

Converts multiple YouTube videos to MP3 with built-in rate limiting protection.
"""

import sys
import time
import argparse
from pathlib import Path
from src.conversion_pipeline import ConversionPipeline

def safe_batch_convert(urls, bitrate=192, output_dir='output', delay=2, batch_size=15, break_time=300, verbose=False):
    """
    Safely convert multiple videos with rate limiting.
    
    Args:
        urls: List of YouTube URLs
        bitrate: MP3 bitrate (128-320 kbps)
        output_dir: Output directory
        delay: Delay between videos (seconds)
        batch_size: Videos per batch before break
        break_time: Break duration between batches (seconds)
        verbose: Enable verbose output
    
    Returns:
        List of results with success/failure status
    """
    pipeline = ConversionPipeline(output_dir=output_dir)
    results = []
    
    print("=" * 70)
    print("Safe Batch Converter with Rate Limiting")
    print("=" * 70)
    print(f"Total videos: {len(urls)}")
    print(f"Bitrate: {bitrate} kbps")
    print(f"Output directory: {output_dir}")
    print(f"Delay between videos: {delay}s")
    print(f"Batch size: {batch_size} videos")
    print(f"Break between batches: {break_time}s ({break_time // 60} minutes)")
    print("=" * 70)
    print()
    
    start_time = time.time()
    
    for i, url in enumerate(urls):
        video_num = i + 1
        print(f"[{video_num}/{len(urls)}] Converting: {url}")
        
        try:
            # Progress callback
            def progress_callback(stage, progress):
                if verbose:
                    print(f"  {stage}: {progress * 100:.0f}%", end='\r')
            
            mp3_file, error = pipeline.convert(url, bitrate, progress_callback if verbose else None)
            
            if mp3_file:
                results.append({
                    'url': url,
                    'success': True,
                    'file': mp3_file.filename,
                    'size': f"{mp3_file.file_size_mb:.2f} MB",
                    'duration': f"{mp3_file.duration // 60}:{mp3_file.duration % 60:02d}"
                })
                print(f"✓ Success: {mp3_file.filename} ({mp3_file.file_size_mb:.2f} MB)")
            else:
                error_msg = error.error_message if error else 'Unknown error'
                results.append({
                    'url': url,
                    'success': False,
                    'error': error_msg
                })
                print(f"✗ Failed: {error_msg}")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Conversion interrupted by user")
            break
        
        except Exception as e:
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })
            print(f"✗ Error: {e}")
        
        # Rate limiting logic
        if video_num < len(urls):  # Not last video
            if video_num % batch_size == 0:
                # Batch complete - take longer break
                successful_in_batch = sum(1 for r in results[-batch_size:] if r['success'])
                print(f"\n{'='*70}")
                print(f"Batch {video_num // batch_size} complete: {successful_in_batch}/{batch_size} successful")
                print(f"⏸️  Taking {break_time}s ({break_time // 60} minute) break to avoid rate limiting...")
                print(f"{'='*70}\n")
                
                # Countdown timer
                for remaining in range(break_time, 0, -30):
                    print(f"Resuming in {remaining}s...", end='\r')
                    time.sleep(min(30, remaining))
                print(" " * 50, end='\r')  # Clear line
            else:
                # Normal delay between videos
                print(f"⏳ Waiting {delay}s before next video...\n")
                time.sleep(delay)
    
    total_time = time.time() - start_time
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print("\n" + "=" * 70)
    print("Conversion Summary")
    print("=" * 70)
    print(f"Total videos: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {successful / len(results) * 100:.1f}%")
    print(f"Total time: {total_time // 60:.0f}m {total_time % 60:.0f}s")
    print("=" * 70)
    
    # List successful conversions
    if successful > 0:
        print("\n✓ Successful Conversions:")
        for r in results:
            if r['success']:
                print(f"  - {r['file']} ({r['size']}, {r['duration']})")
    
    # List failures
    if failed > 0:
        print("\n✗ Failed Conversions:")
        for r in results:
            if not r['success']:
                print(f"  - {r['url']}")
                print(f"    Error: {r['error']}")
    
    return results

def read_urls_from_file(filename):
    """Read URLs from a text file (one per line)."""
    try:
        with open(filename, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return urls
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Batch convert YouTube videos to MP3 with rate limiting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Convert from file
  %(prog)s urls.txt
  
  # Convert with custom settings
  %(prog)s urls.txt --bitrate 320 --delay 3
  
  # Convert specific URLs
  %(prog)s --urls "URL1" "URL2" "URL3"
  
  # Large batch with longer breaks
  %(prog)s urls.txt --batch-size 10 --break-time 600

Rate Limiting:
  Default settings (delay=2s, batch=15) are safe for most use cases.
  For heavy use, increase delay and reduce batch size.
  
  Recommended limits:
    - Light use (1-10 videos): No special settings needed
    - Moderate use (10-20 videos): --delay 2 (default)
    - Heavy use (20-50 videos): --delay 3 --batch-size 10
    - Bulk use (50+ videos): --delay 5 --batch-size 10 --break-time 600
        '''
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='Text file with YouTube URLs (one per line)'
    )
    
    parser.add_argument(
        '--urls',
        nargs='+',
        help='YouTube URLs to convert (space-separated)'
    )
    
    parser.add_argument(
        '-b', '--bitrate',
        type=int,
        default=192,
        choices=range(128, 321),
        metavar='128-320',
        help='MP3 bitrate in kbps (default: 192)'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default='output',
        help='Output directory (default: output)'
    )
    
    parser.add_argument(
        '-d', '--delay',
        type=int,
        default=2,
        help='Delay between videos in seconds (default: 2)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=15,
        help='Videos per batch before break (default: 15)'
    )
    
    parser.add_argument(
        '--break-time',
        type=int,
        default=300,
        help='Break duration between batches in seconds (default: 300 = 5 minutes)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Get URLs from file or command line
    if args.urls:
        urls = args.urls
    elif args.file:
        urls = read_urls_from_file(args.file)
    else:
        parser.print_help()
        print("\nError: Please provide either a file or --urls")
        sys.exit(1)
    
    if not urls:
        print("Error: No URLs provided")
        sys.exit(1)
    
    # Validate settings
    if args.delay < 0:
        print("Error: Delay must be >= 0")
        sys.exit(1)
    
    if args.batch_size < 1:
        print("Error: Batch size must be >= 1")
        sys.exit(1)
    
    # Warning for aggressive settings
    if len(urls) > 20 and args.delay < 2:
        print("⚠️  Warning: Converting many videos with short delay may trigger rate limiting")
        print("   Recommendation: Use --delay 2 or higher")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted")
            sys.exit(0)
    
    # Run conversion
    try:
        results = safe_batch_convert(
            urls=urls,
            bitrate=args.bitrate,
            output_dir=args.output_dir,
            delay=args.delay,
            batch_size=args.batch_size,
            break_time=args.break_time,
            verbose=args.verbose
        )
        
        # Exit code based on success rate
        successful = sum(1 for r in results if r['success'])
        if successful == len(results):
            return 0  # All successful
        elif successful > 0:
            return 1  # Partial success
        else:
            return 2  # All failed
    
    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user")
        return 130

if __name__ == '__main__':
    sys.exit(main())
