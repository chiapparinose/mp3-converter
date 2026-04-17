#!/usr/bin/env python3
"""
Verification Script - Memastikan Proxy HANYA untuk Metadata
Script ini memverifikasi bahwa:
1. Metadata request menggunakan proxy
2. Video download TIDAK menggunakan proxy (direct)
"""

import sys
from src.smart_downloader import SmartDownloader
from src.video_downloader import VideoDownloader


def verify_smart_proxy_implementation():
    """Verify that SmartDownloader uses proxy only for metadata."""
    
    print("\n" + "="*70)
    print("VERIFICATION: Smart Proxy Implementation")
    print("="*70)
    print("\nVerifying that proxy is ONLY used for metadata, NOT for download...")
    print()
    
    # Test proxy URL
    test_proxy = "http://test:test@proxy.example.com:8080"
    
    # Create SmartDownloader
    smart_downloader = SmartDownloader(
        proxy=test_proxy,
        use_cookies=False,
        rotate_user_agent=True
    )
    
    print("✓ SmartDownloader initialized with proxy")
    print(f"  Proxy: {test_proxy}")
    print()
    
    # Check metadata downloader (should have proxy)
    print("Checking metadata_downloader...")
    if smart_downloader.metadata_downloader.proxy == test_proxy:
        print("  ✓ CORRECT: metadata_downloader HAS proxy")
        print(f"    Proxy: {smart_downloader.metadata_downloader.proxy}")
    else:
        print("  ✗ ERROR: metadata_downloader missing proxy!")
        return False
    print()
    
    # Check download downloader (should NOT have proxy)
    print("Checking download_downloader...")
    if smart_downloader.download_downloader.proxy is None:
        print("  ✓ CORRECT: download_downloader has NO proxy (direct)")
        print(f"    Proxy: {smart_downloader.download_downloader.proxy}")
    else:
        print(f"  ✗ ERROR: download_downloader has proxy: {smart_downloader.download_downloader.proxy}")
        print("  This will waste bandwidth!")
        return False
    print()
    
    # Verify yt-dlp options
    print("Verifying yt-dlp options...")
    
    # Metadata downloader options (should have proxy)
    def dummy_hook(d): pass
    metadata_opts = smart_downloader.metadata_downloader._get_ydl_opts(dummy_hook)
    
    if 'proxy' in metadata_opts and metadata_opts['proxy'] == test_proxy:
        print("  ✓ CORRECT: metadata yt-dlp options include proxy")
    else:
        print("  ✗ ERROR: metadata yt-dlp options missing proxy!")
        return False
    
    # Download downloader options (should NOT have proxy)
    download_opts = smart_downloader.download_downloader._get_ydl_opts(dummy_hook)
    
    if 'proxy' not in download_opts:
        print("  ✓ CORRECT: download yt-dlp options have NO proxy")
    else:
        print(f"  ✗ ERROR: download yt-dlp options have proxy: {download_opts['proxy']}")
        return False
    
    print()
    print("="*70)
    print("VERIFICATION RESULT: ✓ ALL CHECKS PASSED")
    print("="*70)
    print("\nSummary:")
    print("  ✓ Metadata requests will use proxy (bypass rate limit)")
    print("  ✓ Video downloads will be direct (save bandwidth)")
    print("  ✓ Expected bandwidth savings: 99%")
    print()
    print("Implementation is CORRECT! 🎉")
    print("="*70 + "\n")
    
    return True


def verify_regular_downloader():
    """Verify that regular VideoDownloader uses proxy for everything."""
    
    print("\n" + "="*70)
    print("COMPARISON: Regular VideoDownloader (Full Proxy Mode)")
    print("="*70)
    print("\nFor comparison, checking regular VideoDownloader...")
    print()
    
    test_proxy = "http://test:test@proxy.example.com:8080"
    
    # Create regular VideoDownloader with proxy
    regular_downloader = VideoDownloader(
        proxy=test_proxy,
        use_cookies=False,
        rotate_user_agent=True
    )
    
    print("✓ VideoDownloader initialized with proxy")
    print(f"  Proxy: {test_proxy}")
    print()
    
    # Check if proxy is set
    if regular_downloader.proxy == test_proxy:
        print("  ✓ VideoDownloader HAS proxy")
        print(f"    Proxy: {regular_downloader.proxy}")
    else:
        print("  ✗ VideoDownloader missing proxy!")
        return False
    
    # Verify yt-dlp options
    def dummy_hook(d): pass
    opts = regular_downloader._get_ydl_opts(dummy_hook)
    
    if 'proxy' in opts and opts['proxy'] == test_proxy:
        print("  ✓ yt-dlp options include proxy")
        print("    This means BOTH metadata AND download use proxy")
        print("    Bandwidth usage: HIGH (metadata + download)")
    else:
        print("  ✗ yt-dlp options missing proxy!")
        return False
    
    print()
    print("="*70)
    print("Regular VideoDownloader uses proxy for EVERYTHING")
    print("="*70)
    print("\nSummary:")
    print("  • Metadata requests use proxy")
    print("  • Video downloads use proxy (BOROS!)")
    print("  • Bandwidth usage: 100% via proxy")
    print("="*70 + "\n")
    
    return True


