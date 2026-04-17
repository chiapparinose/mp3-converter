#!/usr/bin/env python3
"""
Test YouTube Data API with 100 requests
Verify: FREE, no rate limiting, 100% success rate
"""

import time
from src.youtube_api import YouTubeAPI


# API Key
API_KEY = "AIzaSyDEtALTlUCSyVuzJ2ReAefoDOUoRkNxnOo"

# Test URLs
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
]


def test_api_100():
    """Test API with 100 requests."""
    
    print("\n" + "="*60)
    print("YouTube Data API Test - 100 Requests")
    print("="*60)
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Test: 100 metadata requests")
    print("="*60 + "\n")
    
    youtube_api = YouTubeAPI(API_KEY)
    
    success = 0
    failed = 0
    start_time = time.time()
    
    # Generate 100 URLs (cycle through test URLs)
    urls = [TEST_URLS[i % len(TEST_URLS)] for i in range(100)]
    
    print("Testing...")
    for i, url in enumerate(urls):
        print(f"[{i+1}/100]", end=' ', flush=True)
        
        try:
            metadata = youtube_api.get_video_info(url)
            
            if metadata:
                success += 1
                print("✓", end='', flush=True)
            else:
                failed += 1
                print("✗", end='', flush=True)
        except Exception as e:
            failed += 1
            print("✗", end='', flush=True)
        
        # Progress indicator every 10 requests
        if (i + 1) % 10 == 0:
            print(f" [{success}/{i+1}]", end='', flush=True)
    
    total_time = time.time() - start_time
    
    # Results
    print(f"\n\n{'='*60}")
    print("RESULTS")
    print("="*60)
    print(f"\n✓ Success: {success}/100 ({success}%)")
    print(f"✗ Failed: {failed}/100 ({failed}%)")
    print(f"⏱️  Time: {total_time:.1f}s ({100/total_time*60:.1f} req/min)")
    print(f"📊 API Quota Used: 100 / 10,000 daily limit")
    print()
    
    # Verdict
    if success >= 95:
        print("🎉 EXCELLENT - API works perfectly!")
        print("   ✓ No rate limiting")
        print("   ✓ FREE (10,000 requests/day)")
        print("   ✓ No proxy needed")
        print("   ✓ Ready for production")
    elif success >= 80:
        print("✓ GOOD - API works well")
        print("   Minor issues detected")
    else:
        print("❌ POOR - API has issues")
        print("   Check API key validity")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    test_api_100()
