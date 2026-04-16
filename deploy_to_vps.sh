#!/bin/bash

################################################################################
# YouTube to MP3 Converter - VPS Deployment Script
# 
# Usage: ./deploy_to_vps.sh username@vps_ip
# Example: ./deploy_to_vps.sh root@192.168.1.100
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check arguments
if [ $# -eq 0 ]; then
    print_error "Usage: $0 username@vps_ip"
    print_info "Example: $0 root@192.168.1.100"
    exit 1
fi

VPS_HOST=$1
PROJECT_NAME="ytmp3-converter"
REMOTE_DIR="~/$PROJECT_NAME"

print_header "VPS Deployment Script"
echo ""
print_info "Target: $VPS_HOST"
print_info "Project: $PROJECT_NAME"
echo ""

# Step 1: Test SSH connection
print_header "Step 1: Testing SSH Connection"
if ssh -o ConnectTimeout=5 -o BatchMode=yes $VPS_HOST exit 2>/dev/null; then
    print_success "SSH connection successful"
else
    print_error "Cannot connect to VPS. Please check:"
    echo "  1. VPS IP address is correct"
    echo "  2. SSH key is configured"
    echo "  3. VPS is running"
    echo ""
    print_info "Trying with password authentication..."
    if ! ssh -o ConnectTimeout=10 $VPS_HOST exit; then
        print_error "Connection failed. Exiting."
        exit 1
    fi
fi
echo ""

# Step 2: Install dependencies on VPS
print_header "Step 2: Installing Dependencies on VPS"
ssh $VPS_HOST << 'ENDSSH'
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
ENDSSH

print_success "Dependencies installed"
echo ""

# Step 3: Create project directory
print_header "Step 3: Creating Project Directory"
ssh $VPS_HOST "mkdir -p $REMOTE_DIR"
print_success "Directory created: $REMOTE_DIR"
echo ""

# Step 4: Upload project files
print_header "Step 4: Uploading Project Files"

print_info "Uploading source files..."
scp -r src/ $VPS_HOST:$REMOTE_DIR/ > /dev/null 2>&1
print_success "src/ uploaded"

print_info "Uploading test scripts..."
scp test_*.py $VPS_HOST:$REMOTE_DIR/ > /dev/null 2>&1
print_success "Test scripts uploaded"

print_info "Uploading configuration files..."
scp requirements.txt $VPS_HOST:$REMOTE_DIR/ > /dev/null 2>&1
scp main.py $VPS_HOST:$REMOTE_DIR/ > /dev/null 2>&1 || true
scp batch_convert.py $VPS_HOST:$REMOTE_DIR/ > /dev/null 2>&1 || true
scp advanced_batch_convert.py $VPS_HOST:$REMOTE_DIR/ > /dev/null 2>&1 || true
print_success "Configuration files uploaded"

print_info "Uploading documentation..."
scp *.md $VPS_HOST:$REMOTE_DIR/ > /dev/null 2>&1 || true
print_success "Documentation uploaded"

echo ""

# Step 5: Setup Python environment
print_header "Step 5: Setting Up Python Environment"
ssh $VPS_HOST << ENDSSH
set -e
cd $REMOTE_DIR

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo "✓ Python environment ready"
ENDSSH

print_success "Python environment configured"
echo ""

# Step 6: Create test runner script
print_header "Step 6: Creating Test Runner Script"
ssh $VPS_HOST << 'ENDSSH'
cd ~/ytmp3-converter

cat > run_tests.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
source venv/bin/activate

echo ""
echo "================================"
echo "VPS Rate Limiting Test Suite"
echo "================================"
echo ""

# Test 1: Quick test (25 requests)
echo "Test 1: Quick Test (25 requests, no bypass)"
echo "-------------------------------------------"
python3 test_100_requests.py

echo ""
echo "================================"
echo "Tests completed!"
echo "================================"
echo ""
echo "To run more tests:"
echo "  python3 test_all_bypass_methods.py  # Test all methods (100 req each)"
echo "  python3 test_100_requests.py        # Progressive test"
echo ""
EOF

chmod +x run_tests.sh

echo "✓ Test runner created"
ENDSSH

print_success "Test runner script created"
echo ""

# Step 7: Run initial test
print_header "Step 7: Running Initial Test"
print_info "This will test 25 requests to check VPS rate limiting..."
echo ""

ssh $VPS_HOST << 'ENDSSH'
cd ~/ytmp3-converter
source venv/bin/activate

# Create quick test script
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
    print("  Recommendation: No bypass needed")
elif rate_limited <= 5 and success >= 20:
    print("  ✓ GOOD - Minor rate limiting")
    print("  Recommendation: Use delays (1-2s)")
elif rate_limited <= 10 and success >= 15:
    print("  ⚠️  FAIR - Moderate rate limiting")
    print("  Recommendation: Use all bypass methods + 2-3s delays")
else:
    print("  ❌ POOR - Heavy rate limiting")
    print("  Recommendation: VPS IP is restricted")
    print("  Consider:")
    print("    - Using residential proxy")
    print("    - Different VPS provider")
    print("    - Longer delays (5s+)")

print()
print("="*60)
EOF

python3 quick_test.py
ENDSSH

echo ""
print_success "Initial test completed"
echo ""

# Final instructions
print_header "Deployment Complete!"
echo ""
print_success "Project deployed to: $VPS_HOST:$REMOTE_DIR"
echo ""
print_info "To access your VPS:"
echo "  ssh $VPS_HOST"
echo ""
print_info "To run tests:"
echo "  cd $REMOTE_DIR"
echo "  source venv/bin/activate"
echo "  ./run_tests.sh"
echo ""
print_info "Available test scripts:"
echo "  python3 quick_test.py                  # Quick 25 request test"
echo "  python3 test_100_requests.py           # Progressive test (25→100)"
echo "  python3 test_all_bypass_methods.py     # Test all methods (100 each)"
echo ""
print_info "To convert videos:"
echo "  python3 main.py 'YOUTUBE_URL'"
echo "  python3 batch_convert.py urls.txt"
echo "  python3 advanced_batch_convert.py urls.txt"
echo ""
print_header "Happy Testing! 🚀"
