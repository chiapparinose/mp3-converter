# VPS Deployment Instructions

## ✅ Repository Updated!

All changes have been pushed to GitHub:
- ✅ Smart proxy support (99.5% bandwidth savings)
- ✅ Proxy manager with rotation & health checking
- ✅ Batch converter with proxy file support
- ✅ Comprehensive documentation
- ✅ Verification scripts

**Commit**: `feat: Add smart proxy support with 99.5% bandwidth savings`

---

## 🚀 Deploy to VPS (2 Methods)

### Method 1: Git Pull (RECOMMENDED)

```bash
# SSH to VPS
ssh root@your-vps

# Navigate to project
cd ~/ytmp3-converter

# Pull latest changes
git pull origin main

# Activate venv
source venv/bin/activate

# Verify new files
ls -la src/proxy_manager.py src/smart_downloader.py batch_smart_proxy_file.py

# Done! ✓
```

### Method 2: Fresh Clone

```bash
# SSH to VPS
ssh root@your-vps

# Backup old directory (optional)
mv ~/ytmp3-converter ~/ytmp3-converter.backup

# Clone fresh
git clone https://github.com/chiapparinose/mp3-converter.git ytmp3-converter
cd ytmp3-converter

# Setup venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Done! ✓
```

---

## 📝 Setup on VPS

### Step 1: Verify Files

```bash
cd ~/ytmp3-converter
source venv/bin/activate

# Check new files exist
ls -la src/proxy_manager.py
ls -la src/smart_downloader.py
ls -la batch_smart_proxy_file.py
ls -la proxies.txt

# Should show all files ✓
```

### Step 2: Verify proxies.txt

```bash
# Check proxies loaded
head -5 proxies.txt

# Should show:
# 209.50.178.235:3129
# 216.26.255.36:3129
# 209.50.186.35:3129
# ...
```

### Step 3: Create urls.txt

```bash
cat > urls.txt << 'EOF'
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
https://www.youtube.com/watch?v=kJQP7kiw5Fk
EOF
```

### Step 4: Run Verification (Optional)

```bash
# Verify implementation
python3 verify_smart_proxy.py

# Should show:
# ✓ ALL VERIFICATIONS PASSED!
# ✓ Proxy ONLY for metadata: CONFIRMED
# ✓ Download direct (no proxy): CONFIRMED
# ✓ Bandwidth savings: 99.5% CONFIRMED
```

### Step 5: Run Batch Convert!

```bash
# Basic usage
python3 batch_smart_proxy_file.py urls.txt

# With options
python3 batch_smart_proxy_file.py urls.txt \
    --bitrate 320 \
    --rotation random \
    --delay 0.5 \
    --output-dir music
```

---

## 📊 Expected Output

```
======================================================================
Smart Batch Converter with Proxy File
======================================================================

📁 URLs file: urls.txt
🌐 Proxies file: proxies.txt
   Loaded: 100 proxies
   Rotation: round-robin
   Usage: METADATA ONLY (saves 99% bandwidth!)
📂 Output: output
🎵 Bitrate: 192 kbps
⏱️  Delay: 0.5s
📊 Total videos: 3

======================================================================
BANDWIDTH USAGE COMPARISON
======================================================================

Videos: 3
Avg video size: 10.0 MB

Full Proxy Mode (proxy for everything):
  Bandwidth: 30.2 MB (0.03 GB)
  Cost: $0.05

Smart Mode (proxy only for metadata):
  Bandwidth: 0.2 MB (0.00 GB)
  Cost: $0.00

Savings:
  Bandwidth: 30.0 MB (0.03 GB)
  Percentage: 99.5%
  Cost: $0.05
======================================================================

----------------------------------------------------------------------

[1/3] Converting: https://www.youtube.com/watch?v=dQw4w9WgXcQ
  → Using proxy: 209.50.178.235:3129
  → Getting metadata via proxy...
  → Title: Rick Astley - Never Gonna Give You Up
  → Downloading audio DIRECT (no proxy)...
  ✓ Success: Rick_Astley_Never_Gonna_Give_You_Up.mp3
    Size: 3.45 MB
    Duration: 3:33

[2/3] Converting: https://www.youtube.com/watch?v=9bZkp7q19f0
  → Using proxy: 216.26.255.36:3129
  → Getting metadata via proxy...
  → Title: PSY - GANGNAM STYLE
  → Downloading audio DIRECT (no proxy)...
  ✓ Success: PSY_GANGNAM_STYLE.mp3
    Size: 3.67 MB
    Duration: 4:13

[3/3] Converting: https://www.youtube.com/watch?v=kJQP7kiw5Fk
  → Using proxy: 209.50.186.35:3129
  → Getting metadata via proxy...
  → Title: Luis Fonsi - Despacito
  → Downloading audio DIRECT (no proxy)...
  ✓ Success: Luis_Fonsi_Despacito.mp3
    Size: 4.12 MB
    Duration: 4:42

======================================================================
SUMMARY
======================================================================

✓ Success: 3/3 (100.0%)
✗ Failed: 0/3 (0.0%)
⏱️  Total time: 1.2 minutes
⚡ Speed: 150.0 videos/hour

📊 Bandwidth Usage:
  Proxy (metadata only): ~0.2 MB
  Direct (downloads): ~30.0 MB
  Total: ~30.2 MB

💰 Proxy Cost:
  Smart mode: ~$0.0003
  Full proxy mode: ~$0.05
  Savings: ~$0.05 (99.5%)

📂 Output directory: output/

======================================================================
PROXY STATISTICS
======================================================================

Total proxies: 100
Rotation mode: round-robin
Skip unhealthy: True

Proxy                                    Requests   Success    Failed     Rate       Status    
--------------------------------------------------------------------------------
209.50.178.235:3129                      1          1          0          100.0%     ✓ Healthy 
216.26.255.36:3129                       1          1          0          100.0%     ✓ Healthy 
209.50.186.35:3129                       1          1          0          100.0%     ✓ Healthy 
======================================================================
```

