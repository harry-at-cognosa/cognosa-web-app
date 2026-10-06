#!/usr/bin/env python3
"""
Generate the Cognosa component / software-stack diagram (flat inline SVG).

Usage:  python3 gen_component_stack.py
Writes, next to this script:
  component_stack.svg            the bare drawing
  cognosa_component_stack.html   page_head.html + <figure> + svg + page_tail.html

Model: four columns, one per runtime process or tool set (React SPA, app, rt,
offline tools). Inside each column the panels are the repo packages that make it
up, top to bottom in call order, with the third-party library band at the foot.
A shared `common/` band spans the two Python processes. Data stores and LLM
endpoints sit on the bottom row. Arrows show which process opens which connection.
Facts come from docs/PROJECT_STRUCTURE.md, backend/requirements.txt, frontend/package.json.
"""
import os
out = []
def w(s): out.append(s)
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def panel(x, y, wd, ht, title, cls="pnl", sub=None):
    w(f'<rect class="{cls}" x="{x}" y="{y}" width="{wd}" height="{ht}" rx="6"/>')
    w(f'<text class="ptitle" x="{x+10}" y="{y+17}">{esc(title)}</text>')
    if sub: w(f'<text class="psub" x="{x+wd-10}" y="{y+17}" text-anchor="end">{esc(sub)}</text>')

def items(x, y, lines, cls="item", lh=14):
    for i, ln in enumerate(lines):
        w(f'<text class="{cls}" x="{x}" y="{y+i*lh}">{esc(ln)}</text>')

def chips(x, y, wd, labels, cls="chip"):
    """flow-wrap small pills; returns y after last row"""
    cx, cy = x, y
    for lb in labels:
        cw = 7.2*len(lb) + 16
        if cx + cw > x + wd: cx, cy = x, cy + 22
        w(f'<rect class="{cls}" x="{cx}" y="{cy}" width="{cw:.0f}" height="18" rx="9"/>')
        w(f'<text class="chiptext" x="{cx+cw/2:.1f}" y="{cy+12.5}" text-anchor="middle">{esc(lb)}</text>')
        cx += cw + 6
    return cy + 22

def arrow(p0, p1, label=None, dashed=False, via=None, dy=-5, lpos=0.5):
    pts = [p0] + (via or []) + [p1]
    d = ' stroke-dasharray="6 4"' if dashed else ''
    w(f'<polyline class="edge" points="{" ".join(f"{x},{y}" for x,y in pts)}" marker-end="url(#arrow)"{d}/>')
    if label:
        import math
        segs = [(pts[i], pts[i+1]) for i in range(len(pts)-1)]
        a, b = max(segs, key=lambda s: math.hypot(s[1][0]-s[0][0], s[1][1]-s[0][1]))
        lx, ly = a[0]+(b[0]-a[0])*lpos, a[1]+(b[1]-a[1])*lpos
        for i, ln in enumerate(label if isinstance(label, list) else [label]):
            w(f'<text class="elbl" x="{lx:.1f}" y="{ly+dy+i*12:.1f}" text-anchor="middle">{esc(ln)}</text>')


import textwrap
CH = 6.35   # px per monospace char at 10.5px

def wrap(lines, wd):
    maxc = int((wd - 20) / CH)
    outl = []
    for ln in lines:
        ind = len(ln) - len(ln.lstrip(' '))
        outl += textwrap.wrap(ln, maxc, subsequent_indent=' ' * (ind + 3)) or ['']
    return outl

def stack(x, wd, y, panels, gap=10):
    """panels: list of (title, sub, lines, cls). returns y after last."""
    for title, sub, lines, cls in panels:
        ls = wrap(lines, wd)
        ht = 30 + len(ls) * 14 + 4 if ls else 30
        panel(x, y, wd, ht, title, cls=cls, sub=sub)
        items(x + 10, y + 40, ls)
        y += ht + gap
    return y

