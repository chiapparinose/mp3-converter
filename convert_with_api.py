#!/usr/bin/env python3
"""
YouTube to MP3 Converter with YouTube Data API
- FREE: 10,000 requests/day
- NO rate limiting
- NO proxy needed
- Metadata via API, download direct
"""

import sys
from pathlib import Path
from src.youtube_api import YouTubeAPI
from src.video_downloader import VideoDownloader
from src.conversion_pipeline import ConversionPipeline


# YouTube Data API Key
API_KEY = "AIzaSyDEtALTlUCSyVuzJ2ReAefoDOUoRkNxnOo"


def convert_batch(urls_file='urls.txt', output_dir='output', bitrate=192):
    """Convert batch URLs with YouTube Data API."""
    
    # Initialize API
    youtube_api = YouTubeAPI(API_KEY)
    
    # Load URLs
    try:
        with open(urls_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        print(f"❌ File {urls_file} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"YouTube to MP3 Converter (YouTube Data API)")
    print(f"{'='*60}")
    print(f"API: YouTube Data API v3 (FREE, no rate limit)")
    print(f"URLs: {len(urls)}")
    print(f"Method: API for metadata, direct download")
    print(f"{'='*60}\n")
    
    success = 0
    failed = 0
    
    # Downloader without proxy (direct)
    downloader = VideoDownloader(use_cookies=False, rotate_user_agent=True)
    
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
            
            # Download and convert
            print(f"  Downloading...")
            pipeline = ConversionPipeline(output_dir=output_dir, downloader=downloader)
            mp3_file, error = pipeline.convert(url, bitrate=bitrate)
            
            if mp3_file:
                success += 1
                print(f"  ✓ {mp3_file.filename} ({mp3_file.file_size_mb:.1f}MB)")
            else:
                failed += 1
                print(f"  ✗ Failed: {error.error_message if error else 'Unknown'}")
        
        except Exception as e:
            failed += 1
            print(f"  ✗ Error: {str(e)[:80]}")
        
        print()
    
    # Summary
    print(f"{'='*60}")
    print(f"DONE: {success} success, {failed} failed")
    print(f"API quota used: {len(urls)} / 10,000 daily limit")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    convert_batch()
