#!/usr/bin/env python3
"""
Test YouTube to MP3 Converter with Residential Proxy
This script tests rate limiting bypass using residential proxy.
"""

import sys
import time
from src.video_downloader import VideoDownloader

# Test URLs
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
]

def test_with_proxy(proxy_url: str, num_requests: int = 25):
    """
    Test video info extraction with proxy.
    
    Args:
        proxy_url: Proxy URL (e.g., 'http://user:pass@proxy.com:8080')
        num_requests: Number of requests to test
    """
    print("\n" + "="*70)
    print("YouTube to MP3 Converter - Proxy Test")
    print("="*70)
    print(f"\nProxy: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")
    print(f"Requests: {num_requests}")
    print("\n" + "-"*70 + "\n")
    
    # Initialize downloader with proxy
    downloader = VideoDownloader(
        use_cookies=False,  # Disable cookies for clean test
        rotate_user_agent=True,
        proxy=proxy_url
    )
    
    success = 0
    failed = 0
    rate_limited = 0
    start_time = time.time()
    
    # Generate test URLs
    urls = [TEST_URLS[i % len(TEST_URLS)] for i in range(num_requests)]
    
    print("Testing...")
    for i, url in enumerate(urls):
        print(f"[{i+1}/{num_requests}]", end=' ', flush=True)
        
        try:
            info = downloader.get_video_info(url)
            if info:
                success += 1
                print("✓", end='', flush=True)
            else:
                failed += 1
                print("✗", end='', flush=True)
        except Exception as e:
            error_msg = str(e).lower()
            if any(kw in error_msg for kw in ['rate limit', 'bot', '429', 'sign in', 'captcha']):
                rate_limited += 1
                print("⚠️", end='', flush=True)
            else:
                failed += 1
                print("✗", end='', flush=True)
        
        # Progress indicator every 10 requests
        if (i + 1) % 10 == 0:
            print(f" [{success}/{i+1}]", end='', flush=True)
    
    total_time = time.time() - start_time
    
    # Results
    print(f"\n\n{'='*70}")
    print("RESULTS")
    print("="*70)
    print(f"\n✓ Success: {success}/{num_requests} ({success/num_requests*100:.1f}%)")
    print(f"✗ Failed: {failed}")
    print(f"⚠️  Rate Limited: {rate_limited}")
    print(f"⏱️  Time: {total_time:.1f}s ({num_requests/total_time*60:.1f} req/min)")
    print()
    
    # Verdict
    if rate_limited == 0 and success >= num_requests * 0.95:
        print("🎉 EXCELLENT - Proxy works perfectly!")
        print("   Recommendation: Use this proxy for production")
    elif rate_limited <= num_requests * 0.1 and success >= num_requests * 0.8:
        print("✓ GOOD - Proxy works well")
        print("   Recommendation: Use with 1-2s delays for better results")
    elif rate_limited <= num_requests * 0.3 and success >= num_requests * 0.6:
        print("⚠️  FAIR - Proxy has some issues")
        print("   Recommendation: Try different proxy or add longer delays")
    else:
        print("❌ POOR - Proxy not working")
        print("   Recommendation: Try different proxy provider")
    
    print("\n" + "="*70 + "\n")
    
    return success, failed, rate_limited


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("Usage: python3 test_with_proxy.py <proxy_url> [num_requests]")
        print("="*70)
        print("\nExamples:")
        print("  python3 test_with_proxy.py 'http://user:pass@proxy.com:8080'")
        print("  python3 test_with_proxy.py 'http://user:pass@proxy.com:8080' 50")
        print("  python3 test_with_proxy.py 'socks5://user:pass@proxy.com:1080'")
        print("\nProxy Formats:")
        print("  HTTP:   http://username:password@proxy.com:8080")
        print("  HTTPS:  https://username:password@proxy.com:8080")
        print("  SOCKS5: socks5://username:password@proxy.com:1080")
        print("\nRecommended Proxy Providers:")
        print("  • IPRoyal: https://iproyal.com (Cheapest - $1.75/GB)")
        print("  • Smartproxy: https://smartproxy.com ($75/month for 8GB)")
        print("  • Bright Data: https://brightdata.com (Premium)")
        print("\n" + "="*70 + "\n")
        sys.exit(1)
    
    proxy_url = sys.argv[1]
    num_requests = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    
    # Run test
    test_with_proxy(proxy_url, num_requests)


if __name__ == "__main__":
    main()
