# Smart Proxy Converter - Quick Guide

## 🚀 Cara Pakai

### 1. Buat urls.txt
```bash
cat > urls.txt << 'EOF'
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
EOF
```

### 2. Run
```bash
python3 convert_with_proxy.py
```

## ✅ Fitur

- ✅ Proxy HANYA untuk metadata (~50KB per video)
- ✅ Download langsung tanpa proxy (~10MB per video)  
- ✅ Save 99% bandwidth proxy
- ✅ Auto-load dari proxies.txt (100 proxies)
- ✅ Auto-rotation
- ✅ Health checking

## 📊 Bandwidth

```
Per video:
  Metadata via proxy: 50 KB
  Download direct: 10 MB
  Proxy usage: 0.5% only!

1000 videos:
  Proxy bandwidth: 50 MB
  Direct bandwidth: 10 GB
  Cost: $0.09 (vs $17.50 full proxy)
```

## 🔧 Files

- `convert_with_proxy.py` - Main script
- `proxies.txt` - 100 proxies (IP-whitelisted)
- `urls.txt` - YouTube URLs
- `src/proxy_manager.py` - Proxy rotation
- `src/smart_downloader.py` - Hybrid method

## 📝 Deploy ke VPS

```bash
# Pull latest
cd ~/ytmp3-converter
git pull origin main
source venv/bin/activate

# Run
python3 convert_with_proxy.py
```

Done! 🎉
