#!/usr/bin/env python3
"""
YouTube to MP3 Converter using pytubefix
- Uses pytubefix library (fork of pytube with better updates)
- Direct download without API or proxy
- Simple and fast
"""

import os
import sys
import subprocess
from pathlib import Path

try:
    from pytubefix import YouTube
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TALB, TPE1, TIT2, TCON
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("\nInstalling required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytubefix", "mutagen"])
    print("\nDependencies installed. Please run the script again.")
    sys.exit(0)


def sanitize_filename(filename):
    """Remove illegal characters from filename."""
    illegal_chars = ('?', "'", '"', '.', '/', '\\', '*', '^', '%', '$', '#', '~', '<', '>', ',', ';', ':', '|')
    for char in illegal_chars:
        filename = filename.replace(char, '')
    return filename


def download_and_convert(url, output_dir='output', bitrate=192):
    """
    Download YouTube video and convert to MP3.
    
    Args:
        url: YouTube video URL
        output_dir: Output directory for MP3 files
        bitrate: Audio bitrate in kbps (default: 192)
    
    Returns:
        tuple: (success: bool, filename: str, error: str)
    """
    temp_dir = Path(output_dir) / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Get video info
        print(f"  Getting video info...")
        yt = YouTube(url)
        
        title = yt.title
        author = yt.author
        duration = yt.length
        
        # Handle Unicode in title/author
        try:
            print(f"  Title: {title}")
            print(f"  Author: {author}")
        except UnicodeEncodeError:
            print(f"  Title: [Unicode title]")
            print(f"  Author: [Unicode author]")
        
        print(f"  Duration: {duration}s")
        
        # Sanitize filename
        safe_title = sanitize_filename(title)
        mp4_filename = f"{safe_title}.mp4"
        mp3_filename = f"{safe_title}.mp3"
        
        # Download audio stream
        print(f"  Downloading audio...")
        stream = yt.streams.filter(only_audio=True).first()
        
        if not stream:
            return False, None, "No audio stream available"
        
        mp4_path = temp_dir / mp4_filename
        stream.download(output_path=str(temp_dir), filename=mp4_filename)
        
        # Convert to MP3 using ffmpeg
        print(f"  Converting to MP3...")
        mp3_path = Path(output_dir) / mp3_filename
        
        # Use ffmpeg for conversion
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', str(mp4_path),
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-b:a', f'{bitrate}k',
            '-y',  # Overwrite output file
            str(mp3_path)
        ]
        
        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        
        # Add metadata
        print(f"  Adding metadata...")
        audio = MP3(str(mp3_path), ID3=ID3)
        audio["TIT2"] = TIT2(encoding=3, text=title)
        audio["TPE1"] = TPE1(encoding=3, text=author)
        audio["TALB"] = TALB(encoding=3, text="YouTube")
        audio.save()
        
        # Cleanup temp file
        mp4_path.unlink()
        
        # Get file size
        file_size_mb = mp3_path.stat().st_size / (1024 * 1024)
        
        return True, mp3_filename, file_size_mb
    
    except Exception as e:
        error_msg = str(e)
        return False, None, error_msg
    
    finally:
        # Cleanup temp directory
        try:
            if temp_dir.exists() and not list(temp_dir.iterdir()):
                temp_dir.rmdir()
        except:
            pass


def convert_batch(urls_file='urls.txt', output_dir='output', bitrate=192):
    """Convert batch URLs using pytubefix."""
    
    # Load URLs
    try:
        with open(urls_file) as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except:
        print(f"❌ File {urls_file} not found")
        return
    
    print(f"\n{'='*60}")
    print(f"YouTube to MP3 Converter (pytubefix)")
    print(f"{'='*60}")
    print(f"Method: Direct download with pytubefix")
    print(f"URLs: {len(urls)}")
    print(f"Output: {output_dir}/")
    print(f"Bitrate: {bitrate} kbps")
    print(f"{'='*60}\n")
    
    success = 0
    failed = 0
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] {url}")
        
        result, filename, info = download_and_convert(url, output_dir, bitrate)
        
        if result:
            success += 1
            print(f"  OK {filename} ({info:.1f}MB)")
        else:
            failed += 1
            error_msg = str(info)[:80]
            print(f"  FAILED: {error_msg}")
            
            # Check for specific errors
            if "Sign in" in error_msg or "bot" in error_msg:
                print(f"  WARNING: BOT DETECTION - Try cookies or proxy method")
            elif "429" in error_msg:
                print(f"  WARNING: RATE LIMIT - Try cookies or proxy method")
        
        print()
    
    # Summary
    print(f"{'='*60}")
    print(f"DONE: {success} success, {failed} failed")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    convert_batch()
