"""
Production launcher for Airfare Intelligence Platform.
Starts the resilient FastAPI server and provisions a live public HTTPS Cloudflare tunnel.

Usage: py -3 start_production.py
"""
import sys, os, time, subprocess, re, urllib.request, json

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

print("=" * 65)
print("AIRFARE INTELLIGENCE PLATFORM — PRODUCTION LAUNCHER")
print("=" * 65)

# 1. Start Server
print("[1/2] Starting FastAPI backend on http://127.0.0.1:8000...")
server_proc = subprocess.Popen(
    ["py", "-3", "run_server.py"],
    cwd=PROJECT_ROOT,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait for server to be responsive
time.sleep(3)
for _ in range(15):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as r:
            if r.status == 200:
                print("      FastAPI Backend is ONLINE (200 OK)")
                break
    except Exception:
        time.sleep(1)

# 2. Start Cloudflare Tunnel
cloudflared_bin = os.path.join(PROJECT_ROOT, "bin", "cloudflared.exe")
if not os.path.exists(cloudflared_bin):
    print(f"Error: {cloudflared_bin} not found.")
    sys.exit(1)

print("[2/2] Launching Cloudflare public HTTPS tunnel...")
tunnel_proc = subprocess.Popen(
    [cloudflared_bin, "tunnel", "--url", "http://127.0.0.1:8000"],
    cwd=PROJECT_ROOT,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

public_url = None
start_t = time.time()
for line in iter(tunnel_proc.stdout.readline, ""):
    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
    if match:
        public_url = match.group(0)
        break
    if time.time() - start_t > 30:
        break

if public_url:
    print("\n" + "=" * 65)
    print("PRODUCTION DEPLOYMENT SUCCESSFUL!")
    print("=" * 65)
    print(f"FRONTEND UI URL : {public_url}/app/")
    print(f"BACKEND URL     : {public_url}/")
    print(f"API DOCS (SWAG) : {public_url}/docs")
    print(f"HEALTH ENDPOINT : {public_url}/health")
    print("=" * 65)
else:
    print("Failed to acquire public Cloudflare URL within 30s.")
