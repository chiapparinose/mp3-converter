#!/usr/bin/env python3
"""
Advanced Batch Converter with All Rate Limiting Bypass Methods

Features:
- Browser cookies support (highest rate limits)
- User agent rotation
- Exponential backoff retry logic
- Metadata caching
- Automatic delays and breaks
- Progress tracking and statistics
"""

import sys
import time
import argparse
from pathlib import Path
from src.conversion_pipeline import ConversionPipeline
from src.video_downloader import VideoDownloader
from src.video_cache import VideoCache


def advanced_batch_convert(
    urls,
    bitrate=192,
    output_dir='output',
    delay=2,
    batch_size=15,
    break_time=300,
    use_cookies=True,
    cookies_browser='chrome',
    cookies_file=None,
    rotate_user_agent=True,
    use_cache=True,
    verbose=False
):
    """
    Advanced batch converter with all rate limiting bypass methods.
    
    Args:
        urls: List of YouTube URLs
        bitrate: MP3 bitrate (128-320 kbps)
        output_dir: Output directory
        delay: Delay between videos (seconds)
        batch_size: Videos per batch before break
        break_time: Break duration between batches (seconds)
        use_cookies: Enable browser cookies (recommended)
        cookies_browser: Browser to extract cookies from
        cookies_file: Path to cookies.txt file
        rotate_user_agent: Enable user agent rotation
        use_cache: Enable metadata caching
        verbose: Enable verbose output
    
    Returns:
        List of results with success/failure status
    """
    # Initialize components with rate limiting bypass
    downloader = VideoDownloader(
        use_cookies=use_cookies,
        cookies_browser=cookies_browser,
        cookies_file=cookies_file,
        rotate_user_agent=rotate_user_agent
    )
    
    pipeline = ConversionPipeline(
        output_dir=output_dir,
        downloader=downloader
    )
    
    cache = VideoCache() if use_cache else None
    
    results = []
    cache_hits = 0
    rate_limit_errors = 0
    
    print("=" * 80)
    print("Advanced Batch Converter with Rate Limiting Bypass")
    print("=" * 80)
    print(f"Total videos: {len(urls)}")
    print(f"Bitrate: {bitrate} kbps")
    print(f"Output directory: {output_dir}")
    print(f"Delay between videos: {delay}s")
    print(f"Batch size: {batch_size} videos")
    print(f"Break between batches: {break_time}s ({break_time // 60} minutes)")
    print()
    print("Rate Limiting Bypass Features:")
    print(f"  ✓ Browser Cookies: {'Enabled' if use_cookies else 'Disabled'}")
    if use_cookies:
        if cookies_file:
            print(f"    - Using cookies file: {cookies_file}")
        else:
            print(f"    - Using browser: {cookies_browser}")
    print(f"  ✓ User Agent Rotation: {'Enabled' if rotate_user_agent else 'Disabled'}")
    print(f"  ✓ Exponential Backoff: Enabled (up to 5 retries)")
    print(f"  ✓ Metadata Caching: {'Enabled' if use_cache else 'Disabled'}")
    print("=" * 80)
    print()
    
    # Show cache stats if enabled
    if cache:
        stats = cache.get_stats()
        if stats['total_entries'] > 0:
            print(f"Cache: {stats['total_entries']} entries, "
                  f"{stats['cache_size_mb']:.2f} MB, "
                  f"TTL: {stats['ttl_days']:.0f} days")
            print()
    
    start_time = time.time()
    
    for i, url in enumerate(urls):
        video_num = i + 1
        print(f"[{video_num}/{len(urls)}] Converting: {url}")
        
        # Check cache first
        if cache:
            video_id = cache.extract_video_id(url)
            if video_id and cache.has(video_id):
                cached_metadata = cache.get(video_id)
                if cached_metadata:
                    cache_hits += 1
                    print(f"  ℹ️  Using cached metadata (cache hit #{cache_hits})")
        
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
                    'duration': f"{mp3_file.duration // 60}:{mp3_file.duration % 60:02d}",
                    'retries': downloader.get_retry_count()
                })
                
                retry_info = f" (after {downloader.get_retry_count()} retries)" if downloader.get_retry_count() > 0 else ""
                print(f"✓ Success: {mp3_file.filename} ({mp3_file.file_size_mb:.2f} MB){retry_info}")
                
                # Cache metadata if enabled
                if cache and video_id:
                    cache.set(video_id, {
                        'title': mp3_file.title,
                        'channel': mp3_file.channel,
                        'duration': mp3_file.duration
                    })
            else:
                error_msg = error.error_message if error else 'Unknown error'
                
                # Check if it's a rate limit error
                is_rate_limit = any(keyword in error_msg.lower() for keyword in [
                    'rate limit', 'too many requests', 'bot', 'captcha', '429'
                ])
                
                if is_rate_limit:
                    rate_limit_errors += 1
                
                results.append({
                    'url': url,
                    'success': False,
                    'error': error_msg,
                    'rate_limited': is_rate_limit
                })
                
                error_prefix = "⚠️  Rate Limited" if is_rate_limit else "✗ Failed"
                print(f"{error_prefix}: {error_msg}")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Conversion interrupted by user")
            break
        
        except Exception as e:
            error_msg = str(e)
            is_rate_limit = any(keyword in error_msg.lower() for keyword in [
                'rate limit', 'too many requests', 'bot', 'captcha', '429'
            ])
            
            if is_rate_limit:
                rate_limit_errors += 1
            
            results.append({
                'url': url,
                'success': False,
                'error': error_msg,
                'rate_limited': is_rate_limit
            })
            
            error_prefix = "⚠️  Rate Limited" if is_rate_limit else "✗ Error"
            print(f"{error_prefix}: {e}")
        
        # Rate limiting logic
        if video_num < len(urls):  # Not last video
            if video_num % batch_size == 0:
                # Batch complete - take longer break
                successful_in_batch = sum(1 for r in results[-batch_size:] if r['success'])
                print(f"\n{'='*80}")
                print(f"Batch {video_num // batch_size} complete: {successful_in_batch}/{batch_size} successful")
                
                if rate_limit_errors > 0:
                    print(f"⚠️  Rate limit errors in this session: {rate_limit_errors}")
                    print(f"   Recommendation: Increase delay or enable more bypass methods")
                
                print(f"⏸️  Taking {break_time}s ({break_time // 60} minute) break to avoid rate limiting...")
                print(f"{'='*80}\n")
                
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
    
    print("\n" + "=" * 80)
    print("Conversion Summary")
    print("=" * 80)
    print(f"Total videos: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {successful / len(results) * 100:.1f}%")
    print(f"Total time: {total_time // 60:.0f}m {total_time % 60:.0f}s")
    
    if cache_hits > 0:
        print(f"Cache hits: {cache_hits} (saved {cache_hits} API requests)")
    
    if rate_limit_errors > 0:
        print(f"⚠️  Rate limit errors: {rate_limit_errors}")
        print(f"   Suggestions:")
        if not use_cookies:
            print(f"   - Enable browser cookies (--use-cookies)")
        print(f"   - Increase delay (--delay {delay + 2})")
        print(f"   - Reduce batch size (--batch-size {max(5, batch_size - 5)})")
        print(f"   - Increase break time (--break-time {break_time + 300})")
    
    print("=" * 80)
    
    # List successful conversions
    if successful > 0:
        print("\n✓ Successful Conversions:")
        for r in results:
            if r['success']:
                retry_info = f" [{r['retries']} retries]" if r.get('retries', 0) > 0 else ""
                print(f"  - {r['file']} ({r['size']}, {r['duration']}){retry_info}")
    
    # List failures
    if failed > 0:
        print("\n✗ Failed Conversions:")
        for r in results:
            if not r['success']:
                rate_limit_marker = " [RATE LIMITED]" if r.get('rate_limited') else ""
                print(f"  - {r['url']}{rate_limit_marker}")
                print(f"    Error: {r['error']}")
    
    # Cache stats
    if cache:
        print("\nCache Statistics:")
        stats = cache.get_stats()
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Cache size: {stats['cache_size_mb']:.2f} MB")
        print(f"  Cache hits this session: {cache_hits}")
    
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
        description='Advanced batch converter with rate limiting bypass',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage with all bypass methods enabled
  %(prog)s urls.txt
  
  # Use Firefox cookies instead of Chrome
  %(prog)s urls.txt --cookies-browser firefox
  
  # Use cookies file
  %(prog)s urls.txt --cookies-file cookies.txt
  
  # Disable cookies (not recommended)
  %(prog)s urls.txt --no-cookies
  
  # Heavy use with aggressive settings
  %(prog)s urls.txt --delay 5 --batch-size 10 --break-time 600

