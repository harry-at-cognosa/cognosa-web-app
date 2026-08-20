# FUROCAD: why two Qdrant collections, and options for unified retrieval

*2026-08-19 — companion to `pass1_book_ingest_design.md` (see its §2.4 and §5).*

## Current state

The Papetti SBS book is ingested as **two sibling Qdrant collections**, both embedded with
`BAAI/bge-base-en-v1.5` (768-d, cosine):

| Collection | Points | Content |
|---|---|---|
| `furocad` | 216 | Body-text chunks: section-aware, breadcrumb-prefixed, ≈350-token target. Each carries `footnote_refs` (the note numbers cited in that passage). |
| `furocad_footnotes` | 937 | The book's 884 footnotes (long ones split into parts). Each carries `note_no` and `anchors_chunk_idx` — a link back to the body chunk that cites it. |

Both are exposed to the NAAG group as separate `Document Collection` choices
("FUROCAD — … (text)" and "… (footnotes / citations)").

## Why the split

The footnotes are 1.7× the volume of the body text and are dense with case citations,
study citations, and quoted parentheticals. In a mixed collection they dominated
similarity search — on test queries, footnotes took 4 of the top-5 slots, crowding out the
narrative passages a reader usually wants first. The platform's retrieval filters are
*user-selected per query*; there is currently no way to attach a fixed default filter
(e.g. `kind = body`) to a `group_vdbs` row. Splitting the collections was the
no-platform-change way to get clean body-first retrieval while keeping every citation
searchable.

**Consequence:** a single query today searches one collection or the other. "Try the text
collection first; use the footnotes collection when the question is about authority or
evidence" is the current usage guidance.

## Options for a single query that uses both

In increasing order of ambition:

### 1. Citation expansion (recommended; planned for phase 2)

Retrieve from `furocad` (body) as today, then **deterministically join** in the footnotes
that the retrieved chunks actually cite, via `footnote_refs` → `note_no`. No second vector
search. The LLM sees each passage together with the citations supporting *that passage*.

- Semantically right for this corpus: a footnote earns its place through its anchor's
  relevance, not through its own (citation-string-shaped) embedding.
- Implementation: a small post-retrieval step in the `run_tasks` VDB worker + a per-query
  UI toggle ("include citations"). No re-ingestion; the linking metadata already exists.

### 2. Multi-collection retrieval as a platform feature

Fan a query out to N selected collections and merge results by score. Legitimate here
because both collections share the same embedding model and metric, so scores are
comparable. More general (useful to other tenants) but a larger UI/config surface — and
for FUROCAD specifically it re-introduces the crowding problem the split was made to avoid.

### 3. Re-merge into one collection behind a `default_filter`

If `group_vdbs` gains a `default_filter` (JSON applied to every query against that row),
the two collections can be merged back into one (`kind = body | footnote` payload), with
"body only" as the default row and "with footnotes" as a second row differing only in
filter. Cleanest long-term data model; requires the platform feature first. The loader's
deterministic point IDs make the re-merge a plain re-run of `load`.

## Note for phase 2 (journal articles)

The article corpus needs **none** of the above to be cross-searchable with the book:
articles load into the *same* `furocad` collection with `source_type: "article"`
(vs. `"book"`), so one query already spans book + articles. The split described here is
only body-vs-footnotes, and options 1/3 apply equally to article footnotes if we extract
them.
