#!/usr/bin/env python3
"""
Generate the Cognosa query sequence diagram (flat inline SVG, swimlane style).

Usage:  python3 gen_query_sequence.py
Writes, next to this script:
  query_sequence.svg            the bare drawing
  cognosa_query_sequence.html   page_head.html + <figure> + svg + page_tail.html

Model: eight lifelines (SPA, app, Postgres doc_tasks, rt main loop, VDB worker,
Qdrant, LLM worker, LLM). Each numbered step is one message between lanes or a
local action on one lane. Pills on the Postgres lane show the doc_tasks.status
value written at that step (common/enums/doc_task_status.py). Sources:
tasks_lib/main_iteration.py, qd_lib/*, vdb_lib/workers.py, llm_lib/workers.py,
llm_lib/llm_type_openai.py, cwa_lib/routers/doc_tasks.py,
frontend/src/pages/QueryDocuments/stores/useQueryDocumentStore.ts.
"""
import os
out = []
def w(s): out.append(s)
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

LANES = [
  ("spa",  "React SPA",         "QueryDocuments page",            "spa"),
  ("app",  "app · FastAPI",     "routers/doc_tasks.py",           "app"),
  ("pg",   "PostgreSQL",        "doc_tasks row",                  "dat"),
  ("rt",   "rt · main loop",    "main_iteration.py · qd_lib/",    "rt"),
  ("vdb",  "VDB worker",        "vdb_lib · process",              "rt"),
  ("qd",   "Qdrant",            "group VDB collection",           "dat"),
  ("llm",  "LLM worker",        "llm_lib · thread",               "rt"),
  ("api",  "LLM",               "Ollama · cloud chat APIs", "ext"),
]
X0, GAP = 100, 178
LX = {k: X0 + i*GAP for i, (k, *_r) in enumerate(LANES)}
TOP, ROW = 150, 54
W = X0 + (len(LANES)-1)*GAP + 100

steps = []   # (kind, a, b, lines, status)
def msg(a, b, lines, status=None, dashed=False): steps.append(("msg", a, b, lines, status, dashed))
def act(a, lines, status=None):               steps.append(("act", a, None, lines, status, False))

msg("spa", "app", ["POST /api/v1/doc_tasks  (JWT)", "input_text, gvdbs_id, gllms_id, gc_id"])
msg("app", "pg",  ["INSERT doc_tasks: snapshot group_vdbs,", "group_llms rows → gvdbs_json, gllms_json"], status="0 QD_INIT")
msg("app", "spa", ["201 → doc_task uuid"], dashed=True)
msg("spa", "app", ["poll GET /doc_tasks/{uuid} on a timeout loop", "→ status, status_text, pct, answer so far", "until status in FINISHED_LIST"], dashed=True)
msg("rt",  "pg",  ["SELECT … WHERE status IN (0, 3)", "ORDER BY doc_task_id LIMIT 1", "FOR UPDATE SKIP LOCKED"])
act("rt", ["qd_init: validate gvdbs_json (url,", "collection, emb model, retr filters)"], status="1 QD_INIT_FETCHED")
msg("rt",  "vdb", ["Queue.put(VDBDocTaskQueueMsg)", "multiprocessing queue"], status="2 QD_VDB_PENDING")
act("vdb", ["embed question: HuggingFaceEmbeddings", "(gvdbs_emb_model, preloaded)"])
msg("vdb", "qd",  ["as_retriever(search_type, k …)", "+ payload filter from retr_filters"])
msg("qd",  "vdb", ["top-k chunks + metadata"], dashed=True)
msg("vdb", "pg",  ["UPDATE context_json (found docs,", "deduped), vdb_query_seconds"], status="3 QD_VDB_FETCHED")
msg("rt",  "pg",  ["next poll picks status 3 →", "qd_vdb_fetched"], status="4 QD_LLM_PENDING")
msg("rt",  "llm", ["start LLMWorker(Thread)(doc_task_id)"])
msg("llm", "pg",  ["read task, gllms_json,", "group_contexts template"])
act("llm", ["prepare_context: \"Document i: …\"", "chain = {context, question} | prompt", "        | ChatModel | StrOutputParser"])
msg("llm", "api", ["chain.stream(question)", "ChatOpenAI · ChatAnthropic ·", "ChatGoogleGenerativeAI"])
msg("api", "llm", ["token chunks, streamed"], dashed=True)
msg("llm", "pg",  ["write sent_to_llm; append answer", "per chunk"], status="5 QD_LLM_WRITING")
msg("llm", "pg",  ["final answer, llm_query_seconds"], status="6 QD_LLM_FETCHED")
msg("app", "spa", ["poll returns status 6: answer (markdown)", "+ sources from context_json; stop polling"], dashed=True)

