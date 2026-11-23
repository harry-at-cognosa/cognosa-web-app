# UI migration plan: v1.1.0 (direction 9b, "Soft gradient, side menu")

Status: draft for Harry's approval, 2026-11-22. No code has been written.

## Scope

Replace the react-bootstrap frontend with the look and layout of prototype 9b
(shadcn/ui + Tailwind v4 + Radix + Lucide). Reference build:
`~/cognosa_web_app_new_UI/prototypes/09b-soft-gradient-sidebar`, live at
https://files.cognosa.net/ui-survey/prototypes/09b-soft-gradient-sidebar/index.html.

Rules, from Harry's rulings:

- Functionality does not change, even where the control that offers it does. Anything
  unclear is asked, not decided.
- The only behaviour changes are those already ruled: collapsible history list (24 % by
  default, same storage key and 18-45 % limits); the question shown as a heading above the
  answer; no cap on the answer column width; side menu with one icon per item, collapsible
  to a 16-icon strip; dark mode as an option in the user menu (light is the default);
  styled dropdowns in place of native `<select>`.
- `webapp_main_color` remains the only colour setting (22 ramps).
- Admin pages are desktop-only. Queries and Chat stay usable on a phone.
- Backend: no change except the version number.

## Method

- Branch `ui-9b` off `main`. Local commits per step; no push until Harry says.
- One cut-over, one release. Bootstrap's stylesheet comes out in batch 0, because it and
  Tailwind cannot share a page (conflicting resets, about ten colliding class names). On
  the branch, pages not yet converted will work but look unstyled until their batch.
- Views change; `api/`, `stores/`, `models/` and behaviour hooks are left alone. Where a
  view cannot be converted without touching one, that is reported.
- Work runs on the Vite dev server (proxying to the backend), so `localhost:8000` keeps
  serving v1.0.1 from `backend/static` until the final build.
- shadcn components are copied from prototype 9b as already restyled (14 of 18 were
  edited for the look). They are our source from then on.

## Batches

Harry reviews at the end, and may review any batch when it is reported done.

| # | Batch | Contents |
|---|---|---|
| 0 | Foundation and shell | Tailwind v4, tokens, fonts, shadcn components; instance colour mapping (`ThemeColor`) and light/dark; side menu with role-gated groups and the 16 icons; user menu; login, Home, Logout, Change Password, Change Group |
| 1 | Queries | History list (resize, collapse, delete), question heading, answer card, found documents, query form, Retrieval Parameters and Retrieval Filters editors with per-control reset, Ask button states |
| 2 | Chat | Conversation list, header with fixed collection and filter chips, message stream, composer, download, Open in Queries |
| 3 | Table pattern and CRUD pages | `tables/` (sort, filter row, paging, column resize, export, cell and edit renderers), then every page built on it: GroupAdmin Users, Queries, Retrieval Parameters, Doc Collections; SuperUser Groups, Users, LLMs, VDBs, Doc Tasks, Api Settings, Log CRUD |
| 4 | Remaining pages | Manage Contexts, Server Status |
| 5 | Removal and release | Uninstall bootstrap, react-bootstrap, both icon packages, popper, react-router-bootstrap; confirm no residue; version 1.1.0; CHANGELOG; production build into `backend/static` |

Pages the prototype did not draw (login, Change Password, Change Group, Manage Contexts,
Doc Tasks, edit forms other than VDB) follow 9b's existing components; each is shown to
Harry in its batch report with a screenshot.

## Verification

The frontend has no tests. Each batch is checked by:

1. `tsc -b`, `eslint`, `vite build` clean.
2. A Playwright script against the local stack (real backend, real LLM calls) that
   exercises the batch's controls, at 1440 px, and at phone width for Queries and Chat.
3. Light and dark, and at least three instance colours including a pale ramp.

End to end, using `p06_lbprods_demo/tools/capture.py` as Harry suggested:

- Before batch 0: run it with `--skip-live` against v1.0.1 as the baseline record.
- Its selectors are tied to Bootstrap (`.modal.show`, `select.form-select`,
  `.input-group`, `button.w-100.btn-outline-secondary`), so it cannot run unchanged on the
  new UI. After batch 4 it is ported to role- and label-based selectors, in that project,
  and run in full. The ported script is then what the demo re-creation uses; Chat steps
  are added to it there.
- The full run deletes user `als_user`'s queries and creates a new one, as it does today.

## Known risks (from the prototype's ISSUES.md)

1. No data grid in shadcn: the table pattern is our own component. Largest single piece.
2. Radix Select differs from `<select>`: no empty value, string values only, no native
   phone picker. Every form select in the CRUD pages is affected.
3. Nine of the 22 ramps fail contrast with white text at shade 600; the mapping uses
   700/800 in light and 300/400 with dark text in dark. Solved in the prototype.
4. Tailwind v4's CSS minifier dropped the unprefixed `backdrop-filter`; the fix is known.
5. The Group VDBs table has 1150 px with the menu open at 1440 px; wide tables rely on
   collapsing the menu or on horizontal scroll.

## Open

- The menu and the history list use different collapse icons; settle in batch 1.
