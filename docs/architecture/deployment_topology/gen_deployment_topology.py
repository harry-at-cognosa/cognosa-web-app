#!/usr/bin/env python3
"""
Generate the Cognosa deployment topology diagram (isometric / "2.5D" inline SVG).

Usage:  python3 gen_deployment_topology.py
Writes, next to this script:
  deployment_topology.svg           the bare drawing (drop into any document)
  cognosa_deployment_topology.html  page_head.html + <figure> + svg + page_tail.html
                                    (the artifact-style page; open in a browser)

How it works:
  * Hosts and containers are declared in "world" coordinates (x, y footprint on the
    slab, z height) and projected with the standard 30-degree isometric transform in
    iso(). Screen x grows to the right-down along +x, left-down along +y.
  * box() draws the three visible faces of a cuboid and an upright label on its top.
  * platform_outline() draws a host slab; ghost platforms are the same slab, offset.
  * card() draws a flat upright rectangle for external services.
  * arrow() draws a polyline with a marker head. Convention: the arrow points from the
    client that opens the connection to the service that listens.
  * Colours are CSS classes (cmp, dat, net, vol, host, ghost, ext) resolved by the
    tokens in page_head.html, so the same SVG renders in light and dark themes.
Facts shown (hosts, instance ids, ports, images) come from
  release/ec2_ubuntu_24_04/cognosa/docker-compose.yml and ~/0_playbooks/canonical/infrastructure.md.
"""
import os
import math
C, S = math.cos(math.radians(30)), 0.5
out = []
def w(s): out.append(s)

def iso(ox, oy):
    return lambda x, y, z=0: (ox + (x - y) * C, oy + (x + y) * S - z)

def poly(pts, cls, extra=""):
    w(f'<polygon class="{cls}" points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" {extra}/>')

def box(P, x0, y0, x1, y1, h, fam, lines, sub=None, dashed=False):
    top = [P(x0,y0,h), P(x1,y0,h), P(x1,y1,h), P(x0,y1,h)]
    left = [P(x0,y1,h), P(x1,y1,h), P(x1,y1,0), P(x0,y1,0)]
    right = [P(x1,y0,h), P(x1,y1,h), P(x1,y1,0), P(x1,y0,0)]
    d = ' stroke-dasharray="5 4"' if dashed else ''
    poly(left, f"{fam} l", d); poly(right, f"{fam} r", d); poly(top, f"{fam} t", d)
    cx, cy = P((x0+x1)/2, (y0+y1)/2, h)
    n = len(lines) + (1 if sub else 0)
    y = cy - (n-1)*7 - 3
    for i, ln in enumerate(lines):
        w(f'<text class="lbl" x="{cx:.1f}" y="{y+i*14:.1f}" text-anchor="middle">{ln}</text>')
    if sub:
        w(f'<text class="sub" x="{cx:.1f}" y="{y+len(lines)*14:.1f}" text-anchor="middle">{sub}</text>')
    return (cx, cy)

def platform_outline(P, X, Y, h, cls):
    top = [P(0,0,h), P(X,0,h), P(X,Y,h), P(0,Y,h)]
    left = [P(0,Y,h), P(X,Y,h), P(X,Y,0), P(0,Y,0)]
    right = [P(X,0,h), P(X,Y,h), P(X,Y,0), P(X,0,0)]
    poly(left, cls+" l"); poly(right, cls+" r"); poly(top, cls+" t")

def card(x, y, wd, ht, cls, lines, anchor="start", size=None):
    w(f'<rect class="{cls}" x="{x}" y="{y}" width="{wd}" height="{ht}" rx="8"/>')
    tx = x+12 if anchor=="start" else x+wd/2
    n = len(lines); y0 = y + ht/2 - (n-1)*7 + 4
    for i, (ln, c) in enumerate(lines):
        w(f'<text class="{c}" x="{tx}" y="{y0+i*14:.1f}" text-anchor="{anchor}">{ln}</text>')

def arrow(p0, p1, label=None, lpos=0.5, dashed=False, trim0=0, trim1=0, both=False, dy=-6, via=None):
    pts = [p0] + (via or []) + [p1]
    # trim ends
    def trim(a, b, t):
        dx, dy_ = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy_) or 1
        return (a[0]+dx/L*t, a[1]+dy_/L*t)
    pts[0] = trim(pts[0], pts[1], trim0)
    pts[-1] = trim(pts[-1], pts[-2], trim1)
    d = ' stroke-dasharray="6 4"' if dashed else ''
    ms = ' marker-start="url(#arrowS)"' if both else ''
    w(f'<polyline class="edge" points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" marker-end="url(#arrow)"{ms}{d}/>')
    if label:
        # label along the longest segment
        segs = [(pts[i], pts[i+1]) for i in range(len(pts)-1)]
        a, b = max(segs, key=lambda s: math.hypot(s[1][0]-s[0][0], s[1][1]-s[0][1]))
        lx, ly = a[0]+(b[0]-a[0])*lpos, a[1]+(b[1]-a[1])*lpos
        lines = label if isinstance(label, list) else [label]
        for i, ln in enumerate(lines):
            w(f'<text class="elbl" x="{lx:.1f}" y="{ly+dy+i*12:.1f}" text-anchor="middle">{ln}</text>')