W, H = 1400, 1080
w(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cognosa component stack: React SPA, FastAPI app process, run_tasks process, offline tools, the shared common package, and the data stores and LLM endpoints they connect to" xmlns="http://www.w3.org/2000/svg">')
w('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')

COLS = {
  "spa":   (30,   290, "React SPA (browser)",   "frontend/src · Vite build → backend/static"),
  "app":   (350,  310, "app · FastAPI process", "backend/webapp.py → cwa_lib/"),
  "rt":    (690,  420, "rt · task processor",   "backend/run_tasks.py → tasks_lib/"),
  "tools": (1130, 240, "Offline tools",         "backend/*.py · tools/"),
}
TOP, PAD = 60, 12
content = {
 "spa": [
  ("pages/", "React Router", [
    "QueryDocuments · ManageContexts · HomePage",
    "Ga*: ManageUsers · ManageVDBs · ManageDocTasks · GVDBsRetrParams",
    "Su*: ManageGroups · ManageUsers · ManageLLMs · ManageVDBs · ManageApiSettings · ManageLogCRUD · ServerStatus",
    "guards: GroupAdminRoute · SuperUserRoute",
    "QueryDocuments polls doc_tasks until status ≥ 6"], "pnl"),
  ("stores/ · tables/ · components/", None, [
    "Zustand: useLoggedUserStore · useWebAppOptionsStore · per-page stores (createResettableStore)",
    "UniversalTable + TableStoreFactory (CRUD grids)",
    "GVDBsRetrParams / GVDBsRetrFilters editors",
    "MarkdownRenderer · TopNavBar · ThemeColor"], "pnl"),
  ("api/", None, [
    "axiosClient: JWT bearer, 401 → logout",
    "apiURL: /api/v1 prefix · NavigationInjector"], "pnl"),
 ],
 "app": [
  ("cwa_lib/app.py · users.py", "uvicorn webapp:app", [
    "FastAPI app factory · CORS · static SPA mount",
    "fastapi-users JWT (7-day), username-or-email login",
    "middleware/last_seen · Depends() auth guards",
    "roles: user · group admin · superuser"], "pnl"),
  ("routers/ → pages/ → sql_tables/", "/api/v1/*", [
    "user: doc_tasks · manage_contexts · users · misc · webapp_options",
    "ga_*: manage_users · manage_vdbs · manage_doc_tasks · settings (retrieval params)",
    "su_*: groups · users · llms · vdbs · api_settings · doc_tasks · log_crud · server_status · change_oneself",
    "pages/ = handlers · sql_tables/ = repositories"], "pnl"),
  ("pydantic_schemas/ · validators/", None, [
    "request / response models per router",
    "doc_tasks create: snapshots the group_vdbs and group_llms rows into the task"], "pnl"),
  ("alembic/", "migrations", [], "pnl"),
 ],
 "rt": [
  ("run_tasks.py · main_iteration.py", "1 process", [
    "poll doc_tasks WHERE status IN (0, 3) FOR UPDATE SKIP LOCKED",
    "qd_lib/qd_init → VDB queue · qd_lib/qd_vdb_fetched → LLM thread",
    "group_vdbs_tasks: refresh filter select values"], "pnl"),
  ("vdb_lib/", "RT_VDB_PROCESS_NUM processes", [
    "VDBWorker(Process) reads a multiprocessing Queue",
    "emb_models: HuggingFaceEmbeddings, preloaded per model name",
    "vdb_ops → qdrant_ops | chromadb_ops | pgvector_ops",
    "qdrant_filters: payload filter from group retrieval filters",
    "retriever: similarity · mmr · similarity_score_threshold (k, fetch_k, lambda_mult, score_threshold)",
    "found_documents → doc_tasks.context_json"], "pnl"),
  ("llm_lib/", "1 thread per task", [
    "LLMWorker(Thread) · llm_ops: prepare_context + chain",
    "llm_type_openai: ChatGPT · Qwen · Ollama local / remote",
    "llm_type_claude · llm_type_gemini · tiktoken_count",
    "chain: {context, question} | PromptTemplate | llm | StrOutputParser, run with .stream()"], "pnl"),
  ("entities/ · vdb_llm_status_worker.py · watchdogs", None, [
    "queue messages · VDB / LLM availability checks → api_processes"], "pnl"),
 ],
 "tools": [
  ("ingestion", None, [
    "document_loader_qdrant.py · document_loader_pgvector.py",
    "tools/ingest_dev/: casambi_*, furocad_book_loader.py",
    "multi-strategy chunking, metadata per document class"], "pnl"),
  ("database", None, [
    "init_sql_db.py (.init_sql_data/)",
    "create_user.py · alembic upgrade head",
    "tools/db: backup / restore"], "pnl"),
  ("checks", None, [
    "check_qdrant_server.py · check_pgvector.py · check_chroma_server.py"], "pnl"),
 ],
}
libs = {
 "spa": ["React 19", "TypeScript 5.8", "Vite 7", "react-router-dom 7", "React Bootstrap 2.10", "Bootstrap Icons", "Zustand 5", "Axios", "react-markdown", "rehype-highlight", "SheetJS xlsx"],
 "app": ["FastAPI 0.116", "Uvicorn", "fastapi-users 14", "Pydantic v2", "SQLAlchemy 2 async", "asyncpg", "Alembic", "Jinja2"],
 "rt": ["LangChain core 1.0", "langchain-huggingface", "sentence-transformers", "langchain-qdrant", "qdrant-client", "langchain-chroma", "langchain-community PGVector", "langchain-openai", "langchain-anthropic", "langchain-google-genai", "tiktoken", "SQLAlchemy 2 sync", "psycopg2", "multiprocessing", "threading"],
 "tools": ["community loaders", "text splitters", "pypdf", "docx2txt", "python-pptx", "openpyxl", "unstructured", "pg_dump"],
}
# pass 1: stacks
ends = {}
for k, (cx, cw, t, s) in COLS.items():
    ends[k] = stack(cx + PAD, cw - 2*PAD, TOP + 52, content[k])
lib_y = max(ends.values()) + 2
# pass 2: library bands, measure height
lib_end = {}
for k, (cx, cw, t, s) in COLS.items():
    y2 = chips(cx + PAD + 10, lib_y + 26, cw - 2*PAD - 20, libs[k])
    lib_end[k] = y2
lib_h = max(lib_end.values()) - lib_y + 4
# common band under app, rt, tools
com_y = lib_y + lib_h + 12
com_x, com_w = COLS["app"][0] + PAD, COLS["tools"][0] + COLS["tools"][1] - PAD - (COLS["app"][0] + PAD)
com_lines = wrap([
  "sql_models/: api_groups · api_users · group_llms · group_vdbs · group_contexts · doc_tasks · api_settings · api_processes · log_crud · group_vdbs_tasks",
  "enums/: TaskStatus 0 → 6 · GLLMsTypes · GVDBsTypes      features/: gvdbs_retr_params · gvdbs_retr_filters      sql_db_async · sql_db_sync (session factories) · watchdogs/ · async_log · .env config"], com_w)
com_h = 30 + len(com_lines)*14 + 4
col_bottom = com_y + com_h + PAD
# draw column frames first (prepend) by re-ordering: easiest is to rebuild `out`
body = out[2:]          # svg + defs stay at [0:2]
del out[2:]
for k, (cx, cw, t, s) in COLS.items():
    bottom = col_bottom if k != "spa" else lib_y + lib_h + PAD
    w(f'<rect class="col {k}" x="{cx}" y="{TOP}" width="{cw}" height="{bottom - TOP}" rx="10"/>')
    w(f'<text class="ctitle" x="{cx+12}" y="{TOP+24}">{esc(t)}</text>')
    w(f'<text class="csub" x="{cx+12}" y="{TOP+40}">{esc(s)}</text>')
    w(f'<rect class="pnl lib" x="{cx+PAD}" y="{lib_y}" width="{cw-2*PAD}" height="{lib_h}" rx="6"/>')
    w(f'<text class="ptitle" x="{cx+PAD+10}" y="{lib_y+17}">libraries</text>')
out.extend(body)
panel(com_x, com_y, com_w, com_h, "common/  —  shared package: ORM models, enums, retrieval settings, DB session factories, watchdogs", cls="pnl common")
items(com_x + 10, com_y + 40, com_lines)

# stores row
ST = col_bottom + 165
stores = [
  (30,  300, "PostgreSQL · cwa_db", ["tenants, users, roles · group LLM / VDB / context configs", "doc_tasks: question, context_json, sent_to_llm, answer, status", "log_crud audit · api_processes health"], "dat"),
  (350, 310, "Qdrant", ["one collection per group VDB · dense vectors + payload metadata", "collections today: casambi, furocad", "ChromaDB / pgvector: same vdb_ops interface"], "dat"),
  (690, 190, "HF model cache", ["hf_cache volume", "all-MiniLM-L6-v2", "BAAI/bge-base-en-v1.5"], "vol"),
  (910, 460, "LLM endpoints", ["Ollama local / remote :11434 (OpenAI-compatible /v1)", "OpenAI · Anthropic · Google · Alibaba DashScope", "chosen per task from the group_llms snapshot (gllms_json)"], "ext"),
]
for x, wd, t, ls, cls in stores:
    ls = wrap(ls, wd); ht = 30 + len(ls)*14 + 14
    panel(x, ST, wd, ht, t, cls=f"pnl {cls}")
    items(x + 10, ST + 40, ls)
H = ST + 100
out[0] = out[0].replace(f'viewBox="0 0 {W} 1080"', f'viewBox="0 0 {W} {H}"')

# SPA -> app
ay = TOP + 52 + 40
arrow((COLS["spa"][0] + COLS["spa"][1], ay), (COLS["app"][0], ay), None)
w(f'<text class="elbl" x="{COLS["spa"][0]+COLS["spa"][1]+15}" y="{ay-8}" text-anchor="middle">HTTPS</text>')
w(f'<text class="elbl" x="{COLS["spa"][0]+COLS["spa"][1]+15}" y="{ay+18}" text-anchor="middle">JWT</text>')

# bus below the columns: each edge drops from a column bottom, runs along its own level, drops into a store
B = col_bottom
lv = [B + 22 + i*19 for i in range(7)]
def bus(x0, x1, level, label, dashed=False):
    arrow((x0, B), (x1, ST), label, dashed=dashed, via=[(x0, level), (x1, level)], dy=-4, lpos=0.5)
bus(480,  200, lv[0], "app → Postgres: SQLAlchemy async, asyncpg :5432")
bus(760,  120, lv[1], "rt → Postgres: sync session, poll + write doc_tasks")
bus(840,  520, lv[2], "rt → Qdrant: embed + search, langchain-qdrant :6333")
bus(920,  790, lv[3], "rt → model cache", dashed=True)
bus(1040, 1130, lv[4], "rt → LLM: chat completions, streamed")
bus(1210, 600, lv[5], "ingestion → Qdrant: load, chunk, embed, upsert", dashed=True)
bus(1300, 280, lv[6], "db tools → Postgres: init, migrate, backup / restore", dashed=True)
w('</svg>')
HERE = os.path.dirname(os.path.abspath(__file__))
svg = "\n".join(out)
open(os.path.join(HERE, "component_stack.svg"), "w").write(svg)
page = open(os.path.join(HERE, "page_head.html")).read() + "<figure>\n" + svg + "\n" + open(os.path.join(HERE, "page_tail.html")).read()
open(os.path.join(HERE, "cognosa_component_stack.html"), "w").write(page)
print("wrote component_stack.svg and cognosa_component_stack.html")
