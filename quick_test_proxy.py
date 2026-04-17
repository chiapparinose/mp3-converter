#!/usr/bin/env python3
"""
Quick Proxy Test - Test 1 proxy cepat
"""

import sys
import time
from src.smart_downloader import SmartDownloader

TEST_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def quick_test(proxy_line):
    """Quick test single proxy."""
    
    # Normalize proxy format
    if not any(proxy_line.startswith(p) for p in ['http://', 'https://', 'socks5://']):
        if ':' in proxy_line:
            proxy = f"http://{proxy_line}"
        else:
            print(f"❌ Invalid proxy format: {proxy_line}")
            return False
    else:
        proxy = proxy_line
    
    print(f"\nTesting proxy: {proxy}")
    print("-"*50)
    
    try:
        downloader = SmartDownloader(
            proxy=proxy,
            use_cookies=False,
            rotate_user_agent=True
        )
        
        print("Getting metadata...")
        start = time.time()
        metadata = downloader.get_video_info(TEST_URL)
        elapsed = time.time() - start
        
        if metadata:
            print(f"✓ SUCCESS ({elapsed:.1f}s)")
            print(f"  Title: {metadata.title}")
            print(f"  Channel: {metadata.channel}")
            print(f"  Duration: {metadata.duration}s")
            return True
        else:
            print(f"✗ FAILED - No metadata")
            return False
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return False
    except Exception as e:
        error_msg = str(e)
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        print(f"✗ ERROR: {error_msg}")
        return False


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python3 quick_test_proxy.py <proxy>")
        print("\nExamples:")
        print("  python3 quick_test_proxy.py '1.2.3.4:8080'")
        print("  python3 quick_test_proxy.py 'http://1.2.3.4:8080'")
        print("  python3 quick_test_proxy.py 'http://user:pass@proxy.com:8080'")
        print("\nOr test from proxies.txt:")
        print("  python3 quick_test_proxy.py --file")
        sys.exit(1)
    
    if sys.argv[1] == '--file':
        # Test first proxy from file
        try:
            with open('proxies.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        print(f"\nTesting first proxy from proxies.txt...")
                        quick_test(line)
                        break
        except FileNotFoundError:
            print("❌ proxies.txt not found")
    else:
        quick_test(sys.argv[1])


if __name__ == "__main__":
    main()