W, H = 1400, 880
w(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cognosa deployment: one EC2 app host per environment running six compose containers, a GPU Ollama host, four cloud LLM APIs, and the supporting AWS and external services" xmlns="http://www.w3.org/2000/svg">')
w('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>'
  '<marker id="arrowS" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M10,0 L0,5 L10,10 z" fill="currentColor"/></marker></defs>')

HX, HY = 480, 340
OX, OY = 640, 300
go = (-35, -80)
def shifted(k): return iso(OX + (go[0]*k - go[1]*k)*C, OY + (go[0]*k + go[1]*k)*S)
P_prod, P_demo, P = shifted(2), shifted(1), iso(OX, OY)

for Pg, cls, title, sub in [(P_prod, "ghost prod", "prod.cognosa.net (planned)", "same compose stack · host TBD"),
                            (P_demo, "ghost", "demo.cognosa.net · 52.13.212.94", "i-0cb656285d48d9bfc · c6a.xlarge · up 10:00–18:00 PT")]:
    platform_outline(Pg, HX, HY, 10, cls)
    tx, ty = Pg(0, 0, 10)
    w(f'<text class="ghostlbl" x="{tx+14:.1f}" y="{ty-14:.1f}">{title}</text>')
    w(f'<text class="ghostsub" x="{tx+14:.1f}" y="{ty-2:.1f}">{sub}</text>')

platform_outline(P, HX, HY, 10, "host")
bx_, by_ = P(HX, HY, 0)
tagx, tagy = P(HX-6, 6, 10)
w(f'<text class="tag" x="{tagx:.1f}" y="{tagy-6:.1f}" text-anchor="end">Docker Compose · 6 containers</text>')
w(f'<text class="hostlbl" x="{bx_:.1f}" y="{by_+22:.1f}" text-anchor="middle">dev.cognosa.net · 44.230.124.164</text>')
w(f'<text class="hostsub" x="{bx_:.1f}" y="{by_+36:.1f}" text-anchor="middle">EC2 i-01cf57d1433d161fc · c6a.xlarge · Ubuntu 24.04 · us-west-2</text>')
w(f'<text class="hostsub" x="{bx_:.1f}" y="{by_+50:.1f}" text-anchor="middle">docker compose · systemd cognosa.service · ops dir ~/cognosa · clone ~/cognosa-src</text>')

bh = 14
nginx = box(P,  30,  36, 140, 100, bh, "net", ["nginx"], "nginx:stable · 80/443")
app   = box(P, 190,  36, 300, 100, bh, "cmp", ["app"], "FastAPI + uvicorn :8000")
rt    = box(P, 350,  36, 460, 100, bh, "cmp", ["rt"], "run_tasks.py · LangChain")
cert  = box(P,  30, 180, 140, 244, bh, "net", ["certbot"], "profile tools · on demand", dashed=True)
db    = box(P, 190, 180, 300, 244, bh, "dat", ["db"], "postgres:17 · :5432")
qd    = box(P, 350, 180, 460, 244, bh, "dat", ["qdrant"], "qdrant v1.15.5 · :6333")
vhf   = box(P,  30, 278, 140, 318, 8, "vol", ["hf_cache (app + rt)"])
vpg   = box(P, 190, 278, 300, 318, 8, "vol", ["./pg_db_data"])
vqd   = box(P, 350, 278, 460, 318, 8, "vol", ["./qdrantdb"])

arrow(nginx, app, "proxy_pass app:8000", trim0=50, trim1=50, dy=-8)
arrow(app, db, ["SQLAlchemy", "asyncpg"], trim0=44, trim1=44, dy=14, lpos=0.5)
arrow(rt, db, ["polls doc_tasks, writes", "status 0 → 6 + answer"], trim0=52, trim1=52, dy=-16, lpos=0.74)
arrow(rt, qd, ["embed + search", "langchain-qdrant"], trim0=44, trim1=44, dy=16, lpos=0.5)

# GPU Ollama host
GX, GY = 200, 150
G_ox, G_oy = 1205, 592
Pg2 = iso(G_ox + 22, G_oy - 34)
platform_outline(Pg2, GX, GY, 8, "ghost")
tx, ty = Pg2(0, 0, 8)
w(f'<text class="ghostlbl" x="{tx+12:.1f}" y="{ty-12:.1f}">ollama_local / other remote</text>')
w(f'<text class="ghostsub" x="{tx+12:.1f}" y="{ty:.1f}">e.g. Mac Studio :11434</text>')
G = iso(G_ox, G_oy)
platform_outline(G, GX, GY, 8, "host")
oll = box(G, 30, 45, 170, 115, bh, "cmp", ["ollama serve"], "systemd service · :11434 · not a container")
bx2, by2 = G(GX, GY, 0)
w(f'<text class="hostlbl" x="{bx2:.1f}" y="{by2+20:.1f}" text-anchor="middle">LLM host · EC2 g6e.2xlarge</text>')
w(f'<text class="hostsub" x="{bx2:.1f}" y="{by2+34:.1f}" text-anchor="middle">NVIDIA L40S 48 GB · 300 GB gp3 · ollama_remote</text>')

# Users + cards
w('<g class="person" transform="translate(80,62)"><circle cx="22" cy="14" r="12"/><path d="M0,58 a22,22 0 0 1 44,0 z"/></g>')
w('<text class="lbl" x="136" y="78">Users</text>')
w('<text class="sub" x="136" y="93">browser · React SPA</text>')
w('<text class="sub" x="136" y="106">user · group admin · superuser</text>')
card(350, 150, 250, 64, "ext", [("Route 53 · cognosa.net zone", "lbl"), ("dev → 44.230.124.164", "sub"), ("demo → 52.13.212.94  (elastic IPs)", "sub")])
card(600, 60, 230, 64, "ext", [("Let’s Encrypt", "lbl"), ("ACME http‑01 via nginx webroot", "sub"), ("certbot renew cron Mon/Thu 03:17 UTC", "sub")])

llms = [("Qwen / Alibaba", "DashScope · OpenAI‑compatible"),
        ("ChatGPT / OpenAI", "langchain-openai"),
        ("Gemini / Google", "langchain-google-genai"),
        ("Claude / Anthropic", "langchain-anthropic")]
bx, by, cw, ch, dx, dyy = 1080, 330, 216, 56, 26, -34
for i, (n, s) in enumerate(llms):
    x, y = bx + i*dx, by + i*dyy
    w(f'<rect class="ext stack" x="{x}" y="{y}" width="{cw}" height="{ch}" rx="8"/>')
    w(f'<text class="lbl" x="{x+12}" y="{y+ch-24}">{n}</text>')
    w(f'<text class="sub" x="{x+12}" y="{y+ch-9}">{s}</text>')
w(f'<text class="sub" x="{bx}" y="{by+ch+18}">cloud LLM APIs · one group_llms row each</text>')

card(80, 290, 210, 66, "ext", [("EventBridge Scheduler", "lbl"), ("demo: start 10:00 · stop 18:00 PT", "sub"), ("dev: manual start/stop only", "sub")])
card(80, 400, 210, 66, "ext", [("Hugging Face Hub", "lbl"), ("all‑MiniLM‑L6‑v2", "sub"), ("BAAI/bge‑base‑en‑v1.5", "sub")])
card(80, 540, 210, 66, "ext", [("Developer Mac", "lbl"), ("ssh -i ctc01instance.pem ubuntu@…", "sub"), ("cd ~/cognosa && ./deploy.sh [ref]", "sub")])
card(80, 660, 210, 66, "ext", [("Git remotes", "lbl"), ("GitHub origin · GitLab mirror", "sub"), ("branch main", "sub")])

# edges
arrow((170, 112), (350, 176), "DNS lookup", dashed=True, trim0=6, trim1=4, dy=-8, lpos=0.55)
arrow((150, 118), (nginx[0]-10, nginx[1]-8), ["HTTPS 443", "HTTP 80 → 301"], trim1=34, dy=-16, lpos=0.5, via=[(150, 250), (nginx[0]-10, 250)])
arrow((715, 124), (nginx[0]+12, nginx[1]-8), ["issue / renew cert", "nginx_certs volume"], trim1=36, dy=-14, lpos=0.4, dashed=True)
arrow((290, 433), (vhf[0]-10, vhf[1]-4), ["model download", "on first use"], trim1=60, dy=-14, lpos=0.45, dashed=True)
arrow((290, 323), P_demo(0, HY, 10), "ec2:start / stopInstances", trim1=6, dashed=True, dy=-8, lpos=0.5)
arrow((290, 573), P(70, HY, 10), "ssh 22", trim1=6, dy=-8, lpos=0.45)
arrow((290, 693), P(150, HY, 10), ["deploy.sh: git pull origin/main", "compose build → up -d"], trim1=6, dy=-14, lpos=0.45)
arrow((185, 606), (185, 660), None, trim0=0, trim1=2)
w('<text class="sub" x="196" y="638">push / pull</text>')
arrow((rt[0]+36, rt[1]-6), (bx, by+ch/2), ["chat completions, streaming", "ChatOpenAI · ChatAnthropic · ChatGoogleGenerativeAI"], trim0=20, trim1=6, dy=-14, lpos=0.5)
arrow((rt[0]+36, rt[1]+10), (oll[0]-40, oll[1]-10), ["OpenAI‑compatible /v1 :11434"], trim0=20, trim1=36, dy=-8, lpos=0.55)
w('</svg>')
HERE = os.path.dirname(os.path.abspath(__file__))
svg = "\n".join(out)
open(os.path.join(HERE, "deployment_topology.svg"), "w").write(svg)
page = open(os.path.join(HERE, "page_head.html")).read() + "<figure>\n" + svg + "\n" + open(os.path.join(HERE, "page_tail.html")).read()
open(os.path.join(HERE, "cognosa_deployment_topology.html"), "w").write(page)
print("wrote deployment_topology.svg and cognosa_deployment_topology.html")
