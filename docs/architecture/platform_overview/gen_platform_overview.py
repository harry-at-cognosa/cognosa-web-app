#!/usr/bin/env python3
"""
Generate the two executive-level Cognosa overview figures (plain inline SVG).

Usage:  python3 gen_platform_overview.py
Writes, next to this script:
  request_flow.svg              Figure 1: how one question is answered (numbered flow)
  platform_layers.svg           Figure 2: what the platform is made of (layered boxes)
  cognosa_platform_overview.html  page_head.html + both figures + page_tail.html

These replace the two original hand-drawn overviews (the ChromaDB-era sequence
drawing and the generic "Enterprise RAG" layer diagram). Same facts as the three
detailed diagrams in the sibling folders, one level up: plain-language labels,
no file names, one vector database, one generic language-model box.
"""
import os

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

# ---------------------------------------------------------------- figure 1: request flow
def figure_flow():
    out = []; w = out.append
    lanes = [("user", "User", "", "ext"),
             ("web",  "Web app", "in the browser", "spa"),
             ("api",  "API server", "sign-in, records the request", "app"),
             ("eng",  "RAG engine", "background processor", "rt"),
             ("kb",   "Knowledge base", "vector database", "dat"),
             ("llm",  "Language model", "private or cloud", "ext")]
    X0, GAP, TOP, ROW = 110, 200, 150, 58
    LX = {k: X0 + i*GAP for i, (k, *_r) in enumerate(lanes)}
    steps = [
      ("user", "web", ["asks a question, picks a", "knowledge base and a model"], False),
      ("web",  "api", ["submits the question", "(signed-in user, their group)"], False),
      ("api",  "api", ["records the request;", "web app checks progress"], False),
      ("eng",  "api", ["picks up the request"], False),
      ("eng",  "kb",  ["finds the most relevant passages", "(filters, top matches)"], False),
      ("kb",   "eng", ["passages with their sources"], True),
      ("eng",  "llm", ["question + passages +", "the group's instructions"], False),
      ("llm",  "eng", ["answer, streamed as it is written"], True),
      ("eng",  "api", ["saves progress, then the", "final answer and sources"], False),
      ("web",  "user", ["shows the answer with sources"], True),
    ]
    W = X0 + (len(lanes)-1)*GAP + 110
    BOT = TOP + len(steps)*ROW + 10
    H = BOT + 20
    w(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="How Cognosa answers a question: the user asks in the web app, the API server records the request, the RAG engine retrieves passages from the knowledge base, sends them with the question to a language model, and the answer with sources is shown in the web app" xmlns="http://www.w3.org/2000/svg">')
    w('<defs><marker id="arrowF" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')
    w(f'<rect class="band" x="{LX["api"]-92}" y="{TOP-40}" width="{LX["kb"]-LX["api"]+184}" height="{BOT-TOP+40}" rx="10"/>')
    w(f'<text class="bandname" x="{LX["api"]-80}" y="{TOP-24}">back end · runs on our server</text>')
    w(f'<text class="bandname" x="{LX["llm"]-60}" y="{TOP-24}">private or cloud</text>')
    for k, t, s, cls in lanes:
        x = LX[k]
        w(f'<line class="life" x1="{x}" y1="104" x2="{x}" y2="{BOT}"/>')
        if k == "user":
            w(f'<g class="person" transform="translate({x-20},34)"><circle cx="20" cy="11" r="11"/><path d="M0,48 a20,20 0 0 1 40,0 z"/></g>')
            w(f'<text class="ltitle" x="{x}" y="{96}" text-anchor="middle">{esc(t)}</text>')
        else:
            w(f'<rect class="lane {cls}" x="{x-86}" y="40" width="172" height="58" rx="8"/>')
            w(f'<text class="ltitle" x="{x}" y="{64}" text-anchor="middle">{esc(t)}</text>')
            w(f'<text class="lsub" x="{x}" y="{82}" text-anchor="middle">{esc(s)}</text>')
    for i, (a, b, lines, dashed) in enumerate(steps):
        y = TOP + i*ROW
        xa, xb = LX[a], LX[b]
        d = ' stroke-dasharray="7 5"' if dashed else ''
        if a == b:
            w(f'<path class="msg" d="M{xa},{y-9} h30 v18 h-24" marker-end="url(#arrowF)"/>')
            mid, anchor, lx = xa, "start", xa + 38
        else:
            w(f'<line class="msg" x1="{xa}" y1="{y}" x2="{xb}" y2="{y}" marker-end="url(#arrowF)"{d}/>')
            mid, anchor, lx = (xa+xb)/2, "middle", (xa+xb)/2
        n = len(lines)
        for j, ln in enumerate(lines):
            yy = y - 8 - (n-1-j)*14 if a != b else y - 2 + (j - (n-1)/2)*14
            w(f'<text class="mlbl" x="{lx:.1f}" y="{yy:.1f}" text-anchor="{anchor}">{esc(ln)}</text>')
        bx = xa + (14 if (a == b or xb > xa) else -14)
        w(f'<circle class="badge" cx="{bx}" cy="{y}" r="10"/>')
        w(f'<text class="badgetext" x="{bx}" y="{y+3.5}" text-anchor="middle">{i+1}</text>')
    w('</svg>')
    return "\n".join(out)

# ---------------------------------------------------------------- figure 2: layers
def figure_layers():
    out = []; w = out.append
    W = 1200
    def row(y, h, title, cls, boxes, note=None):
        nmax = max(len(ls) for _t, ls in boxes)
        bh_ = 30 + nmax*15 + 6
        h = 36 + bh_ + 12
        w(f'<rect class="layer {cls}" x="30" y="{y}" width="{W-60}" height="{h}" rx="10"/>')
        w(f'<text class="rtitle" x="46" y="{y+24}">{esc(title)}</text>')
        if note: w(f'<text class="rnote" x="{W-46}" y="{y+24}" text-anchor="end">{esc(note)}</text>')
        n = len(boxes); gap = 16; bx0 = 46; bw = (W - 92 - gap*(n-1)) / n
        for i, (t, lines) in enumerate(boxes):
            x = bx0 + i*(bw+gap); by = y + 36; bh = h - 48
            w(f'<rect class="box" x="{x:.1f}" y="{by}" width="{bw:.1f}" height="{bh}" rx="7"/>')
            w(f'<text class="btitle" x="{x+bw/2:.1f}" y="{by+20}" text-anchor="middle">{esc(t)}</text>')
            for j, ln in enumerate(lines):
                w(f'<text class="bline" x="{x+bw/2:.1f}" y="{by+38+j*15}" text-anchor="middle">{esc(ln)}</text>')
        return y + h
    def down(y, label=None):
        w(f'<line class="flow" x1="{W/2}" y1="{y}" x2="{W/2}" y2="{y+14}" marker-end="url(#arrowL)"/>')
        return y + 16

    y = 20
    rows = []
    H = 900
    w(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="What the Cognosa platform is made of: people, the web application, the API server, the RAG engine, the knowledge and application data, the language model options, and the hosting" xmlns="http://www.w3.org/2000/svg">')
    w('<defs><marker id="arrowL" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')
    y = row(y, 100, "People", "ext",
            [("End users", ["ask questions, read answers", "and sources"]),
             ("Group administrators", ["manage their group's users,", "knowledge bases, retrieval settings"]),
             ("Platform administrator", ["manages groups, models,", "settings, audit log"])],
            note="each group (tenant) sees only its own data")
    y = down(y)
    y = row(y, 104, "Web application", "spa",
            [("Ask", ["choose knowledge base and model,", "ask, watch the answer arrive"]),
             ("Review", ["answer with the passages", "it was based on; export"]),
             ("Prompt templates", ["each group's instructions", "to the model"]),
             ("Administration", ["users, knowledge bases,", "models, settings, status"])])
    y = down(y)
    y = row(y, 104, "API server", "app",
            [("Sign-in and roles", ["user, group admin,", "platform admin"]),
             ("Group isolation", ["every request scoped", "to the user's group"]),
             ("Request queue and status", ["records each question;", "reports progress"]),
             ("Configuration and audit", ["models, knowledge bases,", "settings, change log"])])
    y = down(y)
    y = row(y, 104, "RAG engine", "rt",
            [("1 · Embed", ["turn the question into", "a vector"]),
             ("2 · Retrieve", ["most relevant passages,", "with metadata filters"]),
             ("3 · Compose", ["group template + passages", "+ question"]),
             ("4 · Generate", ["language model writes", "the answer, streamed"])],
            note="built on LangChain · runs in the background, several requests at once")
    y = down(y)
    y = row(y, 118, "Knowledge and application data", "dat",
            [("Document ingestion", ["PDF, DOCX, PPTX, XLSX, TXT", "split into passages with", "metadata, one tool run per set"]),
             ("Knowledge base", ["vector database (Qdrant)", "one collection per", "knowledge base"]),
             ("Application database", ["PostgreSQL: users, groups,", "settings, requests, answers,", "audit log"])])
    y = down(y)
    y = row(y, 104, "Language models", "ext",
            [("Private model", ["open-source model on", "our own GPU server (Ollama)"]),
             ("Cloud model service", ["OpenAI, Anthropic, Google,", "Alibaba, via their APIs"]),
             ("Chosen per group", ["any mix; the model is", "picked when asking"])])
    y = down(y)
    y = row(y, 72, "Hosting", "host",
            [("One server per environment", ["AWS EC2: dev, demo, prod"]),
             ("Containers", ["web + API, engine, databases"]),
             ("Secure access", ["HTTPS, certificates renewed automatically"])])
    out[0] = out[0].replace(f'viewBox="0 0 {W} {H}"', f'viewBox="0 0 {W} {y+20}"')
    w('</svg>')
    return "\n".join(out)

HERE = os.path.dirname(os.path.abspath(__file__))
f1, f2 = figure_flow(), figure_layers()
open(os.path.join(HERE, "request_flow.svg"), "w").write(f1)
open(os.path.join(HERE, "platform_layers.svg"), "w").write(f2)
head = open(os.path.join(HERE, "page_head.html")).read()
tail = open(os.path.join(HERE, "page_tail.html")).read()
mid = open(os.path.join(HERE, "page_mid.html")).read()
page = head + "<figure>\n" + f1 + "\n" + mid + "<figure>\n" + f2 + "\n" + tail
open(os.path.join(HERE, "cognosa_platform_overview.html"), "w").write(page)
print("wrote request_flow.svg, platform_layers.svg, cognosa_platform_overview.html")
