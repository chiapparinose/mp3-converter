#!/usr/bin/env python3
"""
Test script untuk proxies.txt yang sudah ada
Test langsung dengan proxy dari file
"""

import sys
from src.proxy_manager import ProxyManager
from src.smart_downloader import SmartDownloader

# Test URL
TEST_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_proxies_from_file():
    """Test proxies from proxies.txt file."""
    
    print("\n" + "="*70)
    print("Testing Proxies from proxies.txt")
    print("="*70)
    print()
    
    # Load proxies
    proxy_manager = ProxyManager(
        proxies_file="proxies.txt",
        rotation_mode="round-robin",
        skip_unhealthy=True
    )
    
    if not proxy_manager.has_proxies():
        print("❌ No proxies loaded from proxies.txt")
        return
    
    print(f"✓ Loaded {proxy_manager.get_proxy_count()} proxies")
    print()
    
    # Test first 5 proxies
    num_tests = min(5, proxy_manager.get_proxy_count())
    print(f"Testing first {num_tests} proxies with metadata request...")
    print("-"*70)
    print()
    
    success = 0
    failed = 0
    
    for i in range(num_tests):
        proxy = proxy_manager.get_next_proxy()
        print(f"[{i+1}/{num_tests}] Testing proxy: {proxy}")
        
        try:
            # Create smart downloader with this proxy
            downloader = SmartDownloader(
                proxy=proxy,
                use_cookies=False,
                rotate_user_agent=True
            )
            
            # Try to get metadata (via proxy)
            print(f"  → Getting metadata via proxy...")
            metadata = downloader.get_video_info(TEST_URL)
            
            if metadata:
                success += 1
                proxy_manager.report_success(proxy)
                print(f"  ✓ SUCCESS")
                print(f"    Title: {metadata.title}")
                print(f"    Duration: {metadata.duration}s")
            else:
                failed += 1
                proxy_manager.report_failure(proxy)
                print(f"  ✗ FAILED - No metadata returned")
        
        except Exception as e:
            failed += 1
            proxy_manager.report_failure(proxy)
            print(f"  ✗ ERROR: {str(e)[:100]}")
        
        print()
    
    # Summary
    print("="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"\n✓ Success: {success}/{num_tests} ({success/num_tests*100:.1f}%)")
    print(f"✗ Failed: {failed}/{num_tests} ({failed/num_tests*100:.1f}%)")
    print()
    
    if success > 0:
        print("✓ At least some proxies are working!")
        print("  You can use batch_smart_proxy_file.py for batch conversion")
    else:
        print("❌ All tested proxies failed")
        print("  Possible issues:")
        print("    - Proxies require authentication (username:password)")
        print("    - Proxies are not working")
        print("    - Network connectivity issues")
    
    print()
    
    # Show proxy stats
    proxy_manager.print_stats()


def main():
    """Main function."""
    print("\n" + "="*70)
    print("Proxy File Test Script")
    print("="*70)
    print("\nThis script will:")
    print("  1. Load proxies from proxies.txt")
    print("  2. Test first 5 proxies with metadata request")
    print("  3. Show which proxies are working")
    print("="*70)
    
    test_proxies_from_file()


if __name__ == "__main__":
    main()