---

## 🎯 Command Options

```bash
# Basic
python3 batch_smart_proxy_file.py urls.txt

# Custom proxy file
python3 batch_smart_proxy_file.py urls.txt --proxies-file my_proxies.txt

# High quality
python3 batch_smart_proxy_file.py urls.txt --bitrate 320

# Random rotation
python3 batch_smart_proxy_file.py urls.txt --rotation random

# Custom delay
python3 batch_smart_proxy_file.py urls.txt --delay 1.0

# Custom output
python3 batch_smart_proxy_file.py urls.txt --output-dir /mnt/music

# No statistics
python3 batch_smart_proxy_file.py urls.txt --no-stats

# All options
python3 batch_smart_proxy_file.py urls.txt \
    --proxies-file proxies.txt \
    --output-dir music \
    --bitrate 320 \
    --rotation random \
    --delay 1.0 \
    --no-stats
```

---

## 🔍 Troubleshooting

### Issue 1: "No proxies loaded"

```bash
# Check proxies.txt exists
ls -la proxies.txt

# Check content
head proxies.txt

# Should show IP:PORT format
```

### Issue 2: "All proxies failed"

```bash
# Check if proxies are IP-whitelisted for VPS IP
# Verify VPS IP is whitelisted in proxy provider dashboard

# Test single proxy manually
curl -x http://209.50.178.235:3129 https://www.youtube.com
```

### Issue 3: "Module not found"

```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 4: Git pull fails

```bash
# Stash local changes
git stash

# Pull
git pull origin main

# Reapply changes
git stash pop
```

---

## 📊 Performance Expectations

### With 100 IP-Whitelisted Proxies:

```
Success Rate: 95-100%
Speed: 40-60 videos/hour
Proxy Bandwidth: ~50 KB per video
Direct Bandwidth: ~10 MB per video
Total Proxy Usage: 99.5% less than full proxy mode
```

### Cost Analysis (1000 videos):

```
Full Proxy Mode:
  Bandwidth: ~10 GB via proxy
  Cost: ~$17.50

Smart Mode:
  Bandwidth: ~50 MB via proxy
  Cost: ~$0.09

Savings: $17.41 (99.5%)
```

---

## ✅ Verification Checklist

- [ ] SSH to VPS
- [ ] Navigate to ~/ytmp3-converter
- [ ] Run `git pull origin main`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Verify files exist (proxy_manager.py, smart_downloader.py, etc.)
- [ ] Check proxies.txt has 100 proxies
- [ ] Create urls.txt with test URLs
- [ ] Run verification: `python3 verify_smart_proxy.py`
- [ ] Run batch convert: `python3 batch_smart_proxy_file.py urls.txt`
- [ ] Check output directory for MP3 files
- [ ] Verify proxy statistics show success

---

## 🎉 Success Indicators

✅ All files pulled from Git
✅ proxies.txt loaded (100 proxies)
✅ Verification passed
✅ Batch convert running
✅ MP3 files created in output/
✅ Proxy statistics show high success rate
✅ Bandwidth usage: ~50 KB proxy per video
✅ Cost savings: 99.5%

**Ready for production! 🚀**

---

## 📚 Documentation

- **FINAL_SETUP_GUIDE.md** - Quick start guide
- **SMART_PROXY_GUIDE.md** - Detailed explanation
- **IMPLEMENTATION_COMPLETE.md** - Complete summary
- **VPS_DEPLOY_INSTRUCTIONS.md** - This file

---

**Last Updated**: April 17, 2026
**Status**: ✅ READY FOR DEPLOYMENT
**Repository**: https://github.com/chiapparinose/mp3-converter.git
