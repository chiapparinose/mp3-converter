#!/usr/bin/env python3
"""
Progressive Test: Find the Best Rate Limiting Bypass Method

This script tests different bypass methods progressively:
1. No bypass (baseline)
2. User agent rotation only
3. User agent + delays
4. Browser cookies + user agent
5. All methods combined

Stops at first method that works well, or continues to find the best one.
"""

import sys
import time
import logging
from datetime import datetime
from src.video_downloader import VideoDownloader
from src.video_cache import VideoCache

# Setup logging
logging.basicConfig(
    level=logging.WARNING,  # Less verbose
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test URLs - using popular videos that are unlikely to be deleted
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Luis Fonsi - Despacito
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",  # Ed Sheeran - Shape of You
    "https://www.youtube.com/watch?v=OPf0YbXqDm0",  # Mark Ronson - Uptown Funk
    "https://www.youtube.com/watch?v=fRh_vgS2dFE",  # Justin Bieber - Sorry
    "https://www.youtube.com/watch?v=RgKAFK5djSk",  # Wiz Khalifa - See You Again
    "https://www.youtube.com/watch?v=CevxZvSJLk8",  # Katy Perry - Roar
    "https://www.youtube.com/watch?v=nfWlot6h_JM",  # Taylor Swift - Shake It Off
    "https://www.youtube.com/watch?v=hT_nvWreIhg",  # OneRepublic - Counting Stars
]

# Test URLs - using popular videos that are unlikely to be deleted
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Luis Fonsi - Despacito
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",  # Ed Sheeran - Shape of You
    "https://www.youtube.com/watch?v=OPf0YbXqDm0",  # Mark Ronson - Uptown Funk
]

