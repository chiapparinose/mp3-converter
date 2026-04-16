#!/usr/bin/env python3
"""
Complete Test of ALL Bypass Methods (Without Chrome Cookies)

Tests all possible combinations:
1. No Bypass (baseline)
2. User Agent Rotation only
3. Cache only
4. User Agent + Cache
5. User Agent + Cache + 1s Delays
6. User Agent + Cache + 2s Delays
"""

import sys
import time
from src.video_downloader import VideoDownloader
from src.video_cache import VideoCache

TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
    "https://www.youtube.com/watch?v=JGwWNGJdvx8",
    "https://www.youtube.com/watch?v=OPf0YbXqDm0",
]

def test_method(method_name, downloader, cache, num_requests=100, delay=0):
    """Test a specific method."""
    print(f"\n{'='*80}")
    print(f"{method_name}")
    print(f"{'='*80}")
    print(f"Requests: {num_requests}, Delay: {delay}s")
    print()
    
    stats = {
        'method': method_name,
        'total': 0,
        'successful': 0,
        'failed': 0,
        'rate_limited': 0,
        'cache_hits': 0,
        'start_time': time.time()
    }
    
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
            
            is_rate_limit = any(kw in error_msg for kw in [
                'rate limit', 'too many requests', 'bot', 'captcha', '429', 'sign in'
            ])
            
            if is_rate_limit:
                stats['rate_limited'] += 1
                print("⚠️", end='', flush=True)
                
                if stats['rate_limited'] >= 3:
                    print(f"\n\n❌ Rate limited {stats['rate_limited']} times. Stopping.")
                    break
            else:
                print("✗", end='', flush=True)
        
        # Progress every 25
        if request_num % 25 == 0:
            success_rate = (stats['successful'] / request_num) * 100
            print(f" [{success_rate:.0f}%]", end='', flush=True)
        
        # Delay
        if request_num < num_requests and delay > 0:
            time.sleep(delay)
    
    # Results
    total_time = time.time() - stats['start_time']
    stats['success_rate'] = (stats['successful'] / stats['total']) * 100 if stats['total'] > 0 else 0
    stats['total_time'] = total_time
    stats['requests_per_minute'] = (stats['total'] / total_time) * 60 if total_time > 0 else 0
    
    print(f"\n\n📊 Results:")
    print(f"  Success: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
    print(f"  Failed: {stats['failed']}")
    print(f"  Rate Limited: {stats['rate_limited']}")
    print(f"  Cache Hits: {stats['cache_hits']}")
    print(f"  Time: {total_time:.1f}s ({stats['requests_per_minute']:.1f} req/min)")
    
    # Verdict
    if stats['rate_limited'] == 0 and stats['success_rate'] >= 95:
        print(f"  ✅ EXCELLENT")
        stats['verdict'] = 'excellent'
    elif stats['rate_limited'] <= 2 and stats['success_rate'] >= 80:
        print(f"  ✓ GOOD")
        stats['verdict'] = 'good'
    else:
        print(f"  ❌ POOR")
        stats['verdict'] = 'poor'
    
    return stats

def main():
    """Test all methods."""
    print("\n" + "="*80)
    print("COMPLETE BYPASS METHODS TEST")
    print("="*80)
    print("\nTesting ALL bypass method combinations (100 requests each)")
    print("Excluding browser cookies (Chrome locked issue)")
    print()
    
    all_results = []
    
    # Method 1: No Bypass
    print("\n" + "="*80)
    print("METHOD 1: No Bypass (Baseline)")
    print("="*80)
    
    downloader1 = VideoDownloader(use_cookies=False, rotate_user_agent=False)
    result1 = test_method("No Bypass", downloader1, None, 100, 0)
    all_results.append(result1)
    
    time.sleep(3)
    
    # Method 2: User Agent Rotation Only
    print("\n" + "="*80)
    print("METHOD 2: User Agent Rotation")
    print("="*80)
    
    downloader2 = VideoDownloader(use_cookies=False, rotate_user_agent=True)
    result2 = test_method("User Agent Rotation", downloader2, None, 100, 0)
    all_results.append(result2)
    
    time.sleep(3)
    
    # Method 3: Cache Only
    print("\n" + "="*80)
    print("METHOD 3: Metadata Caching")
    print("="*80)
    
    downloader3 = VideoDownloader(use_cookies=False, rotate_user_agent=False)
    cache3 = VideoCache(cache_file='test_cache3.json')
    result3 = test_method("Metadata Caching", downloader3, cache3, 100, 0)
    all_results.append(result3)
    
    time.sleep(3)
    
    # Method 4: User Agent + Cache
    print("\n" + "="*80)
    print("METHOD 4: User Agent + Cache")
    print("="*80)
    
    downloader4 = VideoDownloader(use_cookies=False, rotate_user_agent=True)
    cache4 = VideoCache(cache_file='test_cache4.json')
    result4 = test_method("User Agent + Cache", downloader4, cache4, 100, 0)
    all_results.append(result4)
    
    time.sleep(3)
    
    # Method 5: User Agent + Cache + 1s Delays
    print("\n" + "="*80)
    print("METHOD 5: User Agent + Cache + 1s Delays")
    print("="*80)
    
    downloader5 = VideoDownloader(use_cookies=False, rotate_user_agent=True)
    cache5 = VideoCache(cache_file='test_cache5.json')
    result5 = test_method("User Agent + Cache + 1s Delays", downloader5, cache5, 100, 1)
    all_results.append(result5)
    
    time.sleep(3)
    
    # Method 6: User Agent + Cache + 2s Delays
    print("\n" + "="*80)
    print("METHOD 6: User Agent + Cache + 2s Delays")
    print("="*80)
    
    downloader6 = VideoDownloader(use_cookies=False, rotate_user_agent=True)
    cache6 = VideoCache(cache_file='test_cache6.json')
    result6 = test_method("User Agent + Cache + 2s Delays", downloader6, cache6, 100, 2)
    all_results.append(result6)
    
    # Final comparison
    print("\n\n" + "="*80)
    print("FINAL COMPARISON - ALL METHODS")
    print("="*80)
    print()
    
    print(f"{'Method':<40} {'Success':<15} {'Rate Limited':<15} {'Speed (req/min)':<20} {'Verdict'}")
    print("-" * 100)
    
    for result in all_results:
        print(f"{result['method']:<40} "
              f"{result['success_rate']:>6.1f}% ({result['successful']}/{result['total']})  "
              f"{result['rate_limited']:>6}          "
              f"{result['requests_per_minute']:>10.1f}          "
              f"{result['verdict']}")
    
    print()
    print("="*80)
    print()
    
    # Find best
    best = max(all_results, key=lambda x: (x['success_rate'], -x['rate_limited'], x['requests_per_minute']))
    
    print("🏆 BEST METHOD:")
    print(f"   {best['method']}")
    print(f"   Success: {best['success_rate']:.1f}%")
    print(f"   Rate Limited: {best['rate_limited']} times")
    print(f"   Speed: {best['requests_per_minute']:.1f} req/min")
    print(f"   Cache Hits: {best['cache_hits']}")
    print()
    
    # Analysis
    print("="*80)
    print("ANALYSIS")
    print("="*80)
    print()
    
    excellent_count = sum(1 for r in all_results if r['verdict'] == 'excellent')
    
    if excellent_count >= 4:
        print("✅ UNLIMITED ACCESS CONFIRMED!")
        print("   Multiple methods achieve 100% success rate.")
        print("   YouTube is NOT enforcing rate limits currently.")
    elif excellent_count >= 2:
        print("✓ GOOD ACCESS")
        print("   Several methods work well.")
        print("   Some bypass methods provide benefits.")
    else:
        print("⚠️  LIMITED ACCESS")
        print("   Rate limiting is being enforced.")
        print("   Bypass methods are necessary.")
    
    print()
    print("="*80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
