#!/usr/bin/env python3
"""
Smart Batch Converter - Uses Proxy ONLY for Metadata
Saves 90%+ proxy bandwidth by downloading videos directly!

Bandwidth Usage:
- Full Proxy Mode: 100 videos = ~1 GB proxy bandwidth
- Smart Mode: 100 videos = ~5 MB proxy bandwidth (200x less!)
"""

import sys
import time
import argparse
from pathlib import Path
from src.conversion_pipeline import ConversionPipeline
from src.smart_downloader import SmartDownloader


def batch_convert_smart(
    urls_file: str,
    proxy: str,
    output_dir: str = 'output',
    bitrate: int = 192,
    delay: float = 0.5,
    show_bandwidth_stats: bool = True
):
    """
    Batch convert with smart proxy usage (metadata only).
    
    Args:
        urls_file: Path to file with YouTube URLs
        proxy: Proxy URL (used ONLY for metadata)
        output_dir: Output directory
        bitrate: MP3 bitrate
        delay: Delay between requests
        show_bandwidth_stats: Show bandwidth comparison
    """
    # Read URLs
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"❌ Error: File '{urls_file}' not found")
        return
    
    if not urls:
        print(f"❌ Error: No URLs found in '{urls_file}'")
        return
    
    print("\n" + "="*70)
    print("Smart Batch Converter - Proxy Only for Metadata")
    print("="*70)
    print(f"\n📁 URLs file: {urls_file}")
    print(f"🌐 Proxy: {proxy.split('@')[-1] if '@' in proxy else proxy}")
    print(f"   Usage: METADATA ONLY (saves 90%+ bandwidth!)")
    print(f"📂 Output: {output_dir}")
    print(f"🎵 Bitrate: {bitrate} kbps")
    print(f"⏱️  Delay: {delay}s")
    print(f"📊 Total videos: {len(urls)}")
    
    # Show bandwidth comparison
    if show_bandwidth_stats:
        downloader = SmartDownloader(proxy=proxy)
        downloader.print_bandwidth_comparison(len(urls))
    
    print("\n" + "-"*70 + "\n")
    
    # Initialize smart downloader
    downloader = SmartDownloader(
        proxy=proxy,
        use_cookies=False,
        rotate_user_agent=True
    )
    
    # Create pipeline
    pipeline = ConversionPipeline(
        output_dir=output_dir,
        downloader=downloader
    )
    
    # Convert videos
    success = 0
    failed = 0
    start_time = time.time()
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Converting: {url}")
        
        try:
            # Get metadata via proxy (bypass rate limit)
            print(f"  → Getting metadata via proxy...")
            metadata = downloader.get_video_info(url)
            
            if not metadata:
                failed += 1
                print(f"  ✗ Failed to get metadata")
                continue
            
            print(f"  → Title: {metadata.title}")
            print(f"  → Downloading audio direct (no proxy)...")
            
            # Convert (download happens without proxy)
            result = pipeline.convert(url, output_dir=output_dir, bitrate=bitrate)
            
            if result.success:
                success += 1
                print(f"  ✓ Success: {result.mp3_file.filename}")
                print(f"    Size: {result.mp3_file.file_size_mb:.2f} MB")
                print(f"    Duration: {result.mp3_file.duration // 60}:{result.mp3_file.duration % 60:02d}")
            else:
                failed += 1
                print(f"  ✗ Failed to convert")
        except Exception as e:
            failed += 1
            print(f"  ✗ Error: {str(e)}")
        
        # Delay between requests
        if i < len(urls) - 1 and delay > 0:
            time.sleep(delay)
        
        print()
    
    # Summary
    total_time = time.time() - start_time
    
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n✓ Success: {success}/{len(urls)} ({success/len(urls)*100:.1f}%)")
    print(f"✗ Failed: {failed}/{len(urls)} ({failed/len(urls)*100:.1f}%)")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"⚡ Speed: {len(urls)/total_time*60:.1f} videos/hour")
    
    # Bandwidth usage estimate
    avg_video_size = 10  # MB
    metadata_size = 0.05  # MB (~50 KB)
    
    proxy_bandwidth_used = len(urls) * metadata_size
    direct_bandwidth_used = success * avg_video_size
    
    print(f"\n📊 Bandwidth Usage:")
    print(f"  Proxy (metadata only): ~{proxy_bandwidth_used:.1f} MB")
    print(f"  Direct (downloads): ~{direct_bandwidth_used:.1f} MB")
    print(f"  Total: ~{proxy_bandwidth_used + direct_bandwidth_used:.1f} MB")
    
    # Cost estimate
    proxy_cost = proxy_bandwidth_used / 1024 * 1.75  # $1.75/GB
    print(f"\n💰 Proxy Cost: ~${proxy_cost:.4f} (vs ${(proxy_bandwidth_used + direct_bandwidth_used)/1024*1.75:.2f} if full proxy)")
    
    print(f"\n📂 Output directory: {output_dir}/")
    print("\n" + "="*70 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Smart Batch Converter - Proxy Only for Metadata (Saves 90%+ Bandwidth)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 batch_smart_proxy.py urls.txt 'http://user:pass@proxy.com:8080'
  python3 batch_smart_proxy.py urls.txt 'http://user:pass@proxy.com:8080' --bitrate 320
  python3 batch_smart_proxy.py urls.txt 'http://user:pass@proxy.com:8080' --no-stats

How It Works:
  1. Get metadata via proxy (bypass rate limit) - ~50 KB per video
  2. Download video direct (no proxy) - ~10 MB per video
  3. Save 90%+ proxy bandwidth!

Bandwidth Comparison (100 videos):
  Full Proxy Mode: ~1 GB proxy bandwidth ($1.75)
  Smart Mode: ~5 MB proxy bandwidth ($0.01)
  Savings: ~995 MB (99%) and $1.74!

Why This Works:
  - YouTube rate limits METADATA requests (video info)
  - YouTube does NOT rate limit actual video downloads
  - So we only need proxy for metadata, not downloads!

Proxy Formats:
  HTTP:   http://username:password@proxy.com:8080
  HTTPS:  https://username:password@proxy.com:8080
  SOCKS5: socks5://username:password@proxy.com:1080
        """
    )
    
    parser.add_argument('urls_file', help='Text file with YouTube URLs (one per line)')
    parser.add_argument('proxy', help='Proxy URL (used ONLY for metadata)')
    parser.add_argument('--output-dir', default='output', help='Output directory (default: output)')
    parser.add_argument('--bitrate', type=int, default=192, choices=[128, 192, 256, 320],
                        help='MP3 bitrate in kbps (default: 192)')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('--no-stats', action='store_true',
                        help='Hide bandwidth statistics')
    
    args = parser.parse_args()
    
    # Validate proxy format
    if not any(args.proxy.startswith(proto) for proto in ['http://', 'https://', 'socks5://']):
        print("\n❌ Error: Invalid proxy format")
        print("\nValid formats:")
        print("  http://username:password@proxy.com:8080")
        print("  https://username:password@proxy.com:8080")
        print("  socks5://username:password@proxy.com:1080")
        print()
        sys.exit(1)
    
    # Run batch convert
    batch_convert_smart(
        urls_file=args.urls_file,
        proxy=args.proxy,
        output_dir=args.output_dir,
        bitrate=args.bitrate,
        delay=args.delay,
        show_bandwidth_stats=not args.no_stats
    )


if __name__ == "__main__":
    main()