def test_method(method_name, downloader, cache, num_requests=25, delay=0):
    """
    Test a specific bypass method.
    
    Returns:
        dict with results (success_rate, rate_limited_count, etc.)
    """
    print(f"\n{'='*80}")
    print(f"Testing: {method_name} ({num_requests} requests, delay={delay}s)")
    print(f"{'='*80}")
    
    stats = {
        'method': method_name,
        'total': 0,
        'successful': 0,
        'failed': 0,
        'rate_limited': 0,
        'cache_hits': 0,
        'start_time': time.time()
    }
    
    # Generate URLs by cycling
    urls = [TEST_URLS[i % len(TEST_URLS)] for i in range(num_requests)]
    
    for i, url in enumerate(urls):
        request_num = i + 1
        stats['total'] = request_num
        
        # Check cache
        video_id = cache.extract_video_id(url) if cache else None
        cache_hit = cache.has(video_id) if (cache and video_id) else False
        
        if cache_hit:
            stats['cache_hits'] += 1
        
        print(f"[{request_num}/{num_requests}]", end=' ', flush=True)
        
        try:
            video_info = downloader.get_video_info(url)
            
            if video_info:
                stats['successful'] += 1
                print("✓", end='', flush=True)
                
                # Cache it
                if cache and video_id and not cache_hit:
                    cache.set(video_id, {
                        'title': video_info.title,
                        'channel': video_info.channel,
                        'duration': video_info.duration
                    })
            else:
                stats['failed'] += 1
                print("✗", end='', flush=True)
        
        except Exception as e:
            stats['failed'] += 1
            error_msg = str(e).lower()
            
            # Check if rate limited
            is_rate_limit = any(keyword in error_msg for keyword in [
                'rate limit', 'too many requests', 'bot', 'captcha', '429', 'sign in'
            ])
            
            if is_rate_limit:
                stats['rate_limited'] += 1
                print("⚠️", end='', flush=True)
                
                # Stop early if rate limited multiple times
                if stats['rate_limited'] >= 3:
                    print(f"\n\n❌ FAILED: Rate limited {stats['rate_limited']} times at request {request_num}.")
                    break
            else:
                print("✗", end='', flush=True)
        
        # Progress indicator every 25 requests
        if request_num % 25 == 0:
            success_rate = (stats['successful'] / request_num) * 100
            print(f" [{success_rate:.0f}%]", end='', flush=True)
        
        # Delay
        if request_num < num_requests and delay > 0:
            time.sleep(delay)
    
    # Calculate results
    total_time = time.time() - stats['start_time']
    stats['success_rate'] = (stats['successful'] / stats['total']) * 100 if stats['total'] > 0 else 0
    stats['total_time'] = total_time
    stats['requests_per_minute'] = (stats['total'] / total_time) * 60 if total_time > 0 else 0
    
    # Print summary
    print(f"\n\nResults:")
    print(f"  Success: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
    print(f"  Rate Limited: {stats['rate_limited']}")
    print(f"  Cache Hits: {stats['cache_hits']}")
    print(f"  Time: {total_time:.1f}s ({stats['requests_per_minute']:.1f} req/min)")
    
    # Verdict
    if stats['rate_limited'] == 0 and stats['success_rate'] >= 95:
        print(f"  ✅ EXCELLENT - This method works great!")
        stats['verdict'] = 'excellent'
    elif stats['rate_limited'] <= 2 and stats['success_rate'] >= 80:
        print(f"  ✓ GOOD - This method works well")
        stats['verdict'] = 'good'
    elif stats['rate_limited'] <= 5 and stats['success_rate'] >= 60:
        print(f"  ⚠️  FAIR - This method has some issues")
        stats['verdict'] = 'fair'
    else:
        print(f"  ❌ POOR - This method doesn't work well")
        stats['verdict'] = 'poor'
    
    return stats


def progressive_test():
    """Test ALL methods to compare their performance."""
    
    print("=" * 80)
    print("Complete Rate Limiting Bypass Test - ALL METHODS")
    print("=" * 80)
    print()
    print("Strategy:")
    print("  1. Test EVERY method with 25 requests first")
    print("  2. If successful (no rate limit), test 100 requests without delay")
    print("  3. Compare all methods to find the best one")
    print()
    
    all_results = []
    
    # Method 1: No bypass (baseline)
    print("\n" + "="*80)
    print("METHOD 1: No Bypass (Baseline)")
    print("="*80)
    
    downloader1 = VideoDownloader(
        use_cookies=False,
        rotate_user_agent=False
    )
    
    # Test 25 first
    result1_25 = test_method(
        "No Bypass - 25 req",
        downloader1,
        cache=None,
        num_requests=25,
        delay=0
    )
    all_results.append(result1_25)
    
    # If excellent, test 100
    if result1_25['verdict'] == 'excellent':
        print("\n✅ 25 requests successful! Testing 100 requests...")
        time.sleep(2)
        
        result1_100 = test_method(
            "No Bypass - 100 req",
            downloader1,
            cache=None,
            num_requests=100,
            delay=0
        )
        all_results.append(result1_100)
    
    # Method 2: User Agent Rotation Only
    print("\n" + "="*80)
    print("METHOD 2: User Agent Rotation")
    print("="*80)
    
    downloader2 = VideoDownloader(
        use_cookies=False,
        rotate_user_agent=True
    )
    
    result2_25 = test_method(
        "User Agent Rotation - 25 req",
        downloader2,
        cache=None,
        num_requests=25,
        delay=0
    )
    all_results.append(result2_25)
    
    if result2_25['verdict'] == 'excellent':
        print("\n✅ 25 requests successful! Testing 100 requests...")
        time.sleep(2)
        
        result2_100 = test_method(
            "User Agent Rotation - 100 req",
            downloader2,
            cache=None,
            num_requests=100,
            delay=0
        )
        all_results.append(result2_100)
    
    # Method 3: Browser Cookies + User Agent
    print("\n" + "="*80)
    print("METHOD 3: Browser Cookies + User Agent")
    print("="*80)
    
    downloader3 = VideoDownloader(
        use_cookies=True,
        cookies_browser='chrome',
        rotate_user_agent=True
    )
    
    result3_25 = test_method(
        "Cookies + User Agent - 25 req",
        downloader3,
        cache=None,
        num_requests=25,
        delay=0
    )
    all_results.append(result3_25)
    
    if result3_25['verdict'] == 'excellent':
        print("\n✅ 25 requests successful! Testing 100 requests...")
        time.sleep(2)
        
        result3_100 = test_method(
            "Cookies + User Agent - 100 req",
            downloader3,
            cache=None,
            num_requests=100,
            delay=0
        )
        all_results.append(result3_100)
    
    # Method 4: All Methods + Cache (no delay)
    print("\n" + "="*80)
    print("METHOD 4: All Methods + Cache (No Delay)")
    print("="*80)
    print("  - Browser Cookies")
    print("  - User Agent Rotation")
    print("  - Metadata Caching")
    print("  - Exponential Backoff")
    
    downloader4 = VideoDownloader(
        use_cookies=True,
        cookies_browser='chrome',
        rotate_user_agent=True
    )
    
    cache4 = VideoCache(cache_file='test_cache_method4.json')
    
    result4_25 = test_method(
        "All Methods + Cache - 25 req",
        downloader4,
        cache=cache4,
        num_requests=25,
        delay=0
    )
    all_results.append(result4_25)
    
    if result4_25['verdict'] == 'excellent':
        print("\n✅ 25 requests successful! Testing 100 requests...")
        time.sleep(2)
        
        result4_100 = test_method(
            "All Methods + Cache - 100 req",
            downloader4,
            cache=cache4,
            num_requests=100,
            delay=0
        )
        all_results.append(result4_100)
    
    # Method 5: All Methods + Cache + 1s Delays
    print("\n" + "="*80)
    print("METHOD 5: All Methods + Cache + 1s Delays")
    print("="*80)
    print("  - Browser Cookies")
    print("  - User Agent Rotation")
    print("  - Metadata Caching")
    print("  - Exponential Backoff")
    print("  - 1 second delays")
    
    downloader5 = VideoDownloader(
        use_cookies=True,
        cookies_browser='chrome',
        rotate_user_agent=True
    )
    
    cache5 = VideoCache(cache_file='test_cache_method5.json')
    
    result5_25 = test_method(
        "All Methods + Cache + 1s Delays - 25 req",
        downloader5,
        cache=cache5,
        num_requests=25,
        delay=1
    )
    all_results.append(result5_25)
    
    if result5_25['verdict'] in ['excellent', 'good']:
        print("\n✅ 25 requests successful! Testing 100 requests...")
        time.sleep(2)
        
        result5_100 = test_method(
            "All Methods + Cache + 1s Delays - 100 req",
            downloader5,
            cache=cache5,
            num_requests=100,
            delay=1
        )
        all_results.append(result5_100)
    
    return all_results


def main():
    """Main entry point."""
    try:
        print("\n")
        results = progressive_test()
        
        # Final comparison
        print("\n\n" + "="*80)
        print("FINAL COMPARISON")
        print("="*80)
        print()
        
        print(f"{'Method':<40} {'Success Rate':<15} {'Rate Limited':<15} {'Verdict':<15}")
        print("-" * 80)
        
        for result in results:
            print(f"{result['method']:<40} "
                  f"{result['success_rate']:>6.1f}% ({result['successful']}/{result['total']})  "
                  f"{result['rate_limited']:>6}          "
                  f"{result['verdict']:<15}")
        
        print()
        print("="*80)
        print()
        
        # Find best method
        best = max(results, key=lambda x: (x['success_rate'], -x['rate_limited']))
        
        print("RECOMMENDATION:")
        print()
        print(f"✅ Best Method: {best['method']}")
        print(f"   Success Rate: {best['success_rate']:.1f}%")
        print(f"   Rate Limited: {best['rate_limited']} times")
        print(f"   Speed: {best['requests_per_minute']:.1f} requests/minute")
        print()
        
        if best['verdict'] == 'excellent':
            print("🎉 This method achieves near-unlimited access!")
        elif best['verdict'] == 'good':
            print("✓ This method works well for most use cases.")
        else:
            print("⚠️  All methods have limitations. Consider:")
            print("   - YouTube Data API for high-volume applications")
            print("   - Longer delays between requests")
            print("   - Distributed system with multiple IPs")
        
        print()
        print("="*80)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
