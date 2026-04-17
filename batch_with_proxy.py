#!/usr/bin/env python3
"""
Batch YouTube to MP3 Converter with Residential Proxy Support
Perfect for VPS with datacenter IPs that get rate limited.
"""

import sys
import time
import argparse
from pathlib import Path
from src.conversion_pipeline import ConversionPipeline
from src.video_downloader import VideoDownloader


def batch_convert_with_proxy(
    urls_file: str,
    proxy: str,
    output_dir: str = 'output',
    bitrate: int = 192,
    delay: float = 0.5
):
    """
    Batch convert YouTube videos to MP3 using residential proxy.
    
    Args:
        urls_file: Path to file with YouTube URLs (one per line)
        proxy: Proxy URL (e.g., 'http://user:pass@proxy.com:8080')
        output_dir: Output directory for MP3 files
        bitrate: MP3 bitrate (128-320 kbps)
        delay: Delay between requests in seconds
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
    print("Batch YouTube to MP3 Converter with Residential Proxy")
    print("="*70)
    print(f"\n📁 URLs file: {urls_file}")
    print(f"🌐 Proxy: {proxy.split('@')[-1] if '@' in proxy else proxy}")
    print(f"📂 Output: {output_dir}")
    print(f"🎵 Bitrate: {bitrate} kbps")
    print(f"⏱️  Delay: {delay}s")
    print(f"📊 Total videos: {len(urls)}")
    print("\n" + "-"*70 + "\n")
    
    # Initialize downloader with proxy
    downloader = VideoDownloader(
        use_cookies=False,  # No need for cookies with residential proxy
        rotate_user_agent=True,
        proxy=proxy
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
            result = pipeline.convert(url, output_dir=output_dir, bitrate=bitrate)
            
            if result.success:
                success += 1
                print(f"  ✓ Success: {result.mp3_file.filename}")
                print(f"    Size: {result.mp3_file.file_size_mb:.2f} MB")
                print(f"    Duration: {result.mp3_file.duration // 60}:{result.mp3_file.duration % 60:02d}")
            else:
                failed += 1
                print(f"  ✗ Failed")
        except Exception as e:
            failed += 1
            print(f"  ✗ Error: {str(e)}")
        
        # Delay between requests (optional with good proxy)
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
    print(f"\n📂 Output directory: {output_dir}/")
    print("\n" + "="*70 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Batch YouTube to MP3 Converter with Residential Proxy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 batch_with_proxy.py urls.txt 'http://user:pass@proxy.com:8080'
  python3 batch_with_proxy.py urls.txt 'http://user:pass@proxy.com:8080' --bitrate 320
  python3 batch_with_proxy.py urls.txt 'socks5://user:pass@proxy.com:1080' --delay 1.0

Proxy Formats:
  HTTP:   http://username:password@proxy.com:8080
  HTTPS:  https://username:password@proxy.com:8080
  SOCKS5: socks5://username:password@proxy.com:1080

Recommended Proxy Providers:
  • IPRoyal: https://iproyal.com ($1.75/GB - Cheapest)
  • Smartproxy: https://smartproxy.com ($75/month for 8GB)
  • Bright Data: https://brightdata.com (Premium)

URLs File Format:
  One URL per line, lines starting with # are ignored
  
  Example urls.txt:
    # My favorite songs
    https://www.youtube.com/watch?v=dQw4w9WgXcQ
    https://www.youtube.com/watch?v=9bZkp7q19f0
    https://www.youtube.com/watch?v=kJQP7kiw5Fk
        """
    )
    
    parser.add_argument('urls_file', help='Text file with YouTube URLs (one per line)')
    parser.add_argument('proxy', help='Proxy URL (e.g., http://user:pass@proxy.com:8080)')
    parser.add_argument('--output-dir', default='output', help='Output directory (default: output)')
    parser.add_argument('--bitrate', type=int, default=192, choices=[128, 192, 256, 320],
                        help='MP3 bitrate in kbps (default: 192)')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='Delay between requests in seconds (default: 0.5)')
    
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
    batch_convert_with_proxy(
        urls_file=args.urls_file,
        proxy=args.proxy,
        output_dir=args.output_dir,
        bitrate=args.bitrate,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
