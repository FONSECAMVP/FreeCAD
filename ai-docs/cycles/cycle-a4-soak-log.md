# A4.1 Manual Soak Log

Trigger: Phase 3.5 exit gate before Addon Manager promotion per DEC-011.
Source-tree commit: `8295cc2b8e` (CLV-006 PASS).
Addon location: `~/.local/share/FreeCAD/Mod/AIAddon` → symlink → repo `src/Mod/AIAddon/`.
FreeCAD binary: `/usr/bin/freecad`.

Per cycle-a4.md:30 — six required checks.

---

## Pre-flight

| Item | State |
|------|-------|
| Symlink resolved → repo | ✓ |
| `_compat.py` matches repo (DEC-012 shim active) | ✓ |
| 6 workbench plugin modules present (part, partdesign, sketcher, draft, bim, inspection) | ✓ |
| LLM endpoint configured (base_url / model / api_key) | _to be set by user via Edit > Preferences > AI Addon before run_ |

---

## Soak run

Date: _fill in_
LLM endpoint used (Ollama local / OpenAI / Anthropic compat / other): _fill in_
Model: _fill in_

### S1 — Tools registered on startup
Expected: Report View shows `[AI Addon] N tools registered.` where N > 0.
Result: _fill in_  (PASS / FAIL — paste exact Report View line if FAIL)

### S2 — 5 requests covering Part, PartDesign, Sketcher
Suggested prompts (vary to taste):
1. "Make a 50x50x20 box."
2. "Make a 30mm cylinder, 60mm tall."
3. "Create a new PartDesign body and add a 40mm sketch-based pad."
4. "Start a sketch on XY and draw a 25mm radius circle."
5. "List all objects in the current document."

Per-prompt result:

| # | Prompt | Tool(s) called | Visible result | PASS/FAIL |
|---|--------|----------------|----------------|-----------|
| 1 |        |                |                |           |
| 2 |        |                |                |           |
| 3 |        |                |                |           |
| 4 |        |                |                |           |
| 5 |        |                |                |           |

### S3 — Undo stack
For each successful op above, press Ctrl+Z once. Verify the operation reverses.
Result: _PASS / FAIL — note any op that did not undo cleanly_

### S4 — Report View log entries
Verify Report View shows a log line per tool call: tool name, status, duration.
Sample line (paste one):
```
_fill in_
```
Result: _PASS / FAIL_

### S5 — Panel responsive during LLM call
While a long prompt is in flight, try: resize the chat panel, switch FreeCAD workbench, drag the 3D view. UI must not freeze.
Result: _PASS / FAIL — describe any freeze_

### S6 — 30-minute soak (memory growth)
Pre-run RSS:  `_fill in_ MB`  (`ps -o rss= -p $(pgrep -f freecad)` in bytes/1024)
Post-30-min RSS: `_fill in_ MB`
Delta: `_fill in_ MB`
Periodic requests during the window (≥10 total): _fill in count_
Result: _PASS / FAIL — flag if delta > 100 MB without an obvious cause_

---

## Bonus checks (carry over accepted-WARN from CLV-006)

### REQ-NFR-001 — first-token latency ≤ 5s on a local endpoint
Measure on local Ollama (same machine), simplest text prompt. Three trials:
1. _fill in_ s
2. _fill in_ s
3. _fill in_ s
Median: _fill in_ s
Result: _PASS / FAIL_

### REQ-NFR-006 — DPI scaling
Check panel + preferences page on the current display. Text + icons crisp, no clipping.
Result: _PASS / FAIL — note display DPI if known_

---

## Disposition

- [ ] S1–S6 all PASS → A4.1 cleared → Phase 3.5 exit fully met → ready for DEC-011 deploy (external repo + Addon Manager submission)
- [ ] Any FAIL → log issue inline above; if FAIL is REQ-or-DEC-rooted, cascade refresh required; otherwise file as v0.1.1 bug

Closed by: _name + date_
