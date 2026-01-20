#!/usr/bin/env python3
import mmh3, requests, codecs, sys, random
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

def get_hash(content): return mmh3.hash(codecs.encode(content, "base64"))

def solve_favicon(domain, subs_file=None):
    print(f"[*] Starting Favicon Hunt for: {domain}", file=sys.stderr)
    targets = [f"https://{domain}", f"https://www.{domain}"]
    if subs_file:
        try:
            with open(subs_file) as f:
                lines = [l.strip() for l in f if l.strip()]
                random.shuffle(lines)
                targets += lines[:30]
        except: pass

    try:
        g_url = f"https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://{domain}&size=64"
        r = requests.get(g_url, headers=HEADERS, timeout=5)
        if r.status_code == 200 and len(r.content) > 0:
            print(f"    -> [Google Cache] Hash: {get_hash(r.content)}")
    except: pass

    for url in targets:
        if not url.startswith("http"): url = "https://" + url
        try:
            r = requests.get(f"{url}/favicon.ico", headers=HEADERS, timeout=3, verify=False)
            if r.status_code == 200 and len(r.content) > 0:
                h = get_hash(r.content)
                if h == 0: continue
                print(f"\n\033[92m[+] SUCCESS: {url}\033[0m")
                print(f"\033[92m[+] FAVICON HASH: {h}\033[0m")
                print(f"    -> https://www.shodan.io/search?query=http.favicon.hash:{h}")
                return
        except: pass

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if len(sys.argv) > 1:
        solve_favicon(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
