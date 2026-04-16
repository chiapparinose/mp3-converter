# How to Export Browser Cookies for YouTube

This guide explains how to export cookies from your browser to use with the advanced batch converter for **maximum rate limit bypass**.

## Why Use Browser Cookies?

- ✅ **Highest rate limits** - 100+ requests vs ~20 without cookies
- ✅ **Access age-restricted videos**
- ✅ **Access private videos** (if you're the owner)
- ✅ **Better reliability** - Less likely to trigger bot detection
- ✅ **No manual export needed** - yt-dlp can read directly from browser

---

## Method 1: Automatic Browser Cookie Extraction ⭐ RECOMMENDED

**yt-dlp can automatically read cookies from your browser!** No manual export needed.

### Requirements

1. You must be **logged in to YouTube** in your browser
2. Browser must be **closed** when running the converter (for some browsers)

### Usage

```bash
# Chrome (default)
python advanced_batch_convert.py urls.txt

# Firefox
python advanced_batch_convert.py urls.txt --cookies-browser firefox

# Edge
python advanced_batch_convert.py urls.txt --cookies-browser edge

# Safari (macOS only)
python advanced_batch_convert.py urls.txt --cookies-browser safari

# Brave
python advanced_batch_convert.py urls.txt --cookies-browser brave

# Opera
python advanced_batch_convert.py urls.txt --cookies-browser opera
```

### Supported Browsers

| Browser | Command | Notes |
|---------|---------|-------|
| Chrome | `--cookies-browser chrome` | Default, works on all platforms |
| Firefox | `--cookies-browser firefox` | Works on all platforms |
| Edge | `--cookies-browser edge` | Windows, macOS |
| Safari | `--cookies-browser safari` | macOS only |
| Brave | `--cookies-browser brave` | All platforms |
| Opera | `--cookies-browser opera` | All platforms |

### Troubleshooting Automatic Extraction

**Error: "Could not load cookies from browser"**

Solutions:
1. Make sure you're **logged in to YouTube** in that browser
2. **Close the browser** completely (some browsers lock the cookie database)
3. Try a different browser
4. Use Method 2 (manual export) instead

---

## Method 2: Manual Cookie Export (Alternative)

If automatic extraction doesn't work, you can manually export cookies to a file.

### Step 1: Install Browser Extension

Install a cookie export extension for your browser:

#### Chrome / Edge / Brave / Opera

**Extension**: "Get cookies.txt LOCALLY"
- Chrome Web Store: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
- **Important**: Use "LOCALLY" version for privacy

#### Firefox

**Extension**: "cookies.txt"
- Firefox Add-ons: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

#### Safari

**Extension**: "ExportCookies"
- Mac App Store: Search for "ExportCookies"

---

### Step 2: Export YouTube Cookies

1. **Open YouTube** in your browser
2. **Log in** to your YouTube account
3. **Click the extension icon** in your browser toolbar
4. **Select "Export" or "Download"**
5. **Save the file** as `youtube_cookies.txt`

**Important**: The file must be in **Netscape cookie format** (most extensions use this by default)

---

### Step 3: Use the Cookie File

```bash
# Use the exported cookie file
python advanced_batch_convert.py urls.txt --cookies-file youtube_cookies.txt

# With full path
python advanced_batch_convert.py urls.txt --cookies-file ~/Downloads/youtube_cookies.txt

# Windows
python advanced_batch_convert.py urls.txt --cookies-file C:\Users\YourName\Downloads\youtube_cookies.txt
```

---

## Cookie File Format

The cookie file should be in **Netscape format**:

```
# Netscape HTTP Cookie File
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1234567890	CONSENT	YES+cb
.youtube.com	TRUE	/	FALSE	1234567890	VISITOR_INFO1_LIVE	abcdefghijk
.youtube.com	TRUE	/	TRUE	1234567890	LOGIN_INFO	AFmmF2sw...
```

**Key cookies for YouTube**:
- `LOGIN_INFO` - Authentication token
- `VISITOR_INFO1_LIVE` - Visitor tracking
- `CONSENT` - Cookie consent
- `PREF` - User preferences

---

## Security & Privacy

### ⚠️ Important Security Notes

1. **Never share your cookie file** - It contains your login session
2. **Keep cookies private** - Anyone with your cookies can access your account
3. **Cookies expire** - Usually after 30-90 days, you'll need to re-export
4. **Use LOCALLY extensions** - Avoid extensions that upload cookies to servers
5. **Delete old cookie files** - Don't leave them in Downloads folder

### Best Practices

✅ **DO**:
- Use automatic browser extraction (Method 1) when possible
- Keep cookie files in a secure location
- Delete cookie files after use
- Re-export cookies when they expire
- Use cookies only on your own computer

❌ **DON'T**:
- Share cookie files with others
- Upload cookie files to cloud storage
- Use cookies from untrusted sources
- Keep cookie files in public folders
- Use someone else's cookies

---

## Verifying Cookies Work

### Test 1: Check if cookies are loaded

```bash
# Run with verbose output
python advanced_batch_convert.py urls.txt -v
```

Look for this message:
```
Using cookies from browser: chrome
```
or
```
Using cookies from file: youtube_cookies.txt
```

### Test 2: Try converting a video

```bash
# Convert a single video
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -v
```

If cookies work, you should see:
- ✅ No "Sign in to confirm you're not a bot" errors
- ✅ Faster downloads
- ✅ Higher success rate

---

## Troubleshooting

### Problem: "Could not load cookies from browser"

**Solutions**:
1. Make sure you're logged in to YouTube
2. Close the browser completely
3. Try a different browser
4. Use manual export (Method 2)

### Problem: "Cookie file not found"

**Solutions**:
1. Check the file path is correct
2. Use absolute path instead of relative path
3. Make sure file exists: `ls youtube_cookies.txt` (Linux/Mac) or `dir youtube_cookies.txt` (Windows)

### Problem: "Invalid cookie format"

**Solutions**:
1. Make sure file is in Netscape format
2. Re-export cookies using a different extension
3. Check file isn't corrupted (should be plain text)

### Problem: Still getting rate limited

**Solutions**:
1. Cookies may have expired - re-export them
2. You may not be logged in - check YouTube login status
3. Try increasing delays: `--delay 3`
4. Reduce batch size: `--batch-size 10`

### Problem: "Sign in to confirm you're not a bot"

**Solutions**:
1. Cookies are not working - verify they're loaded
2. Cookies may be expired - re-export them
3. You may need to solve a captcha in your browser first
4. Try logging out and back in to YouTube

---

## Cookie Maintenance

### When to Re-export Cookies

- **Every 30 days** - Cookies typically expire after 30-90 days
- **After password change** - Old cookies become invalid
- **After logout** - Logging out invalidates cookies
- **When getting rate limited** - May indicate expired cookies

### How to Check Cookie Expiration

Look at the expiration timestamp in the cookie file:

```
.youtube.com	TRUE	/	TRUE	1234567890	LOGIN_INFO	AFmmF2sw...
                                    ^^^^^^^^^^
                                    Unix timestamp
```

Convert timestamp to date:
```bash
# Linux/Mac
date -d @1234567890

# Or use online converter
# https://www.epochconverter.com/
```

---

## Programmatic Usage

### Python Example

```python
from src.video_downloader import VideoDownloader
from src.conversion_pipeline import ConversionPipeline

# Method 1: Automatic browser extraction
downloader = VideoDownloader(
    use_cookies=True,
    cookies_browser='chrome'  # or 'firefox', 'edge', etc.
)

# Method 2: Cookie file
downloader = VideoDownloader(
    use_cookies=True,
    cookies_file='youtube_cookies.txt'
)

# Use with pipeline
pipeline = ConversionPipeline(downloader=downloader)
mp3_file, error = pipeline.convert(url, bitrate=192)
```

---

## FAQ

### Q: Do I need to be logged in to YouTube?

**A**: Yes, for cookies to work, you must be logged in to YouTube in your browser.

### Q: Will this work with YouTube Premium?

**A**: Yes! YouTube Premium accounts may have even higher rate limits.

### Q: Can I use cookies from multiple accounts?

**A**: No, use cookies from one account at a time. Mixing cookies can cause authentication errors.

### Q: How long do cookies last?

**A**: Typically 30-90 days, but can vary. Re-export when they expire.

### Q: Is this safe and legal?

**A**: Yes, you're using your own cookies from your own account. This is the same as being logged in.

### Q: Can I use this on a server?

**A**: Yes, but you'll need to use Method 2 (cookie file) since servers don't have browsers.

### Q: What if I don't want to use cookies?

**A**: You can disable cookies with `--no-cookies`, but rate limits will be much lower (~20 requests vs 100+).

---

## Summary

### Quick Start (Recommended)

1. **Log in to YouTube** in Chrome/Firefox
2. **Run the converter**:
   ```bash
   python advanced_batch_convert.py urls.txt
   ```
3. **Done!** Cookies are automatically extracted

### If Automatic Doesn't Work

1. **Install cookie extension** (Get cookies.txt LOCALLY)
2. **Export cookies** from YouTube
3. **Use cookie file**:
   ```bash
   python advanced_batch_convert.py urls.txt --cookies-file youtube_cookies.txt
   ```

---

## Additional Resources

- **yt-dlp Cookie Documentation**: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
- **Chrome Extension**: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
- **Firefox Extension**: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/
- **Epoch Converter**: https://www.epochconverter.com/

---

**Need Help?** See `BYPASS_RATE_LIMIT.md` for more information about rate limiting bypass methods.
