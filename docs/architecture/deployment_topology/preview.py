#!/usr/bin/env python3
"""Render cognosa_deployment_topology.html to preview.png with Playwright (optional check)."""
import os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
html = ('<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0">'
        + open(os.path.join(HERE, "cognosa_deployment_topology.html")).read() + "</body></html>")
tmp = os.path.join(HERE, "_preview.html"); open(tmp, "w").write(html)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1300, "height": 1100})
    pg.goto("file://" + tmp); pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(HERE, "preview.png"), full_page=True); b.close()
os.remove(tmp); print("wrote preview.png")
