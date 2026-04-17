#!/usr/bin/env python3
"""
YouTube to MP3 Converter with YouTube Data API + Proxy
- Metadata: YouTube Data API (FREE, 10k/day, no rate limit)
- Download: Proxy rotation (bypass datacenter IP block)
"""

import sys
from pathlib import Path
from src.youtube_api import YouTubeAPI
from src.video_downloader import VideoDownloader
from src.conversion_pipeline import ConversionPipeline
from src.proxy_manager import ProxyManager


# YouTube Data API Key
API_KEY = "AIzaSyDEtALTlUCSyVuzJ2ReAefoDOUoRkNxnOo"


def convert_batch(urls_file='urls.txt', output_dir='output', bitrate=192, proxies_file='proxies.txt'):
    """Convert batch URLs with YouTube Data API + Proxy."""
    
    # Initialize API
    youtube_api = YouTubeAPI(API_KEY)
    
    # Initialize Proxy Manager
    proxy_manager = ProxyManager(
        proxies_file=proxies_file,
        rotation_mode='round-robin',
        skip_unhealthy=True
    )
    
    if not proxy_manager.has_proxies():
        print(f"❌ No proxies found in {proxies_file}")
        return
    
    # Load URLs
    try:
        with open(urls_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        print(f"❌ File {urls_file} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"YouTube to MP3 Converter (API + Proxy)")
    print(f"{'='*60}")
    print(f"Metadata: YouTube Data API (FREE, no rate limit)")
    print(f"Download: Proxy rotation ({proxy_manager.get_proxy_count()} proxies)")
    print(f"URLs: {len(urls)}")
    print(f"{'='*60}\n")
    
    success = 0
    failed = 0
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] {url}")
        
        try:
            # Get metadata via API (FREE, no rate limit!)
            print(f"  Getting metadata via API...")
            metadata = youtube_api.get_video_info(url)
            
            if not metadata:
                failed += 1
                print(f"  ✗ Failed to get metadata")
                continue
            
            print(f"  Title: {metadata.title}")
            print(f"  Duration: {metadata.duration}s")
            
            # Get proxy for download
            proxy = proxy_manager.get_next_proxy()
            print(f"  Using proxy: {proxy.split('@')[-1] if '@' in proxy else proxy}")
            
            # Download with proxy
            print(f"  Downloading with proxy...")
            downloader = VideoDownloader(
                proxy=proxy,
                use_cookies=False,
                rotate_user_agent=True
            )
            
            pipeline = ConversionPipeline(output_dir=output_dir, downloader=downloader)
            mp3_file, error = pipeline.convert(url, bitrate=bitrate)
            
            if mp3_file:
                success += 1
                proxy_manager.report_success(proxy)
                print(f"  ✓ {mp3_file.filename} ({mp3_file.file_size_mb:.1f}MB)")
            else:
                failed += 1
                proxy_manager.report_failure(proxy)
                print(f"  ✗ Failed: {error.error_message if error else 'Unknown'}")
        
        except Exception as e:
            failed += 1
            if 'proxy' in locals():
                proxy_manager.report_failure(proxy)
            print(f"  ✗ Error: {str(e)[:80]}")
        
        print()
    
    # Summary
    print(f"{'='*60}")
    print(f"DONE: {success} success, {failed} failed")
    print(f"API quota used: {len(urls)} / 10,000 daily limit")
    print(f"{'='*60}\n")
    
    # Proxy stats
    proxy_manager.print_stats()


if __name__ == '__main__':
    convert_batch()
