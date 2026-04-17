# Browser Cookies Solution - Bypass Bot Detection

## 🎯 Problem

VPS datacenter IPs get blocked by YouTube with "Sign in to confirm you're not a bot" error, even with proxies.

## ✅ Solution: Browser Cookies from Residential IP

Export cookies from your browser (residential IP) and use them on VPS. YouTube will think the VPS is your residential PC.

---

## 📋 Step-by-Step Guide

### Step 1: Export Cookies from Your PC (Residential IP)

**Option A: Chrome**
1. Install extension: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Go to `youtube.com` (login if not already)
3. Click extension icon
4. Click "Export" → Save as `cookies.txt`

**Option B: Firefox**
1. Install extension: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Go to `youtube.com` (login if not already)
3. Click extension icon
4. Click "Export" → Save as `cookies.txt`

**Option C: Edge**
1. Install extension: [Get cookies.txt LOCALLY](https://microsoftedge.microsoft.com/addons/detail/get-cookiestxt-locally/cdaojjdokolhkfbkaamjplaecpphhmoa)
2. Go to `youtube.com` (login if not already)
3. Click extension icon
4. Click "Export" → Save as `cookies.txt`

### Step 2: Upload Cookies to VPS

**Using SCP (from your PC):**
```bash
scp cookies.txt user@your-vps-ip:/path/to/ytmp3-converter/
```

**Or using SFTP client:**
- FileZilla, WinSCP, etc.
- Upload `cookies.txt` to `/path/to/ytmp3-converter/`

### Step 3: Run Converter on VPS

```bash
cd ytmp3-converter
python3 convert_with_cookies.py
```

---

## 🔄 How It Works

1. **Export cookies** from your browser (residential IP)
2. **Upload cookies** to VPS
3. **VPS uses cookies** when downloading
4. **YouTube thinks** VPS = your residential PC
5. **No bot detection!**

---

## ⚠️ Important Notes

**Cookie Expiration:**
- Cookies expire after ~6 months
- Re-export and upload when they expire
- You'll know when you get bot detection errors again

**Security:**
- Cookies contain your YouTube session
- Don't share cookies.txt with others
- Keep cookies.txt private

**Login Status:**
- You don't need to be logged in to YouTube
- But being logged in may help
- Cookies work for both logged in and logged out

---

## 📊 Comparison

| Method | Metadata | Download | Cost | Success Rate |
|--------|----------|----------|------|--------------|
| **API + Cookies** | API (free) | Cookies (free) | FREE | ~95%+ |
| API + Proxy | API (free) | Proxy (paid) | $$ | ~80% |
| Direct | yt-dlp | yt-dlp | FREE | 0% (VPS) |

---

## 🎯 Recommended Solution

**For VPS:** API + Cookies (this method)
- ✓ FREE
- ✓ No proxy costs
- ✓ High success rate
- ✓ Simple setup

---

## 🚀 Quick Start

```bash
# 1. Export cookies from your browser
# 2. Upload cookies.txt to VPS
# 3. Run converter
python3 convert_with_cookies.py
```

That's it! 🎉