H = TOP + len(steps)*ROW + 120
w(f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cognosa query sequence: a user question travels from the React SPA through the FastAPI app into Postgres, is picked up by the rt main loop, embedded and searched in Qdrant by a VDB worker, answered by a streaming LLM worker, and polled back to the SPA" xmlns="http://www.w3.org/2000/svg">')
w('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>')

# lifelines + headers
BOT = TOP + len(steps)*ROW + 20
for k, t, s, cls in LANES:
    x = LX[k]
    w(f'<line class="life" x1="{x}" y1="{98}" x2="{x}" y2="{BOT}"/>')
    w(f'<rect class="lane {cls}" x="{x-82}" y="40" width="164" height="56" rx="7"/>')
    w(f'<text class="ltitle" x="{x}" y="{62}" text-anchor="middle">{esc(t)}</text>')
    w(f'<text class="lsub" x="{x}" y="{78}" text-anchor="middle">{esc(s)}</text>')
# phase bands behind rows
phases = [(0, 4, "submit + poll"), (4, 11, "retrieval"), (11, 19, "generation"), (19, 20, "deliver")]
for pi, (a, b, name) in enumerate(phases):
    y0, y1 = TOP + a*ROW - 18, TOP + b*ROW - 18
    w(f'<rect class="phase {"alt" if pi % 2 else ""}" x="20" y="{y0}" width="{W-40}" height="{y1-y0}"/>')
    w(f'<text class="phasename" x="{W-28}" y="{y0+14}" text-anchor="end">{esc(name)}</text>')

# steps
for i, (kind, a, b, lines, status, dashed) in enumerate(steps):
    y = TOP + i*ROW
    xa = LX[a]
    d = ' stroke-dasharray="6 4"' if dashed else ''
    if kind == "msg":
        xb = LX[b]
        w(f'<line class="msg" x1="{xa}" y1="{y}" x2="{xb}" y2="{y}" marker-end="url(#arrow)"{d}/>')
        mid = (xa + xb) / 2
    else:
        # self action: small loop beside the lane (to the left on the right-hand lanes)
        left = LANES.index(next(l for l in LANES if l[0] == a)) >= 5
        if left:
            w(f'<path class="msg" d="M{xa},{y-8} h-26 v16 h20" marker-end="url(#arrow)"/>')
            mid = xa - 30
        else:
            w(f'<path class="msg" d="M{xa},{y-8} h26 v16 h-20" marker-end="url(#arrow)"/>')
            mid = xa + 30
    # label: above the line, up to 3 lines, bottom line sits 6px above the arrow
    n = len(lines)
    for j, ln in enumerate(lines):
        cls = "mlbl" if kind == "msg" else "mlbl act"
        anchor = "middle" if kind == "msg" else ("end" if mid < xa else "start")
        lx = mid if kind == "msg" else (mid - 4 if mid < xa else mid + 4)
        w(f'<text class="{cls}" x="{lx:.1f}" y="{y - 7 - (n-1-j)*12:.1f}" text-anchor="{anchor}">{esc(ln)}</text>')
    # number badge at the source
    bx = xa + (12 if (kind == "msg" and LX[b] > xa) or (kind == "act" and mid > xa) else -12)
    w(f'<circle class="badge" cx="{bx}" cy="{y}" r="9"/>')
    w(f'<text class="badgetext" x="{bx}" y="{y+3.5}" text-anchor="middle">{i+1}</text>')
    # status pill on the Postgres lane
    if status:
        px = LX["pg"]
        pw = 7.0*len(status) + 16
        w(f'<rect class="pill" x="{px-pw/2:.1f}" y="{y+6}" width="{pw:.0f}" height="16" rx="8"/>')
        w(f'<text class="pilltext" x="{px}" y="{y+17.5}" text-anchor="middle">{esc(status)}</text>')

# notes
ny = BOT + 14
w(f'<text class="note" x="{X0-80}" y="{ny}">Errors: each stage writes its own negative status and a status_text: -1 QD_INIT_ERROR, -3 QD_VDB_ERROR, -6 QD_LLM_ERROR. The SPA stops polling on any of them.</text>')
w(f'<text class="note" x="{X0-80}" y="{ny+16}">No-retrieval mode: a task with gvdbs_id = -1 skips steps 6 to 11; the main loop moves it from status 0 straight to 3 and it goes to the LLM with an empty context.</text>')
w(f'<text class="note" x="{X0-80}" y="{ny+32}">Concurrency: FOR UPDATE SKIP LOCKED lets several rt instances share one doc_tasks table; VDB workers are RT_VDB_PROCESS_NUM processes; each task gets its own LLM thread.</text>')
w('</svg>')

HERE = os.path.dirname(os.path.abspath(__file__))
svg = "\n".join(out)
open(os.path.join(HERE, "query_sequence.svg"), "w").write(svg)
page = open(os.path.join(HERE, "page_head.html")).read() + "<figure>\n" + svg + "\n" + open(os.path.join(HERE, "page_tail.html")).read()
open(os.path.join(HERE, "cognosa_query_sequence.html"), "w").write(page)
print("wrote query_sequence.svg and cognosa_query_sequence.html")
