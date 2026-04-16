# VPS Quick Start - One Command Deployment

Deploy dan test YouTube to MP3 Converter di VPS dengan satu command!

---

## 🚀 Super Quick Start

### Linux / macOS:

```bash
# Make script executable
chmod +x deploy_to_vps.sh

# Deploy to VPS
./deploy_to_vps.sh username@your_vps_ip

# Example:
./deploy_to_vps.sh root@192.168.1.100
```

### Windows (PowerShell):

```powershell
# Run deployment script
.\deploy_to_vps.ps1 username@your_vps_ip

# Example:
.\deploy_to_vps.ps1 root@192.168.1.100
```

---

## 📋 What the Script Does

The deployment script automatically:

1. ✅ Tests SSH connection to VPS
2. ✅ Installs Python 3, pip, and FFmpeg
3. ✅ Creates project directory
4. ✅ Uploads all project files
5. ✅ Sets up Python virtual environment
6. ✅ Installs dependencies
7. ✅ Creates test runner scripts
8. ✅ Runs initial 25-request test

**Total time**: ~2-5 minutes (depending on VPS speed)

---

## 📊 What to Expect

### After Deployment:

You'll see test results like:

#### Scenario 1: Good VPS IP ✅
```
📊 Results:
  Success: 25/25 (100.0%)
  Failed: 0
  Rate Limited: 0
  Time: 52.3s (28.7 req/min)

  ✅ EXCELLENT - VPS has good IP!
  Recommendation: No bypass needed
```

#### Scenario 2: Restricted VPS IP ⚠️
```
📊 Results:
  Success: 18/25 (72.0%)
  Failed: 0
  Rate Limited: 7
  Time: 65.1s (23.0 req/min)

  ⚠️  FAIR - Moderate rate limiting
  Recommendation: Use all bypass methods + 2-3s delays
```

#### Scenario 3: Heavily Restricted ❌
```
📊 Results:
  Success: 5/25 (20.0%)
  Failed: 0
  Rate Limited: 20
  Time: 78.4s (19.1 req/min)

  ❌ POOR - Heavy rate limiting
  Recommendation: VPS IP is restricted
```

---

## 🔧 After Deployment

### Connect to VPS:

```bash
ssh username@your_vps_ip
cd ~/ytmp3-converter
source venv/bin/activate
```

### Run Tests:

```bash
# Quick test (25 requests)
python3 quick_test.py

# Progressive test (25 → 100 if successful)
python3 test_100_requests.py

# Test all bypass methods (100 requests each)
python3 test_all_bypass_methods.py

# Or use the test runner
./run_tests.sh
```

### Convert Videos:

```bash
# Single video
python3 main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Batch conversion
python3 batch_convert.py urls.txt

# Advanced batch (with all bypass methods)
python3 advanced_batch_convert.py urls.txt
```

---

## 🛠️ Troubleshooting

### Issue 1: "Permission denied (publickey)"

**Solution**: Setup SSH key or use password authentication

```bash
# Generate SSH key (if you don't have one)
ssh-keygen -t rsa -b 4096

# Copy to VPS
ssh-copy-id username@your_vps_ip

# Or use password authentication
./deploy_to_vps.sh -o PreferredAuthentications=password username@your_vps_ip
```

### Issue 2: "Connection refused"

**Solution**: Check VPS is running and SSH port is correct

```bash
# Test connection
ping your_vps_ip

# Check SSH port (if not default 22)
ssh -p PORT username@your_vps_ip

# Deploy with custom port
ssh -p PORT username@your_vps_ip < deploy_to_vps.sh
```

### Issue 3: Script fails during upload

**Solution**: Check you're in the project directory

```bash
# Make sure you're in the project root
cd /path/to/ytmp3-converter

# Verify files exist
ls -la src/
ls -la test_*.py

# Run deployment again
./deploy_to_vps.sh username@your_vps_ip
```

### Issue 4: Rate limited immediately on VPS

