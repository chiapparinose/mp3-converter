#!/usr/bin/env python3
"""
Smart Batch Converter with Proxy File Support
- Loads proxies from proxies.txt
- Automatic proxy rotation
- Proxy ONLY for metadata (saves 99% bandwidth!)
- Direct download without proxy
"""

import sys
import time
import argparse
from pathlib import Path
from src.conversion_pipeline import ConversionPipeline
from src.smart_downloader import SmartDownloader
from src.proxy_manager import ProxyManager


def batch_convert_with_proxy_file(
    urls_file: str,
    proxies_file: str = 'proxies.txt',
    output_dir: str = 'output',
    bitrate: int = 192,
    delay: float = 0.5,
    rotation_mode: str = 'round-robin',
    show_stats: bool = True
):
    """
    Batch convert with proxies from file.
    
    Args:
        urls_file: Path to URLs file
        proxies_file: Path to proxies file
        output_dir: Output directory
        bitrate: MP3 bitrate
        delay: Delay between requests
        rotation_mode: 'round-robin' or 'random'
        show_stats: Show proxy statistics at end
    """
    # Read URLs
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"❌ Error: URLs file '{urls_file}' not found")
        return
    
    if not urls:
        print(f"❌ Error: No URLs found in '{urls_file}'")
        return
    
    # Initialize proxy manager
    proxy_manager = ProxyManager(
        proxies_file=proxies_file,
        rotation_mode=rotation_mode,
        skip_unhealthy=True
    )
    
    if not proxy_manager.has_proxies():
        print(f"❌ Error: No proxies loaded from '{proxies_file}'")
        print(f"\nCreate {proxies_file} with one proxy per line:")
        print("  http://username:password@proxy1.com:8080")
        print("  http://username:password@proxy2.com:8080")
        print("  socks5://username:password@proxy3.com:1080")
        return
    
    print("\n" + "="*70)
    print("Smart Batch Converter with Proxy File")
    print("="*70)
    print(f"\n📁 URLs file: {urls_file}")
    print(f"🌐 Proxies file: {proxies_file}")
    print(f"   Loaded: {proxy_manager.get_proxy_count()} proxies")
    print(f"   Rotation: {rotation_mode}")
    print(f"   Usage: METADATA ONLY (saves 99% bandwidth!)")
    print(f"📂 Output: {output_dir}")
    print(f"🎵 Bitrate: {bitrate} kbps")
    print(f"⏱️  Delay: {delay}s")
    print(f"📊 Total videos: {len(urls)}")
    print("\n" + "-"*70 + "\n")
    
    # Convert videos
    success = 0
    failed = 0
    start_time = time.time()
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Converting: {url}")
        
        # Get next proxy
        proxy = proxy_manager.get_next_proxy()
        proxy_display = proxy.split('@')[-1] if '@' in proxy else proxy
        print(f"  → Using proxy: {proxy_display}")
        
        try:
            # Initialize smart downloader with current proxy
            downloader = SmartDownloader(
                proxy=proxy,  # Proxy ONLY for metadata
                use_cookies=False,
                rotate_user_agent=True
            )
            
            # Get metadata via proxy
            print(f"  → Getting metadata via proxy...")
            metadata = downloader.get_video_info(url)
            
            if not metadata:
                failed += 1
                proxy_manager.report_failure(proxy)
                print(f"  ✗ Failed to get metadata")
                continue
            
            # Report proxy success for metadata
            proxy_manager.report_success(proxy)
            
            print(f"  → Title: {metadata.title}")
            print(f"  → Downloading audio DIRECT (no proxy)...")
            
            # Create pipeline (download happens WITHOUT proxy)
            pipeline = ConversionPipeline(
                output_dir=output_dir,
                downloader=downloader
            )
            
            # Convert
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
            proxy_manager.report_failure(proxy)
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
    metadata_size = 0.05  # MB (~50 KB)
    avg_video_size = 10  # MB
    
    proxy_bandwidth = len(urls) * metadata_size
    direct_bandwidth = success * avg_video_size
    
    print(f"\n📊 Bandwidth Usage:")
    print(f"  Proxy (metadata only): ~{proxy_bandwidth:.1f} MB")
    print(f"  Direct (downloads): ~{direct_bandwidth:.1f} MB")
    print(f"  Total: ~{proxy_bandwidth + direct_bandwidth:.1f} MB")
    
    # Cost estimate
    proxy_cost = proxy_bandwidth / 1024 * 1.75  # $1.75/GB
    full_proxy_cost = (proxy_bandwidth + direct_bandwidth) / 1024 * 1.75
    
    print(f"\n💰 Proxy Cost:")
    print(f"  Smart mode: ~${proxy_cost:.4f}")
    print(f"  Full proxy mode: ~${full_proxy_cost:.2f}")
    print(f"  Savings: ~${full_proxy_cost - proxy_cost:.2f} ({(1 - proxy_cost/full_proxy_cost)*100:.1f}%)")
    
    print(f"\n📂 Output directory: {output_dir}/")
    
    # Show proxy statistics
    if show_stats:
        proxy_manager.print_stats()
    
    print("="*70 + "\n")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Smart Batch Converter with Proxy File Support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 batch_smart_proxy_file.py urls.txt
  python3 batch_smart_proxy_file.py urls.txt --proxies-file my_proxies.txt
  python3 batch_smart_proxy_file.py urls.txt --rotation random --bitrate 320
  python3 batch_smart_proxy_file.py urls.txt --no-stats

Proxies File Format (proxies.txt):
  One proxy per line, lines starting with # are ignored
  
  # My residential proxies
  http://username:password@proxy1.com:8080
  http://username:password@proxy2.com:8080
  socks5://username:password@proxy3.com:1080

How It Works:
  1. Loads proxies from file
  2. Rotates proxies automatically (round-robin or random)
  3. Uses proxy ONLY for metadata (~50 KB per video)
  4. Downloads video DIRECT without proxy (~10 MB per video)
  5. Saves 99% proxy bandwidth!

Bandwidth Savings (100 videos):
  Full Proxy Mode: ~1 GB proxy bandwidth ($1.75)
  Smart Mode: ~5 MB proxy bandwidth ($0.01)
  Savings: ~995 MB (99%) and $1.74!

URLs File Format (urls.txt):
  One URL per line, lines starting with # are ignored
  
  # My favorite songs
  https://www.youtube.com/watch?v=dQw4w9WgXcQ
  https://www.youtube.com/watch?v=9bZkp7q19f0
        """
    )
    
    parser.add_argument('urls_file', help='Text file with YouTube URLs (one per line)')
    parser.add_argument('--proxies-file', default='proxies.txt',
                        help='Text file with proxy URLs (default: proxies.txt)')
    parser.add_argument('--output-dir', default='output',
                        help='Output directory (default: output)')
    parser.add_argument('--bitrate', type=int, default=192, choices=[128, 192, 256, 320],
                        help='MP3 bitrate in kbps (default: 192)')
    parser.add_argument('--delay', type=float, default=0.5,
                        help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('--rotation', choices=['round-robin', 'random'], default='round-robin',
                        help='Proxy rotation mode (default: round-robin)')
    parser.add_argument('--no-stats', action='store_true',
                        help='Hide proxy statistics at end')
    
    args = parser.parse_args()
    
    # Run batch convert
    batch_convert_with_proxy_file(
        urls_file=args.urls_file,
        proxies_file=args.proxies_file,
        output_dir=args.output_dir,
        bitrate=args.bitrate,
        delay=args.delay,
        rotation_mode=args.rotation,
        show_stats=not args.no_stats
    )


if __name__ == "__main__":
    main()
