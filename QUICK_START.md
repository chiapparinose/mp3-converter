# Quick Start Guide - YouTube to MP3 Converter

## Installation (5 minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### 3. Verify Installation
```bash
python test_system.py
```

You should see: `✓ All tests passed! System is ready to use.`

## Basic Usage

### Convert a Video
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Output:
```
Converting: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Output directory: output
Bitrate: 192 kbps

[████████████████████████████] Download: 100.0%

✓ Conversion complete!
  File: output/Never Gonna Give You Up.mp3
  Size: 3.45 MB
  Duration: 3:33
  Bitrate: 192 kbps
```

## Common Commands

### High Quality (320 kbps)
```bash
python main.py "URL" --bitrate 320
```

### Custom Output Directory
```bash
python main.py "URL" -o ~/Music
```

### Skip Metadata
```bash
python main.py "URL" --no-metadata
```

### Verbose Output (for debugging)
```bash
python main.py "URL" -v
```

## Supported URL Formats

✅ Standard: `https://www.youtube.com/watch?v=VIDEO_ID`  
✅ Short: `https://youtu.be/VIDEO_ID`  
✅ Shorts: `https://www.youtube.com/shorts/VIDEO_ID`  
✅ Mobile: `https://m.youtube.com/watch?v=VIDEO_ID`  
✅ Embed: `https://www.youtube.com/embed/VIDEO_ID`

## Troubleshooting

### "FFmpeg not found"
- Make sure FFmpeg is installed
- Check PATH: `ffmpeg -version`
- Restart terminal after installation

### "Download failed"
- Check internet connection
- Verify URL is correct
- Try again (automatic retry: 3 attempts)

### "Conversion timeout"
- Video may be too long (> 1 hour)
- Try a shorter video
- Check disk space

### "Invalid URL"
- Use full YouTube URL
- Check for typos
- Make sure video is public

## Tips

1. **Bitrate Guide:**
   - 128 kbps: Good for speech/podcasts
   - 192 kbps: Standard quality (default)
   - 256 kbps: High quality
   - 320 kbps: Maximum quality

2. **Storage:**
   - Temporary files auto-deleted after 60 seconds
   - Keep 5 GB free disk space
   - Output files saved to `output/` directory

3. **Performance:**
   - Download speed depends on internet
   - Conversion speed depends on CPU
   - Typical: 3-5 minutes for 5-minute video

## Examples

### Example 1: Music Video
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --bitrate 320
```

### Example 2: Podcast
```bash
python main.py "https://youtu.be/PODCAST_ID" --bitrate 128 -o ~/Podcasts
```

### Example 3: Multiple Videos
```bash
python main.py "URL1"
python main.py "URL2"
python main.py "URL3"
```

## Getting Help

```bash
python main.py --help
```

## What Gets Embedded

The MP3 file includes:
- ✅ Video title (as song title)
- ✅ Channel name (as artist)
- ✅ Video thumbnail (as album art)
- ✅ Duration

## File Naming

Files are automatically named based on video title with invalid characters removed:

- `My Video: Tutorial` → `My Video Tutorial.mp3`
- `How to Code | Python` → `How to Code  Python.mp3`
- `Test/File\Name` → `TestFileName.mp3`

## Next Steps

1. Try converting a video
2. Check the `output/` directory
3. Play the MP3 file
4. Enjoy! 🎵

## Need More Help?

- Check `README.md` for detailed documentation
- Check `AUDIT_REPORT.md` for technical details
- Run `python test_system.py` to verify installation
