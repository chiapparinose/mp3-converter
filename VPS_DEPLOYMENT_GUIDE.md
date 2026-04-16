# VPS Deployment & Testing Guide

Panduan lengkap untuk deploy dan test YouTube to MP3 Converter di VPS.

---

## 📋 Prerequisites

### VPS Requirements:
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM**: Minimal 1GB (recommended 2GB)
- **Storage**: Minimal 5GB free space
- **Python**: 3.8+
- **Network**: Unrestricted internet access

### Local Requirements:
- SSH client
- Git (optional, untuk clone repo)

---

## 🚀 Quick Start (Copy-Paste Commands)

### Step 1: Connect to VPS

```bash
# Replace with your VPS details
ssh root@YOUR_VPS_IP
# or
ssh username@YOUR_VPS_IP
```

### Step 2: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Install FFmpeg
sudo apt install -y ffmpeg

# Verify installations
python3 --version
pip3 --version
ffmpeg -version
```

### Step 3: Upload Project Files

**Option A: Using Git (Recommended)**

```bash
# If you have the project in GitHub
cd ~
git clone YOUR_REPO_URL ytmp3-converter
cd ytmp3-converter
```

**Option B: Using SCP (from local machine)**

```bash
# From your local machine (not VPS)
# Navigate to project directory first
cd /path/to/ytmp3-converter

# Upload entire project
scp -r . username@YOUR_VPS_IP:~/ytmp3-converter/

# Then SSH to VPS
ssh username@YOUR_VPS_IP
cd ~/ytmp3-converter
```

**Option C: Manual Upload (if no Git)**

```bash
# On VPS, create directory
mkdir -p ~/ytmp3-converter
cd ~/ytmp3-converter

# Create requirements.txt
cat > requirements.txt << 'EOF'
yt-dlp>=2023.3.4
mutagen>=1.47.0
hypothesis>=6.82.0
pytest>=7.4.0
EOF

# You'll need to upload the src/ folder manually via SFTP
# Or recreate the files one by one
```

### Step 4: Setup Python Environment

```bash
cd ~/ytmp3-converter

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installations
pip list
```

### Step 5: Create Test Script

```bash
# Create simple test script
cat > test_vps.py << 'EOF'
#!/usr/bin/env python3
"""Quick VPS test script."""

import sys
import time
from src.video_downloader import VideoDownloader

TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
]

def quick_test(num_requests=25):
    """Quick test."""
    print(f"\n{'='*60}")
    print(f"VPS Test - {num_requests} Requests")
    print(f"{'='*60}\n")
    
    downloader = VideoDownloader(use_cookies=False, rotate_user_agent=False)
    
    success = 0
    failed = 0
    rate_limited = 0
    start_time = time.time()
    
    urls = [TEST_URLS[i % len(TEST_URLS)] for i in range(num_requests)]
    
    for i, url in enumerate(urls):
        print(f"[{i+1}/{num_requests}]", end=' ', flush=True)
        
        try:
            info = downloader.get_video_info(url)
            if info:
                success += 1
                print("✓", end='', flush=True)
            else:
                failed += 1
                print("✗", end='', flush=True)
        except Exception as e:
            error_msg = str(e).lower()
            if any(kw in error_msg for kw in ['rate limit', 'bot', '429']):
                rate_limited += 1
                print("⚠️", end='', flush=True)
            else:
                failed += 1
                print("✗", end='', flush=True)
        
        if (i + 1) % 10 == 0:
            print(f" [{success}/{i+1}]", end='', flush=True)
    
    total_time = time.time() - start_time
    
    print(f"\n\n📊 Results:")
    print(f"  Success: {success}/{num_requests} ({success/num_requests*100:.1f}%)")
    print(f"  Failed: {failed}")
    print(f"  Rate Limited: {rate_limited}")
    print(f"  Time: {total_time:.1f}s ({num_requests/total_time*60:.1f} req/min)")
    
    if rate_limited == 0 and success >= num_requests * 0.95:
        print(f"  ✅ EXCELLENT")
    elif rate_limited <= 2:
        print(f"  ✓ GOOD")
    else:
        print(f"  ❌ POOR - Rate limited!")
    
    return success, rate_limited

if __name__ == '__main__':
    print("\n🚀 Starting VPS Test...")
    
    # Test 25 requests first
    success, rate_limited = quick_test(25)
    
    if rate_limited == 0 and success >= 24:
        print("\n✅ 25 requests successful! Testing 100...")
        time.sleep(3)
        quick_test(100)
    else:
        print("\n⚠️  Rate limiting detected. VPS IP may be restricted.")

EOF

chmod +x test_vps.py
```

### Step 6: Run Test

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run test
python3 test_vps.py
```

---

## 📊 Expected Results

### Scenario 1: VPS with Good IP (Rare)
```
Success: 100/100 (100.0%)
Rate Limited: 0
✅ EXCELLENT
```

### Scenario 2: VPS with Datacenter IP (Common)
```
Success: 23/100 (23.0%)
Rate Limited: 77
❌ POOR - Rate limited!
```

### Scenario 3: VPS with Moderate Restrictions
```
Success: 85/100 (85.0%)
Rate Limited: 15
✓ GOOD
```

---

## 🔧 Testing Different Bypass Methods on VPS

### Test 1: No Bypass (Baseline)

```bash
python3 test_vps.py
```

### Test 2: With User Agent Rotation

