#!/usr/bin/env python3
"""
Test script to verify all rate limiting bypass implementations.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 70)
    print("Testing Imports")
    print("=" * 70)
    
    try:
        from src.video_downloader import VideoDownloader, USER_AGENTS
        print("✓ VideoDownloader imported successfully")
        print(f"  - {len(USER_AGENTS)} user agents available")
        
        from src.video_cache import VideoCache
        print("✓ VideoCache imported successfully")
        
        from src.conversion_pipeline import ConversionPipeline
        print("✓ ConversionPipeline imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_video_downloader_init():
    """Test VideoDownloader initialization with bypass options."""
    print("\n" + "=" * 70)
    print("Testing VideoDownloader Initialization")
    print("=" * 70)
    
    try:
        from src.video_downloader import VideoDownloader
        
        # Test 1: Default initialization
        downloader1 = VideoDownloader()
        print("✓ Default initialization successful")
        print(f"  - use_cookies: {downloader1.use_cookies}")
        print(f"  - cookies_browser: {downloader1.cookies_browser}")
        print(f"  - rotate_user_agent: {downloader1.rotate_user_agent}")
        
        # Test 2: Custom browser
        downloader2 = VideoDownloader(
            use_cookies=True,
            cookies_browser='firefox',
            rotate_user_agent=True
        )
        print("✓ Custom browser initialization successful")
        print(f"  - cookies_browser: {downloader2.cookies_browser}")
        
        # Test 3: Cookie file
        downloader3 = VideoDownloader(
            use_cookies=True,
            cookies_file='cookies.txt',
            rotate_user_agent=False
        )
        print("✓ Cookie file initialization successful")
        print(f"  - cookies_file: {downloader3.cookies_file}")
        print(f"  - rotate_user_agent: {downloader3.rotate_user_agent}")
        
        # Test 4: Disabled cookies
        downloader4 = VideoDownloader(use_cookies=False)
        print("✓ Disabled cookies initialization successful")
        print(f"  - use_cookies: {downloader4.use_cookies}")
        
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_video_cache():
    """Test VideoCache functionality."""
    print("\n" + "=" * 70)
    print("Testing VideoCache")
    print("=" * 70)
    
    try:
        from src.video_cache import VideoCache
        
        # Test 1: Initialize cache
        cache = VideoCache(cache_file='test_cache.json')
        print("✓ Cache initialized successfully")
        
        # Test 2: Extract video ID
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        ]
        
        for url in test_urls:
            video_id = cache.extract_video_id(url)
            if video_id == "dQw4w9WgXcQ":
                print(f"✓ Extracted video ID from: {url}")
            else:
                print(f"✗ Failed to extract video ID from: {url}")
                return False
        
        # Test 3: Set and get cache
        test_metadata = {
            'title': 'Test Video',
            'channel': 'Test Channel',
            'duration': 180
        }
        
        cache.set('test_video_id', test_metadata)
        print("✓ Metadata cached successfully")
        
        retrieved = cache.get('test_video_id')
        if retrieved == test_metadata:
            print("✓ Metadata retrieved successfully")
        else:
            print("✗ Retrieved metadata doesn't match")
            return False
        
        # Test 4: Check has()
        if cache.has('test_video_id'):
            print("✓ has() method works correctly")
        else:
            print("✗ has() method failed")
            return False
        
        # Test 5: Get stats
        stats = cache.get_stats()
        print("✓ Cache statistics retrieved")
        print(f"  - Total entries: {stats['total_entries']}")
        print(f"  - Cache size: {stats['cache_size_mb']:.4f} MB")
        
        # Test 6: Clear cache
        cache.clear()
        if cache.get_stats()['total_entries'] == 0:
            print("✓ Cache cleared successfully")
        else:
            print("✗ Cache clear failed")
            return False
        
        # Cleanup
        Path('test_cache.json').unlink(missing_ok=True)
        
        return True
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversion_pipeline():
    """Test ConversionPipeline with custom downloader."""
    print("\n" + "=" * 70)
    print("Testing ConversionPipeline with Custom Downloader")
    print("=" * 70)
    
    try:
        from src.video_downloader import VideoDownloader
        from src.conversion_pipeline import ConversionPipeline
        
        # Test 1: Default pipeline
        pipeline1 = ConversionPipeline()
        print("✓ Default pipeline initialized")
        print(f"  - Downloader type: {type(pipeline1.video_downloader).__name__}")
        
        # Test 2: Custom downloader
        custom_downloader = VideoDownloader(
            use_cookies=True,
            cookies_browser='firefox',
            rotate_user_agent=True
        )
        
        pipeline2 = ConversionPipeline(downloader=custom_downloader)
        print("✓ Pipeline with custom downloader initialized")
        print(f"  - Downloader use_cookies: {pipeline2.video_downloader.use_cookies}")
        print(f"  - Downloader cookies_browser: {pipeline2.video_downloader.cookies_browser}")
        print(f"  - Downloader rotate_user_agent: {pipeline2.video_downloader.rotate_user_agent}")
        
        return True
    except Exception as e:
        print(f"✗ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ydl_opts_generation():
    """Test yt-dlp options generation with bypass features."""
    print("\n" + "=" * 70)
    print("Testing yt-dlp Options Generation")
    print("=" * 70)
    
    try:
        from src.video_downloader import VideoDownloader
        
        # Test 1: With cookies and user agent rotation
        downloader = VideoDownloader(
            use_cookies=True,
            cookies_browser='chrome',
            rotate_user_agent=True
        )
        
        def dummy_hook(d):
            pass
        
        opts = downloader._get_ydl_opts(dummy_hook)
        print("✓ yt-dlp options generated successfully")
        print(f"  - Has cookiesfrombrowser: {'cookiesfrombrowser' in opts}")
        print(f"  - Has user_agent: {'user_agent' in opts}")
        print(f"  - Has progress_hooks: {'progress_hooks' in opts}")
        print(f"  - Retries: {opts.get('retries', 'N/A')}")
        
        if 'cookiesfrombrowser' in opts:
            print(f"  - Browser: {opts['cookiesfrombrowser'][0]}")
        
        if 'user_agent' in opts:
            print(f"  - User agent: {opts['user_agent'][:50]}...")
        
        # Test 2: With cookie file
        downloader2 = VideoDownloader(
            use_cookies=True,
            cookies_file='test_cookies.txt'
        )
        
        opts2 = downloader2._get_ydl_opts(dummy_hook)
        print("✓ Options with cookie file generated")
        print(f"  - Has cookiefile: {'cookiefile' in opts2}")
        if 'cookiefile' in opts2:
            print(f"  - Cookie file: {opts2['cookiefile']}")
        
        # Test 3: Without cookies
        downloader3 = VideoDownloader(use_cookies=False)
        opts3 = downloader3._get_ydl_opts(dummy_hook)
        print("✓ Options without cookies generated")
        print(f"  - Has cookiesfrombrowser: {'cookiesfrombrowser' in opts3}")
        print(f"  - Has cookiefile: {'cookiefile' in opts3}")
        
        return True
    except Exception as e:
        print(f"✗ Options generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_agents():
    """Test user agent rotation."""
    print("\n" + "=" * 70)
    print("Testing User Agent Rotation")
    print("=" * 70)
    
    try:
        from src.video_downloader import USER_AGENTS
        import random
        
        print(f"✓ {len(USER_AGENTS)} user agents available")
        
        # Test randomness
        selected = set()
        for _ in range(20):
            ua = random.choice(USER_AGENTS)
            selected.add(ua)
        
        print(f"✓ {len(selected)} unique user agents selected in 20 tries")
        
        # Show all user agents
        print("\nAvailable User Agents:")
        for i, ua in enumerate(USER_AGENTS, 1):
            # Extract browser and OS
            if 'Windows' in ua:
                os = 'Windows'
            elif 'Macintosh' in ua:
                os = 'macOS'
            elif 'Linux' in ua:
                os = 'Linux'
            else:
                os = 'Unknown'
            
            if 'Chrome' in ua and 'Firefox' not in ua:
                browser = 'Chrome'
            elif 'Firefox' in ua:
                browser = 'Firefox'
            else:
                browser = 'Unknown'
            
            print(f"  {i}. {browser} on {os}")
        
        return True
    except Exception as e:
        print(f"✗ User agent test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Rate Limiting Bypass Implementation Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("VideoDownloader Init", test_video_downloader_init),
        ("VideoCache", test_video_cache),
        ("ConversionPipeline", test_conversion_pipeline),
        ("yt-dlp Options", test_ydl_opts_generation),
        ("User Agents", test_user_agents),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