**Solution**: VPS IP is restricted, use bypass methods

```bash
# SSH to VPS
ssh username@your_vps_ip
cd ~/ytmp3-converter
source venv/bin/activate

# Test with delays
python3 test_all_bypass_methods.py

# Use advanced batch converter with delays
python3 advanced_batch_convert.py urls.txt --delay 5 --batch-size 10
```

---

## 📈 Performance Comparison

### Your PC (Residential IP):
- ✅ Success: 100/100 (100%)
- ✅ Rate Limited: 0
- ✅ Speed: ~28 req/min
- ✅ **No bypass needed**

### VPS (Datacenter IP) - Expected:
- ⚠️ Success: 20-80% (varies)
- ⚠️ Rate Limited: Moderate to High
- ⚠️ Speed: 10-25 req/min
- ⚠️ **Bypass methods recommended**

---

## 🎯 Recommendations by VPS Provider

### Good for YouTube (Less Rate Limiting):
- ✅ **DigitalOcean** - Generally good IPs
- ✅ **Linode** - Good reputation
- ✅ **Hetzner** - Mixed but often good
- ✅ **OVH** - Decent for Europe

### Moderate (May Need Bypass):
- ⚠️ **Vultr** - Mixed results
- ⚠️ **Contabo** - Often restricted
- ⚠️ **Hostinger** - Variable

### Restricted (Heavy Bypass Needed):
- ❌ **AWS EC2** - Datacenter IPs often blocked
- ❌ **Google Cloud** - Similar to AWS
- ❌ **Azure** - Datacenter restrictions
- ❌ **Cheap VPS** - Often blacklisted IPs

---

## 🔄 Re-deploying / Updating

### Update code on VPS:

```bash
# From your local machine
./deploy_to_vps.sh username@your_vps_ip

# Or manually
scp -r src/ username@your_vps_ip:~/ytmp3-converter/
scp test_*.py username@your_vps_ip:~/ytmp3-converter/
```

### Update dependencies:

```bash
# SSH to VPS
ssh username@your_vps_ip
cd ~/ytmp3-converter
source venv/bin/activate

# Update packages
pip install --upgrade -r requirements.txt
```

---

## 📊 Monitoring

### Check VPS IP reputation:

```bash
# SSH to VPS
ssh username@your_vps_ip

# Check IP info
curl https://ipinfo.io

# Check if IP is blacklisted
curl https://check.torproject.org/api/ip
```

### View logs:

```bash
# Create log directory
mkdir -p ~/ytmp3-converter/logs

# Run with logging
python3 test_100_requests.py 2>&1 | tee logs/test_$(date +%Y%m%d_%H%M%S).log

# View logs
tail -f logs/test_*.log
```

---

## 🎉 Success Checklist

After deployment, you should have:

- ✅ SSH access to VPS
- ✅ Python 3.8+ installed
- ✅ FFmpeg installed
- ✅ Virtual environment created
- ✅ All dependencies installed
- ✅ Project files uploaded
- ✅ Initial test completed
- ✅ Test results showing VPS rate limit status

---

## 📞 Need Help?

### Common Issues:

1. **Rate limited on VPS**: Normal for datacenter IPs, use bypass methods
2. **Slow uploads**: Normal for large files, be patient
3. **SSH timeout**: Check VPS firewall settings
4. **Python errors**: Make sure virtual environment is activated

### Debug Mode:

```bash
# Run deployment with verbose output
bash -x deploy_to_vps.sh username@your_vps_ip

# Or PowerShell
$VerbosePreference = "Continue"
.\deploy_to_vps.ps1 username@your_vps_ip
```

---

## 🚀 Next Steps

After successful deployment:

1. **Test rate limits** with different methods
2. **Compare** VPS vs local PC performance
3. **Optimize** based on results
4. **Deploy** to production if satisfied

---

**Ready to deploy!** Just run:

```bash
./deploy_to_vps.sh username@your_vps_ip
```

And you're done! 🎉
