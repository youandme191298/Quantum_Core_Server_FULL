# -*- coding: utf-8 -*-
import os, time, threading
def start_watcher(path="core", interval=3, on_change=None):
    seen = {}
    while True:
        try:
            files = [f for f in os.listdir(path) if f.endswith(".py")]
        except FileNotFoundError:
            files = []
        changed = []
        for fn in files:
            p = os.path.join(path, fn)
            ts = os.path.getmtime(p)
            if fn not in seen or seen[fn] != ts:
                seen[fn] = ts
                changed.append(fn)
        if changed and on_change:
            for c in changed:
                try:
                    on_change(c)
                except Exception:
                    pass
        time.sleep(interval)
