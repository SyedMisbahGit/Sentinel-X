#!/usr/bin/env python3
import sys
WORDS = ["dev", "staging", "test", "prod", "beta", "admin", "internal", "vpn", "api", "backend", "demo", "stage", "corp"]
try:
    lines = [line.strip() for line in open(sys.argv[1]) if line.strip()]
    mutations = set()
    for d in lines:
        parts = d.split('.')
        if len(parts) == 2:
            for w in WORDS: mutations.add(f"{w}.{d}")
        elif len(parts) > 2:
            sub, root = parts[0], ".".join(parts[1:])
            for w in WORDS:
                mutations.add(f"{sub}-{w}.{root}")
                mutations.add(f"{w}-{sub}.{root}")
    for m in mutations: print(m)
except: pass
