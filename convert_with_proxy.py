#!/usr/bin/env python3
"""
YouTube to MP3 Converter with Smart Proxy (Hybrid Method)
- Proxy ONLY for metadata (bypass rate limit)
- Direct download without proxy (save bandwidth 99%)
- Auto-load proxies from proxies.txt
- Auto-rotation
"""

import sys
import time
from pathlib import Path
from src.proxy_manager import ProxyManager
from src.smart_downloader import SmartDownloader
from src.conversion_pipeline import ConversionPipeline


def convert_batch(urls_file='urls.txt', output_dir='output', bitrate=192):
    """Convert batch URLs with smart proxy."""
    
    # Load proxies
    proxy_mgr = ProxyManager('proxies.txt', rotation_mode='round-robin')
    
    if not proxy_mgr.has_proxies():
        print("❌ No proxies in proxies.txt")
        return
    
    # Load URLs
    try:
        with open(urls_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        print(f"❌ File {urls_file} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"YouTube to MP3 Converter (Smart Proxy)")
    print(f"{'='*60}")
    print(f"Proxies: {proxy_mgr.get_proxy_count()} loaded")
    print(f"URLs: {len(urls)}")
    print(f"Method: Proxy for metadata only (99% bandwidth save)")
    print(f"{'='*60}\n")
    
    success = 0
    failed = 0
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] {url}")
        
        proxy = proxy_mgr.get_next_proxy()
        print(f"  Proxy: {proxy.split('@')[-1] if '@' in proxy else proxy}")
        
        try:
            # Smart downloader: proxy ONLY for metadata
            downloader = SmartDownloader(proxy=proxy, use_cookies=False, rotate_user_agent=True)
            pipeline = ConversionPipeline(output_dir=output_dir, downloader=downloader)
            
            print(f"  Getting metadata via proxy...")
            result = pipeline.convert(url, output_dir=output_dir, bitrate=bitrate)
            
            if result.success:
                success += 1
                proxy_mgr.report_success(proxy)
                print(f"  ✓ {result.mp3_file.filename} ({result.mp3_file.file_size_mb:.1f}MB)")
            else:
                failed += 1
                proxy_mgr.report_failure(proxy)
                print(f"  ✗ Failed")
        except Exception as e:
            failed += 1
            proxy_mgr.report_failure(proxy)
            print(f"  ✗ Error: {str(e)[:80]}")
        
        print()
    
    # Summary
    print(f"{'='*60}")
    print(f"DONE: {success} success, {failed} failed")
    print(f"{'='*60}\n")
    
    proxy_mgr.print_stats()


if __name__ == '__main__':
    convert_batch()
