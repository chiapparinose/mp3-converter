# YouTube to MP3 Converter - VPS Deployment Script (PowerShell)
# 
# Usage: .\deploy_to_vps.ps1 username@vps_ip
# Example: .\deploy_to_vps.ps1 root@192.168.1.100

param(
    [Parameter(Mandatory=$true)]
    [string]$VpsHost
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Header {
    param([string]$Message)
    Write-Host "`n================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Yellow
}

$ProjectName = "ytmp3-converter"
$RemoteDir = "~/$ProjectName"

Write-Header "VPS Deployment Script"
Write-Info "Target: $VpsHost"
Write-Info "Project: $ProjectName"

# Step 1: Test SSH connection
Write-Header "Step 1: Testing SSH Connection"
try {
    ssh -o ConnectTimeout=5 $VpsHost "exit"
    Write-Success "SSH connection successful"
} catch {
    Write-Error-Custom "Cannot connect to VPS"
    Write-Info "Please check:"
    Write-Host "  1. VPS IP address is correct"
    Write-Host "  2. SSH key is configured"
    Write-Host "  3. VPS is running"
    exit 1
}

# Step 2: Install dependencies
Write-Header "Step 2: Installing Dependencies on VPS"
$installScript = @'
set -e
echo "Updating system packages..."
sudo apt update -qq
echo "Installing Python 3, pip, and FFmpeg..."
sudo apt install -y python3 python3-pip python3-venv ffmpeg > /dev/null 2>&1
echo "Verifying installations..."
python3 --version
pip3 --version
ffmpeg -version | head -n 1
echo "✓ All dependencies installed"
'@

ssh $VpsHost $installScript
Write-Success "Dependencies installed"

# Step 3: Create project directory
Write-Header "Step 3: Creating Project Directory"
ssh $VpsHost "mkdir -p $RemoteDir"
Write-Success "Directory created: $RemoteDir"

# Step 4: Upload project files
Write-Header "Step 4: Uploading Project Files"

Write-Info "Uploading source files..."
scp -r src/ "${VpsHost}:${RemoteDir}/" | Out-Null
Write-Success "src/ uploaded"

Write-Info "Uploading test scripts..."
scp test_*.py "${VpsHost}:${RemoteDir}/" | Out-Null
Write-Success "Test scripts uploaded"

Write-Info "Uploading configuration files..."
scp requirements.txt "${VpsHost}:${RemoteDir}/" | Out-Null
scp main.py "${VpsHost}:${RemoteDir}/" 2>$null | Out-Null
scp batch_convert.py "${VpsHost}:${RemoteDir}/" 2>$null | Out-Null
scp advanced_batch_convert.py "${VpsHost}:${RemoteDir}/" 2>$null | Out-Null
Write-Success "Configuration files uploaded"

Write-Info "Uploading documentation..."
scp *.md "${VpsHost}:${RemoteDir}/" 2>$null | Out-Null
Write-Success "Documentation uploaded"

# Step 5: Setup Python environment
Write-Header "Step 5: Setting Up Python Environment"
$setupScript = @"
set -e
cd $RemoteDir
echo 'Creating virtual environment...'
python3 -m venv venv
echo 'Activating virtual environment...'
source venv/bin/activate
echo 'Installing Python dependencies...'
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo '✓ Python environment ready'
"@

ssh $VpsHost $setupScript
Write-Success "Python environment configured"

# Step 6: Create test runner
Write-Header "Step 6: Creating Test Runner Script"
$testRunnerScript = @'
cd ~/ytmp3-converter
cat > run_tests.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
echo ""
echo "================================"
echo "VPS Rate Limiting Test Suite"
echo "================================"
echo ""
echo "Test 1: Quick Test (25 requests, no bypass)"
echo "-------------------------------------------"
python3 test_100_requests.py
echo ""
echo "================================"
echo "Tests completed!"
echo "================================"
EOF
chmod +x run_tests.sh
echo "✓ Test runner created"
'@

ssh $VpsHost $testRunnerScript
Write-Success "Test runner script created"

# Step 7: Run initial test
Write-Header "Step 7: Running Initial Test"
Write-Info "Testing 25 requests to check VPS rate limiting..."

$quickTestScript = @'
cd ~/ytmp3-converter
source venv/bin/activate
cat > quick_test.py << 'EOF'
#!/usr/bin/env python3
import sys
import time
from src.video_downloader import VideoDownloader

TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
]

print("\n" + "="*60)
print("VPS Quick Test - 25 Requests")
print("="*60 + "\n")

downloader = VideoDownloader(use_cookies=False, rotate_user_agent=False)

success = 0
failed = 0
rate_limited = 0
start_time = time.time()

urls = [TEST_URLS[i % len(TEST_URLS)] for i in range(25)]

for i, url in enumerate(urls):
    print(f"[{i+1}/25]", end=' ', flush=True)
    
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
        if any(kw in error_msg for kw in ['rate limit', 'bot', '429', 'sign in']):
            rate_limited += 1
            print("⚠️", end='', flush=True)
        else:
            failed += 1
            print("✗", end='', flush=True)
    
    if (i + 1) % 10 == 0:
        print(f" [{success}/{i+1}]", end='', flush=True)

total_time = time.time() - start_time

print(f"\n\n📊 Results:")
print(f"  Success: {success}/25 ({success/25*100:.1f}%)")
print(f"  Failed: {failed}")
print(f"  Rate Limited: {rate_limited}")
print(f"  Time: {total_time:.1f}s ({25/total_time*60:.1f} req/min)")
print()

if rate_limited == 0 and success >= 24:
    print("  ✅ EXCELLENT - VPS has good IP!")
elif rate_limited <= 5 and success >= 20:
    print("  ✓ GOOD - Minor rate limiting")
elif rate_limited <= 10 and success >= 15:
    print("  ⚠️  FAIR - Moderate rate limiting")
else:
    print("  ❌ POOR - Heavy rate limiting")

print()
print("="*60)
EOF
python3 quick_test.py
'@

ssh $VpsHost $quickTestScript

Write-Success "Initial test completed"

# Final instructions
Write-Header "Deployment Complete!"
Write-Success "Project deployed to: ${VpsHost}:${RemoteDir}"
Write-Info "To access your VPS:"
Write-Host "  ssh $VpsHost"
Write-Info "To run tests:"
Write-Host "  cd $RemoteDir"
Write-Host "  source venv/bin/activate"
Write-Host "  ./run_tests.sh"
Write-Header "Happy Testing! 🚀"