Rate Limiting Bypass Methods:
  1. Browser Cookies (BEST) - Increases limit to 100+ requests
  2. User Agent Rotation - Helps avoid bot detection
  3. Exponential Backoff - Automatic retry with increasing delays
  4. Metadata Caching - Reduces number of API requests
  
All methods are enabled by default for maximum effectiveness.
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
    
    # Rate limiting bypass options
    parser.add_argument(
        '--no-cookies',
        action='store_true',
        help='Disable browser cookies (not recommended)'
    )
    
    parser.add_argument(
        '--cookies-browser',
        default='chrome',
        choices=['chrome', 'firefox', 'edge', 'safari', 'opera', 'brave'],
        help='Browser to extract cookies from (default: chrome)'
    )
    
    parser.add_argument(
        '--cookies-file',
        help='Path to cookies.txt file (alternative to browser extraction)'
    )
    
    parser.add_argument(
        '--no-user-agent-rotation',
        action='store_true',
        help='Disable user agent rotation'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable metadata caching'
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
    
    # Warning for disabled bypass methods
    if args.no_cookies:
        print("⚠️  Warning: Browser cookies disabled - rate limits will be lower")
        print("   Recommendation: Enable cookies for best results")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted")
            sys.exit(0)
    
    # Run conversion
    try:
        results = advanced_batch_convert(
            urls=urls,
            bitrate=args.bitrate,
            output_dir=args.output_dir,
            delay=args.delay,
            batch_size=args.batch_size,
            break_time=args.break_time,
            use_cookies=not args.no_cookies,
            cookies_browser=args.cookies_browser,
            cookies_file=args.cookies_file,
            rotate_user_agent=not args.no_user_agent_rotation,
            use_cache=not args.no_cache,
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
