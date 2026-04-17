# YouTube Data API + Proxy - VPS Deployment Guide

## ✅ Solution: YouTube Data API + Proxy Rotation

**Method:**
- ✓ Metadata via YouTube Data API (FREE, 10k/day, no rate limit)
- ✓ Download via Proxy (bypass datacenter IP block)

**Why This Works:**
- API gets metadata without rate limit
- Proxy bypasses "Sign in to confirm you're not a bot" error
- Proxy only used for download (~10 MB per video)

---

## 🚀 Quick Deploy to VPS

### 1. Pull Latest Code
```bash
cd ytmp3-converter
git pull origin main
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Setup Proxy File
Make sure `proxies.txt` exists with your proxies (one per line):
```
209.50.178.235:3129
45.67.89.123:8080
...
```

### 4. Prepare URLs File
```bash
# Create urls.txt with your YouTube URLs (one per line)
nano urls.txt
```

### 5. Run Converter
```bash
python3 convert_with_api.py
```

---

## 📊 How It Works

**Step 1: Get Metadata (API)**
- Uses YouTube Data API v3
- FREE: 10,000 requests/day
- No rate limiting
- No proxy needed

**Step 2: Download Video (Proxy)**
- Uses proxy from `proxies.txt`
- Automatic rotation (round-robin)
- Health checking (skips bad proxies)
- Bypasses datacenter IP block

**Step 3: Convert to MP3**
- Standard conversion
- Embed metadata from API

---

## 🔑 Configuration

**API Key:** `AIzaSyDEtALTlUCSyVuzJ2ReAefoDOUoRkNxnOo`
- Daily quota: 10,000 requests
- 1 video = 1 quota

**Proxy File:** `proxies.txt`
- Format: `IP:PORT` (one per line)
- Supports IP-whitelisted proxies
- Automatic rotation and health checking

---

## 📝 Example Usage

```bash
# Default (uses urls.txt and proxies.txt)
python3 convert_with_api.py

# Custom files (edit script)
# - urls_file='your_urls.txt'
# - proxies_file='your_proxies.txt'
# - output_dir='your_output/'
# - bitrate=320
```

---

## ✅ Benefits

1. **No Rate Limiting** - API bypasses YouTube rate limits
2. **Bypass Bot Detection** - Proxy bypasses datacenter IP block
3. **Cost Effective** - Proxy only for download (~10 MB), not metadata (~50 KB)
4. **Automatic Rotation** - Distributes load across proxies
5. **Health Checking** - Skips bad proxies automatically

---

## 🎯 Production Ready

This solution combines the best of both worlds:
- API for metadata (free, no rate limit)
- Proxy for download (bypass bot detection)

Ready for production use on VPS!
