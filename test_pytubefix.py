#!/usr/bin/env python3
"""
Test pytubefix library - check if it can bypass rate limiting
"""

import sys

try:
    from pytubefix import YouTube
    print("✓ pytubefix imported successfully")
except ImportError:
    print("✗ pytubefix not installed")
    print("Installing pytubefix...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytubefix"])
    from pytubefix import YouTube
    print("✓ pytubefix installed and imported")

# Test URLs
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
]

print("\n" + "="*60)
print("Testing pytubefix - Rate Limiting Check")
print("="*60)
print(f"Test URLs: {len(TEST_URLS)}")
print("="*60 + "\n")

success = 0
failed = 0

for i, url in enumerate(TEST_URLS):
    print(f"[{i+1}/{len(TEST_URLS)}] {url}")
    
    try:
        yt = YouTube(url)
        
        # Try to get metadata
        title = yt.title
        duration = yt.length
        author = yt.author
        
        print(f"  ✓ Title: {title}")
        print(f"  ✓ Duration: {duration}s")
        print(f"  ✓ Author: {author}")
        
        # Try to get streams
        streams = yt.streams.filter(only_audio=True).first()
        if streams:
            print(f"  ✓ Audio stream available: {streams.mime_type}")
            success += 1
        else:
            print(f"  ✗ No audio stream available")
            failed += 1
    
    except Exception as e:
        failed += 1
        error_msg = str(e)
        print(f"  ✗ Error: {error_msg[:100]}")
        
        # Check for specific errors
        if "Sign in" in error_msg or "bot" in error_msg:
            print(f"  ⚠️  BOT DETECTION ERROR")
        elif "HTTP Error 429" in error_msg:
            print(f"  ⚠️  RATE LIMIT ERROR")
    
    print()

# Summary
print("="*60)
print("RESULTS")
print("="*60)
print(f"✓ Success: {success}/{len(TEST_URLS)}")
print(f"✗ Failed: {failed}/{len(TEST_URLS)}")
print()

if success == len(TEST_URLS):
    print("🎉 EXCELLENT - pytubefix works perfectly!")
    print("   No rate limiting detected")
elif success > 0:
    print("⚠️  PARTIAL - Some videos worked")
    print("   May have rate limiting issues")
else:
    print("❌ FAILED - pytubefix blocked")
    print("   Rate limiting or bot detection active")

print("="*60 + "\n")
