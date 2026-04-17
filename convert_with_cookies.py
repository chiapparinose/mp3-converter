#!/usr/bin/env python3
"""
YouTube to MP3 Converter with YouTube Data API + Browser Cookies
- Metadata: YouTube Data API (FREE, 10k/day, no rate limit)
- Download: Browser cookies from residential IP (bypass bot detection)

HOW TO GET COOKIES:
1. Install browser extension: "Get cookies.txt LOCALLY" 
   Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/
2. Go to youtube.com and login (if not already)
3. Click extension icon and export cookies
4. Save as 'cookies.txt' in this directory
5. Upload cookies.txt to VPS
"""

import sys
from pathlib import Path
from src.youtube_api import YouTubeAPI
from src.video_downloader import VideoDownloader
from src.conversion_pipeline import ConversionPipeline


# YouTube Data API Key
API_KEY = "AIzaSyDEtALTlUCSyVuzJ2ReAefoDOUoRkNxnOo"


def convert_batch(urls_file='urls.txt', output_dir='output', bitrate=192, cookies_file='cookies.txt'):
    """Convert batch URLs with YouTube Data API + Browser Cookies."""
    
    # Initialize API
    youtube_api = YouTubeAPI(API_KEY)
    
    # Check cookies file
    if not Path(cookies_file).exists():
        print(f"\n❌ Cookies file not found: {cookies_file}")
        print("\nHOW TO GET COOKIES:")
        print("1. Install browser extension: 'Get cookies.txt LOCALLY'")
        print("   Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc")
        print("   Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/")
        print("2. Go to youtube.com and login")
        print("3. Click extension icon and export cookies")
        print("4. Save as 'cookies.txt' in this directory")
        print("5. Upload cookies.txt to VPS\n")
        return
    
    # Load URLs
    try:
        with open(urls_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        print(f"❌ File {urls_file} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"YouTube to MP3 Converter (API + Cookies)")
    print(f"{'='*60}")
    print(f"Metadata: YouTube Data API (FREE, no rate limit)")
    print(f"Download: Browser cookies (bypass bot detection)")
    print(f"URLs: {len(urls)}")
    print(f"Cookies: {cookies_file}")
    print(f"{'='*60}\n")
    
    success = 0
    failed = 0
    
    # Downloader with cookies
    downloader = VideoDownloader(
        use_cookies=True,
        cookies_file=cookies_file,
        rotate_user_agent=True
    )
    
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
            
            # Download with cookies
            print(f"  Downloading with cookies...")
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
