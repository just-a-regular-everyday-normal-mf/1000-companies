# Vercel Python function: stores all applications in one apps.json inside Vercel Blob.
# Standard library only, no requirements.txt needed. Token is auto-added by Vercel (BLOB_READ_WRITE_TOKEN).
import json, os, time, urllib.request
from http.server import BaseHTTPRequestHandler

API = "https://blob.vercel-storage.com"
NAME = "apps.json"
HDR = {"User-Agent": "tracker/1.0"}

def token():
    return os.environ["BLOB_READ_WRITE_TOKEN"]

def read_apps():
    req = urllib.request.Request(
        f"{API}/?prefix={NAME}&limit=5",
        headers={**HDR, "authorization": f"Bearer {token()}", "x-api-version": "7"})
    blobs = json.load(urllib.request.urlopen(req, timeout=15)).get("blobs", [])
    blobs = [b for b in blobs if b["pathname"] == NAME]
    if not blobs:
        return b"[]"
    url = blobs[0]["url"] + f"?t={int(time.time()*1000)}"  # cache-buster
    return urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=15).read()

def write_apps(body):
    req = urllib.request.Request(
        f"{API}/{NAME}", data=body, method="PUT",
        headers={**HDR, "authorization": f"Bearer {token()}", "x-api-version": "7",
                 "x-content-type": "application/json", "x-add-random-suffix": "0",
                 "x-allow-overwrite": "1", "x-cache-control-max-age": "0"})
    urllib.request.urlopen(req, timeout=15).read()

class handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            self._send(200, read_apps())
        except Exception as e:
            self._send(500, str(e).encode(), "text/plain")

    def do_PUT(self):
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            json.loads(body)  # validate
            write_apps(body)
            self._send(200, b"ok", "text/plain")
        except Exception as e:
            self._send(500, str(e).encode(), "text/plain")