def print_bandwidth_comparison():
    """Print bandwidth comparison."""
    
    print("\n" + "="*70)
    print("BANDWIDTH COMPARISON")
    print("="*70)
    print()
    
    num_videos = 100
    metadata_size_mb = 0.05  # 50 KB
    video_size_mb = 10  # 10 MB average
    
    # Regular mode (full proxy)
    regular_bandwidth = num_videos * (metadata_size_mb + video_size_mb)
    regular_cost = regular_bandwidth / 1024 * 1.75
    
    # Smart mode (proxy only for metadata)
    smart_bandwidth = num_videos * metadata_size_mb
    smart_cost = smart_bandwidth / 1024 * 1.75
    
    # Savings
    savings_bandwidth = regular_bandwidth - smart_bandwidth
    savings_cost = regular_cost - smart_cost
    savings_percent = (savings_bandwidth / regular_bandwidth) * 100
    
    print(f"Scenario: {num_videos} videos")
    print(f"  Avg metadata size: {metadata_size_mb} MB (~50 KB)")
    print(f"  Avg video size: {video_size_mb} MB")
    print()
    
    print("Regular VideoDownloader (Full Proxy):")
    print(f"  Proxy bandwidth: {regular_bandwidth:.1f} MB ({regular_bandwidth/1024:.2f} GB)")
    print(f"  Cost: ${regular_cost:.2f}")
    print()
    
    print("SmartDownloader (Proxy Only for Metadata):")
    print(f"  Proxy bandwidth: {smart_bandwidth:.1f} MB ({smart_bandwidth/1024:.2f} GB)")
    print(f"  Cost: ${smart_cost:.4f}")
    print()
    
    print("Savings:")
    print(f"  Bandwidth: {savings_bandwidth:.1f} MB ({savings_bandwidth/1024:.2f} GB)")
    print(f"  Percentage: {savings_percent:.1f}%")
    print(f"  Cost: ${savings_cost:.2f}")
    print()
    
    print("With $7 proxy (4 GB):")
    print(f"  Regular mode: ~{4*1024/regular_bandwidth*num_videos:.0f} videos")
    print(f"  Smart mode: ~{4*1024/smart_bandwidth*num_videos:.0f} videos")
    print(f"  Difference: {(4*1024/smart_bandwidth - 4*1024/regular_bandwidth)/num_videos:.0f}x more videos!")
    
    print("="*70 + "\n")


def main():
    """Main verification function."""
    
    print("\n" + "="*70)
    print("SMART PROXY VERIFICATION SCRIPT")
    print("="*70)
    print("\nThis script verifies that:")
    print("  1. SmartDownloader uses proxy ONLY for metadata")
    print("  2. SmartDownloader downloads videos DIRECT (no proxy)")
    print("  3. Bandwidth savings are maximized (99%)")
    print("="*70)
    
    # Verify SmartDownloader
    if not verify_smart_proxy_implementation():
        print("\n❌ VERIFICATION FAILED!")
        print("SmartDownloader implementation has issues.")
        sys.exit(1)
    
    # Verify regular downloader for comparison
    if not verify_regular_downloader():
        print("\n❌ COMPARISON FAILED!")
        sys.exit(1)
    
    # Print bandwidth comparison
    print_bandwidth_comparison()
    
    print("\n" + "="*70)
    print("✓ ALL VERIFICATIONS PASSED!")
    print("="*70)
    print("\nConclusion:")
    print("  ✓ SmartDownloader correctly uses proxy ONLY for metadata")
    print("  ✓ Video downloads are direct (no proxy)")
    print("  ✓ Bandwidth savings: 99%")
    print("  ✓ Cost savings: 99%")
    print()
    print("You can safely use SmartDownloader for production! 🚀")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
