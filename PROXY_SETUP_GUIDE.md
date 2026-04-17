# Proxy Setup Guide untuk VPS

## 🎯 Problem
VPS dengan datacenter IP kena rate limiting dari YouTube:
- Success rate: 0-24%
- Semua bypass method gagal
- YouTube blacklist datacenter IPs

## ✅ Solution: Residential Proxy

### Step 1: Beli Residential Proxy

#### Option A: IPRoyal (CHEAPEST - Recommended for Testing)
1. Buka: https://iproyal.com/residential-proxies/
2. Sign up dan beli paket:
   - **$7 for 4GB** (cukup untuk ~1000 videos)
   - **$14 for 8GB** (cukup untuk ~2000 videos)
3. Setelah beli, masuk ke dashboard
4. Copy proxy credentials:
   ```
   HTTP Proxy:
   Host: geo.iproyal.com
   Port: 12321
   Username: your_username
   Password: your_password
   
   Format: http://your_username:your_password@geo.iproyal.com:12321
   ```

#### Option B: Smartproxy (Good Balance)
1. Buka: https://smartproxy.com/proxies/residential-proxies
2. Sign up dan beli paket:
   - **$75/month for 8GB**
3. Get credentials dari dashboard
4. Format: `http://username:password@gate.smartproxy.com:7000`

#### Option C: Bright Data (Premium, Most Reliable)
1. Buka: https://brightdata.com/products/residential-proxies
2. Sign up (ada free trial)
3. Paket mulai dari **$500/month for 40GB**
4. Format: `http://username:password@brd.superproxy.io:22225`

### Step 2: Test Proxy di Local PC Dulu

```bash
# Test dengan 25 requests
python3 test_with_proxy.py 'http://username:password@proxy.com:8080'

# Test dengan 100 requests
python3 test_with_proxy.py 'http://username:password@proxy.com:8080' 100
```

**Expected Result:**
- ✅ Success rate: 95-100%
- ✅ No rate limiting
- ✅ Speed: 20-30 req/min

### Step 3: Deploy ke VPS dengan Proxy

#### Upload file terbaru ke VPS:

```bash
# Upload updated files
scp src/video_downloader.py root@your-vps:/root/ytmp3-converter/src/
scp test_with_proxy.py root@your-vps:/root/ytmp3-converter/
scp PROXY_SETUP_GUIDE.md root@your-vps:/root/ytmp3-converter/
```

#### SSH ke VPS dan test:

```bash
ssh root@your-vps
cd ~/ytmp3-converter
source venv/bin/activate

# Test dengan proxy (ganti dengan proxy kamu)
python3 test_with_proxy.py 'http://username:password@geo.iproyal.com:12321'
```

### Step 4: Convert Videos dengan Proxy

#### Single Video:

```python
# main_with_proxy.py
from src.conversion_pipeline import ConversionPipeline
from src.video_downloader import VideoDownloader

# Initialize downloader with proxy
downloader = VideoDownloader(
    use_cookies=False,  # Tidak perlu cookies kalau pakai proxy
    rotate_user_agent=True,
    proxy='http://username:password@geo.iproyal.com:12321'
)

# Create pipeline
pipeline = ConversionPipeline(downloader=downloader)

# Convert
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
result = pipeline.convert(url, output_dir="output", bitrate=192)

if result.success:
    print(f"✓ Success: {result.mp3_file.filename}")
else:
    print(f"✗ Failed")
```

#### Batch Convert:

```python
# batch_with_proxy.py
from src.conversion_pipeline import ConversionPipeline
from src.video_downloader import VideoDownloader
import time

# Your proxy
PROXY = 'http://username:password@geo.iproyal.com:12321'

# Initialize
downloader = VideoDownloader(
    use_cookies=False,
    rotate_user_agent=True,
    proxy=PROXY
)
pipeline = ConversionPipeline(downloader=downloader)

# Read URLs
with open('urls.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

# Convert
success = 0
failed = 0

for i, url in enumerate(urls):
    print(f"\n[{i+1}/{len(urls)}] Converting: {url}")
    
    result = pipeline.convert(url, output_dir="output", bitrate=192)
    
    if result.success:
        success += 1
        print(f"✓ Success: {result.mp3_file.filename}")
    else:
        failed += 1
        print(f"✗ Failed")
    
    # Optional: Small delay (proxy biasanya tidak perlu delay)
    if i < len(urls) - 1:
        time.sleep(0.5)

print(f"\n{'='*60}")
print(f"Results: {success} success, {failed} failed")
print(f"Success rate: {success/len(urls)*100:.1f}%")
```

### Step 5: Run di VPS

```bash
# SSH ke VPS
ssh root@your-vps
cd ~/ytmp3-converter
source venv/bin/activate

# Create batch script
cat > batch_with_proxy.py << 'EOF'
# (paste code dari Step 4 di atas)
EOF

# Create URLs file
cat > urls.txt << 'EOF'
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
https://www.youtube.com/watch?v=kJQP7kiw5Fk
EOF

# Run batch convert
python3 batch_with_proxy.py
```

## 📊 Expected Results

### Without Proxy (VPS Datacenter IP):
```
Success: 5/25 (20%)
Rate Limited: 20/25 (80%)
Verdict: POOR ❌
```

### With Residential Proxy:
```
Success: 24/25 (96%)
Rate Limited: 0/25 (0%)
Verdict: EXCELLENT ✅
```

## 💰 Cost Calculation

### IPRoyal Pricing:
- $1.75 per GB
- 1 video ≈ 3-5 MB bandwidth
- 1 GB ≈ 200-300 videos
- **$7 (4GB) = ~1000 videos**

### Example:
- 100 videos/day × 30 days = 3000 videos/month
- 3000 videos ≈ 10-15 GB
- Cost: **$17-26/month**

## 🔧 Troubleshooting

### Proxy Connection Failed
```
Error: ProxyError: Cannot connect to proxy
```
**Solution:**
1. Check proxy credentials (username/password)
2. Check proxy URL format
3. Test proxy dengan curl:
   ```bash
   curl -x http://user:pass@proxy.com:8080 https://www.youtube.com
   ```

### Proxy Still Rate Limited
```
Success rate: 30-50%
```
**Solution:**
1. Proxy mungkin shared/overused
2. Coba proxy provider lain
3. Tambah delay 1-2 detik antar request

### Proxy Too Slow
```
Speed: 5-10 req/min (normal: 20-30)
```
**Solution:**
1. Proxy server jauh dari YouTube servers
2. Pilih proxy location lebih dekat (US/EU)
3. Upgrade ke premium proxy tier

## 🎯 Recommendations

### For Testing (Low Volume):
- **IPRoyal**: $7 for 4GB
- Good for testing and small batches
- Pay-as-you-go model

### For Production (Medium Volume):
- **Smartproxy**: $75/month for 8GB
- Reliable and fast
- Good support

### For Enterprise (High Volume):
- **Bright Data**: $500/month for 40GB
- Most reliable
- Best performance
- 24/7 support

## 📝 Notes

1. **Proxy adalah solusi terbaik** untuk VPS datacenter IP
2. **Residential proxy** lebih mahal tapi worth it (95-100% success rate)
3. **Datacenter proxy** lebih murah tapi tetap kena rate limit
4. **Rotating proxy** lebih baik dari static proxy
5. **Location matters**: Pilih proxy location dekat dengan YouTube servers (US/EU)

## ❓ Questions?

Kalau ada pertanyaan atau butuh bantuan setup, let me know!
