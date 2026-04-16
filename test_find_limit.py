#!/usr/bin/env python3
"""
Find the Actual Rate Limit

Test progressively larger batches to find where rate limiting kicks in:
- 25 requests (baseline)
- 50 requests
- 100 requests
- 200 requests (if still working)

Stop when rate limited.
"""

import sys
import time
from src.video_downloader import VideoDownloader

TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    "https://www.youtube.com/watch?v=OPf0YbXqDm0",
]

def test_batch(num_requests, delay=0):
    """Test a batch of requests."""
    print(f"\n{'='*80}")
    print(f"Testing {num_requests} Requests (delay={delay}s)")
    print(f"{'='*80}\n")
    
    downloader = VideoDownloader(use_cookies=False, rotate_user_agent=False)
    
    stats = {
        'total': 0,
        'successful': 0,
        'rate_limited': 0,
        'start_time': time.time()
    }
    
    urls = [TEST_URLS[i % len(TEST_URLS)] for i in range(num_requests)]
    
    for i, url in enumerate(urls):
        request_num = i + 1
        stats['total'] = request_num
        
        print(f"[{request_num}/{num_requests}]", end=' ', flush=True)
        
        try:
            video_info = downloader.get_video_info(url)
            
            if video_info:
                stats['successful'] += 1
                print("✓", end='', flush=True)
            else:
                print("✗", end='', flush=True)
        
        except Exception as e:
            error_msg = str(e).lower()
            is_rate_limit = any(kw in error_msg for kw in [
                'rate limit', 'too many requests', 'bot', 'captcha', '429', 'sign in'
            ])
            
            if is_rate_limit:
                stats['rate_limited'] += 1
                print("⚠️", end='', flush=True)
                
                # Stop if rate limited 3 times
                if stats['rate_limited'] >= 3:
                    print(f"\n\n❌ RATE LIMITED at request {request_num}")
                    print(f"   Limit found: ~{request_num - 3} requests")
                    break
            else:
                print("✗", end='', flush=True)
        
        # Delay
        if delay > 0 and request_num < num_requests:
            time.sleep(delay)
        
        # Progress every 25 requests
        if request_num % 25 == 0:
            success_rate = (stats['successful'] / request_num) * 100
            print(f" [{success_rate:.0f}%]", end='', flush=True)
    
    total_time = time.time() - stats['start_time']
    success_rate = (stats['successful'] / stats['total']) * 100
    
    print(f"\n\nResults:")
    print(f"  Success: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")
    print(f"  Rate Limited: {stats['rate_limited']}")
    print(f"  Time: {total_time:.1f}s ({stats['total']/total_time*60:.1f} req/min)")
    
    return stats

def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("Finding YouTube Rate Limit")
    print("="*80)
    print("\nStrategy: Test progressively larger batches until rate limited.")
    print()
    
    # Test 1: 25 requests (baseline)
    result1 = test_batch(25, delay=0)
    
    if result1['rate_limited'] >= 3:
        print("\n❌ Rate limited at 25 requests. Limit is very low.")
        return 1
    
    # Test 2: 50 requests
    print("\n✓ 25 requests successful. Testing 50...")
    time.sleep(5)  # Brief pause
    
    result2 = test_batch(50, delay=0)
    
    if result2['rate_limited'] >= 3:
        print(f"\n⚠️  Rate limit found between 25-50 requests")
        return 0
    
    # Test 3: 100 requests
    print("\n✓ 50 requests successful. Testing 100...")
    time.sleep(5)
    
    result3 = test_batch(100, delay=0)
    
    if result3['rate_limited'] >= 3:
        print(f"\n⚠️  Rate limit found between 50-100 requests")
        return 0
    
    # Test 4: 200 requests (ambitious!)
    print("\n✓ 100 requests successful! Testing 200...")
    time.sleep(10)
    
    result4 = test_batch(200, delay=0)
    
    if result4['rate_limited'] >= 3:
        print(f"\n⚠️  Rate limit found between 100-200 requests")
        return 0
    
    # If we get here, we found no limit!
    print("\n\n" + "="*80)
    print("🎉 AMAZING RESULTS!")
    print("="*80)
    print()
    print("No rate limiting detected even after 200+ requests!")
    print("This is effectively UNLIMITED for normal use cases.")
    print()
    print("Possible reasons:")
    print("  - YouTube updated their rate limiting policy")
    print("  - Residential IP has higher trust")
    print("  - Natural request pattern not flagged as bot")
    print("  - Geographic location has higher limits")
    print()
    print("="*80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