```bash
cat > test_vps_useragent.py << 'EOF'
#!/usr/bin/env python3
from src.video_downloader import VideoDownloader
import time

TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
]

downloader = VideoDownloader(use_cookies=False, rotate_user_agent=True)

print("Testing with User Agent Rotation...")
success = 0
for i in range(25):
    try:
        info = downloader.get_video_info(TEST_URLS[i % len(TEST_URLS)])
        if info:
            success += 1
            print(f"[{i+1}/25] ✓", end=' ', flush=True)
    except:
        print(f"[{i+1}/25] ✗", end=' ', flush=True)

print(f"\n\nSuccess: {success}/25 ({success/25*100:.1f}%)")
EOF

python3 test_vps_useragent.py
```

### Test 3: With Delays

```bash
cat > test_vps_delays.py << 'EOF'
#!/usr/bin/env python3
from src.video_downloader import VideoDownloader
import time

TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
]

downloader = VideoDownloader(use_cookies=False, rotate_user_agent=True)

print("Testing with 2s delays...")
success = 0
for i in range(25):
    try:
        info = downloader.get_video_info(TEST_URLS[i % len(TEST_URLS)])
        if info:
            success += 1
            print(f"[{i+1}/25] ✓", end=' ', flush=True)
    except:
        print(f"[{i+1}/25] ✗", end=' ', flush=True)
    
    if i < 24:
        time.sleep(2)

print(f"\n\nSuccess: {success}/25 ({success/25*100:.1f}%)")
EOF

python3 test_vps_delays.py
```

---

## 🔍 Troubleshooting

### Issue 1: "ModuleNotFoundError: No module named 'src'"

```bash
# Make sure you're in the project directory
cd ~/ytmp3-converter

# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: "FFmpeg not found"

```bash
# Install FFmpeg
sudo apt install -y ffmpeg

# Verify
ffmpeg -version
```

### Issue 3: "Permission denied"

```bash
# Make scripts executable
chmod +x test_vps.py
chmod +x test_*.py

# Or run with python3
python3 test_vps.py
```

### Issue 4: Rate Limited Immediately

```bash
# VPS IP might be blacklisted
# Try with delays
python3 test_vps_delays.py

# Check your IP reputation
curl https://ipinfo.io
```

---

## 📈 Performance Comparison

### Residential IP (Your PC):
- **Success Rate**: 100% (100/100)
- **Rate Limited**: 0
- **Speed**: ~28 req/min

### VPS Datacenter IP (Expected):
- **Success Rate**: 20-80% (varies by provider)
- **Rate Limited**: High
- **Speed**: Limited by rate limiting

### VPS with Bypass Methods:
- **Success Rate**: 60-95% (with delays)
- **Rate Limited**: Moderate
- **Speed**: ~10-20 req/min (with delays)

---

## 🎯 Recommendations for VPS

### If Rate Limited on VPS:

1. **Use Delays** (2-5 seconds between requests)
2. **Use User Agent Rotation**
3. **Process in small batches** (10-15 videos)
4. **Take breaks** (5 minutes every 15 videos)
5. **Consider residential proxy** (if high volume needed)

### VPS Providers with Better IPs:

- **DigitalOcean**: Generally good
- **Linode**: Good reputation
- **Vultr**: Mixed results
- **AWS/GCP**: Often restricted (datacenter IPs)
- **Contabo**: Often restricted

---

## 🚀 Running Full Test Suite on VPS

```bash
# Upload the complete test script
# Make sure test_all_bypass_methods.py is uploaded

# Run complete test
python3 test_all_bypass_methods.py

# Or run the progressive test
python3 test_100_requests.py
```

---

## 📝 Automated Testing Script

```bash
cat > run_vps_tests.sh << 'EOF'
#!/bin/bash

echo "================================"
echo "VPS Rate Limiting Test Suite"
echo "================================"
echo ""

# Activate virtual environment
source venv/bin/activate

echo "Test 1: No Bypass (25 requests)"
python3 test_vps.py

echo ""
echo "Waiting 10 seconds..."
sleep 10

echo ""
echo "Test 2: User Agent Rotation (25 requests)"
python3 test_vps_useragent.py

echo ""
echo "Waiting 10 seconds..."
sleep 10

echo ""
echo "Test 3: With 2s Delays (25 requests)"
python3 test_vps_delays.py

echo ""
echo "================================"
echo "All tests completed!"
echo "================================"
EOF

chmod +x run_vps_tests.sh

# Run all tests
./run_vps_tests.sh
```

---

## 🔐 Security Notes

1. **Don't commit sensitive data** to Git
2. **Use environment variables** for API keys (if any)
3. **Keep VPS updated**: `sudo apt update && sudo apt upgrade`
4. **Use firewall**: `sudo ufw enable`
5. **Change default SSH port** (optional but recommended)

---

## 📊 Monitoring & Logs

```bash
# Create log directory
mkdir -p ~/ytmp3-converter/logs

# Run with logging
python3 test_vps.py 2>&1 | tee logs/test_$(date +%Y%m%d_%H%M%S).log

# View logs
tail -f logs/test_*.log
```

---

## 🎉 Success Criteria

### VPS Test is Successful if:
- ✅ At least 80% success rate with delays
- ✅ Less than 5 rate limit errors per 25 requests
- ✅ Consistent performance across multiple runs

### VPS Test Needs Improvement if:
- ⚠️ Success rate below 60%
- ⚠️ Frequent rate limiting (>10 per 25 requests)
- ⚠️ Inconsistent results

---

## 📞 Need Help?

If you encounter issues:

1. Check VPS IP reputation: `curl https://ipinfo.io`
2. Test basic connectivity: `curl -I https://www.youtube.com`
3. Check if yt-dlp works: `yt-dlp --version`
4. Try different VPS provider if consistently rate limited

---

**Ready to test on VPS!** 🚀

Just follow the Quick Start section and you'll be testing in minutes.
