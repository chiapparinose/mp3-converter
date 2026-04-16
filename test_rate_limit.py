#!/usr/bin/env python3
"""
YouTube Rate Limit Test

This script tests how many requests can be made to YouTube before rate limiting occurs.
WARNING: This may trigger YouTube's rate limiting. Use responsibly.
"""

import time
import sys
from datetime import datetime
from src.url_validator import URLValidator

def test_rate_limit(max_requests=50, delay_between_requests=0):
    """
    Test YouTube rate limiting by making multiple requests.
    
    Args:
        max_requests: Maximum number of requests to test
        delay_between_requests: Delay in seconds between requests (0 = no delay)
    """
    print("=" * 70)
    print("YouTube Rate Limit Test")
    print("=" * 70)
    print(f"Max requests: {max_requests}")
    print(f"Delay between requests: {delay_between_requests}s")
    print()
    
    # Test URLs - using different videos to avoid caching
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Gangnam Style
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito
        "https://www.youtube.com/watch?v=JGwWNGJdvx8",  # Shape of You
        "https://www.youtube.com/watch?v=OPf0YbXqDm0",  # Uptown Funk
    ]
    
    validator = URLValidator()
    
    successful_requests = 0
    failed_requests = 0
    rate_limited = False
    start_time = time.time()
    
    print("Starting requests...")
    print("-" * 70)
    
    for i in range(max_requests):
        # Rotate through test URLs
        url = test_urls[i % len(test_urls)]
        
        try:
            request_start = time.time()
            
            # Try to get video info (this makes actual request to YouTube)
            video_info = validator.get_video_info(url)
            
            request_time = time.time() - request_start
            
            if video_info:
                successful_requests += 1
                status = "✓"
                result = f"OK ({request_time:.2f}s)"
            else:
                failed_requests += 1
                status = "✗"
                result = "Failed to get info"
                
                # Check if this might be rate limiting
                if failed_requests > 3:
                    rate_limited = True
                    print(f"\n⚠️  Multiple failures detected - possible rate limiting!")
                    break
            
            print(f"Request {i+1:3d}/{max_requests}: {status} {result}")
            
            # Add delay if specified
            if delay_between_requests > 0 and i < max_requests - 1:
                time.sleep(delay_between_requests)
                
        except Exception as e:
            failed_requests += 1
            print(f"Request {i+1:3d}/{max_requests}: ✗ Error: {str(e)[:50]}")
            
            # Check for rate limiting errors
            error_str = str(e).lower()
            if 'too many requests' in error_str or '429' in error_str or 'rate limit' in error_str:
                rate_limited = True
                print(f"\n⚠️  Rate limiting detected!")
                break
    
    total_time = time.time() - start_time
    
    # Results
    print("-" * 70)
    print("\nResults:")
    print(f"  Total requests: {successful_requests + failed_requests}")
    print(f"  Successful: {successful_requests}")
    print(f"  Failed: {failed_requests}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average time per request: {total_time / (successful_requests + failed_requests):.2f}s")
    
    if rate_limited:
        print(f"\n⚠️  Rate limiting occurred after {successful_requests} successful requests")
        print(f"  Recommendation: Add delay between requests or reduce frequency")
    else:
        print(f"\n✓ No rate limiting detected in {successful_requests} requests")
        print(f"  Note: YouTube's limits may vary based on IP, time, and usage patterns")
    
    print("\n" + "=" * 70)
    
    return {
        'successful': successful_requests,
        'failed': failed_requests,
        'rate_limited': rate_limited,
        'total_time': total_time
    }

def test_with_delays():
    """Test with different delay strategies."""
    print("\n" + "=" * 70)
    print("Testing Different Delay Strategies")
    print("=" * 70)
    
    strategies = [
        ("No delay", 10, 0),
        ("1 second delay", 10, 1),
        ("2 second delay", 10, 2),
    ]
    
    results = []
    
    for name, requests, delay in strategies:
        print(f"\n\nStrategy: {name}")
        print("-" * 70)
        result = test_rate_limit(max_requests=requests, delay_between_requests=delay)
        results.append((name, result))
        
        # Wait between strategies to avoid triggering rate limits
        if delay == 0:
            print("\nWaiting 30 seconds before next strategy...")
            time.sleep(30)
    
    # Summary
    print("\n\n" + "=" * 70)
    print("Summary of All Strategies")
    print("=" * 70)
    
    for name, result in results:
        print(f"\n{name}:")
        print(f"  Successful: {result['successful']}/{result['successful'] + result['failed']}")
        print(f"  Rate limited: {'Yes' if result['rate_limited'] else 'No'}")
        print(f"  Avg time: {result['total_time'] / (result['successful'] + result['failed']):.2f}s per request")

def quick_test():
    """Quick test with just a few requests."""
    print("Running quick test (5 requests, no delay)...")
    return test_rate_limit(max_requests=5, delay_between_requests=0)

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            quick_test()
        elif sys.argv[1] == '--full':
            test_rate_limit(max_requests=50, delay_between_requests=0)
        elif sys.argv[1] == '--strategies':
            test_with_delays()
        elif sys.argv[1] == '--help':
            print("Usage:")
            print("  python test_rate_limit.py --quick       # Quick test (5 requests)")
            print("  python test_rate_limit.py --full        # Full test (50 requests)")
            print("  python test_rate_limit.py --strategies  # Test different delays")
            print("  python test_rate_limit.py --help        # Show this help")
            return 0
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
            return 1
    else:
        # Default: quick test
        quick_test()
    
    print("\n⚠️  Important Notes:")
    print("  1. YouTube's rate limits vary by IP address and usage patterns")
    print("  2. Limits may be different for authenticated vs unauthenticated requests")
    print("  3. Using yt-dlp may have different limits than direct API access")
    print("  4. Rate limits reset over time (usually hourly or daily)")
    print("  5. Excessive requests may result in temporary IP blocking")
    print("\n💡 Recommendations:")
    print("  - Add 1-2 second delay between requests for normal use")
    print("  - Implement exponential backoff on failures")
    print("  - Cache video info when possible")
    print("  - Consider using YouTube Data API for high-volume applications")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
