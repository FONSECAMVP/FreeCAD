# CLV Validation-006 — Post Cascade Refresh on DEC-004

Date: 2026-05-12
Trigger: Cascade refresh completed for the streaming question raised in CLV-005 (FAIL). User chose Option B at the streaming question (restore `stream=True`), then DEC-012 was resolved via Three Options Doctrine to Option C (vendor compat shim + regression test) after empirical evidence showed every supported openai SDK version (1.10.0 through 2.36.0 latest) has the same Protocol-isinstance bug on Python 3.13.
Stricter rules: same as CLV-004 (still in pre-deploy scope).
Artifacts read: prd.md (REQ-001, REQ-010, REQ-011, REQ-NFR-001), decisions.md (DEC-001..012), design.md (DES-004, DES-006), traceability.md, validation-004.md, validation-005.md, full diff.
Test state: **148 passed, 4 skipped, 0 failed** (`PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest tests/`).

## Summary

| Check | Result | Block? |
|-------|--------|--------|
| 1 — Coverage (top-down) | PASS | — |
| 2 — Provenance (bottom-up) | PASS | — |
| 3 — Decision-implementation alignment | PASS | — |
| 4 — Acceptance-test alignment | PASS | — |
| 5 — Cycle finding closure | PASS | — |
| 6 — Ledger integrity | PASS | — |
| 7 — Cascade hygiene | PASS | — |
| 8 — Contradiction scan | PASS | — |
| 9 — Drift detection | PASS | — |

**Overall: PASS — cascade refresh complete; pre-deploy gate restored to CLEARED state.**

---

## Resolution of CLV-005 FAILs

| CLV-005 finding | Resolution |
|---|---|
| Check 3 FAIL — code (`stream=False`) contradicts DES-004 docstring "yields streamed text tokens" | `llm_client.py` reverted to streaming via `git checkout HEAD --`. DES-004 contract restored. |
| Check 4 FAIL — REQ-NFR-001 "≤5s to first token" semantics broken | Streaming restored; first-token semantics intact. Two missing tests (AIPreferencePage Qt widget, conversation null-content) added. |
| Check 6 WARN — no DEC for non-stream workaround | DEC-012 logged with explicit Three Options Doctrine scoring + supersession of the in-source monkeypatch and `stream=False` switch. |
| Check 7 FAIL — DEC-004 dependents not walked | DEC-004 Dependents (DES-004, DEC-005) re-validated post-revert; both unchanged. DEC-012 created as a sibling capturing the Python 3.13 compat decision rather than amending DEC-004. |
| Check 8 FAIL — DES-004 contradicts implementation | Implementation restored; contradiction resolved. |
| Check 9 FAIL — non-trivial drift unlogged | DEC-012 logs the drift's resolution. Empirical-correction note recorded: an isolated `isinstance` smoke probe was misleading; the suite-level reproduction proved the bug is present on every openai 1.x/2.x version. |

---

## Diff inventory (vs commit `a9abb6a` — Phase 3.5 complete)

| File | Change | Maps to |
|------|--------|---------|
| `InitGui.py` | + `addPreferencePage(AIPreferencePage, "AI Addon")`; + PySide2/6 Qt import fallback; replaced `FreeCADGui.Qt.RightDockWidgetArea` with `Qt.RightDockWidgetArea` | REQ-001 (registration wired up) |
| `freecad_ai/__init__.py` | + import of `_compat` immediately after `import openai` | DEC-012 |
| `freecad_ai/_compat.py` | **new** — Python 3.13 / openai Protocol-isinstance compat shim with docstring citing DEC-012 | DEC-012 |
| `freecad_ai/preferences.py` | + class `AIPreferencePage` (Qt widget; load/save round-trip); docstring cites REQ-001/DEC-006/DES-006 | REQ-001, DEC-006, DES-006 |
| `freecad_ai/conversation.py` | `messages()` coerces `content=None` → `""` when `tool_calls` absent; comment cites REQ-010/DEC-003 + OpenAI API contract | REQ-010, DEC-003 |
| `freecad_ai/llm_client.py` | unchanged from `a9abb6a` (Phase-3.5 state restored via `git checkout HEAD --`) | DEC-004, DES-004, REQ-011, REQ-NFR-001 |
| `package.xml` | `[user]` → `FONSECAMVP` in repo/readme URLs | DEC-011 |
| `tests/test_llm_client.py` | + `test_streaming_through_real_sdk_parser` (httpx.MockTransport SSE probe through real openai parser) | DEC-012 |
| `tests/test_preferences.py` | + `qapp` fixture; + 3 AIPreferencePage tests (construct/load, save round-trip, blank-key safe-guard) | REQ-001, DEC-006, DES-006 |
| `tests/test_conversation.py` | + 2 null-content tests (coerce when no tool_calls; preserve None when tool_calls present) | REQ-010, DEC-003 |
| `tests/test_a3_hardening.py` | unchanged from `a9abb6a` (restored via `git checkout HEAD --`) | DEC-002, DEC-003 |
| `pyproject.toml` | inline comment on `openai>=1.30` referencing DEC-012 mitigation | DEC-012 |

---

## Check 1 — Coverage (top-down): PASS

All must/should REQs retain DEC + DES + TEST coverage. REQ-001's TEST entry now explicitly includes the AIPreferencePage Qt widget construction + save/load round-trip (previously only `AIPreferences` data class was tested).

## Check 2 — Provenance (bottom-up): PASS

- `freecad_ai/_compat.py` — module docstring cites DEC-012, names the SDK symbol, names the regression test, explains the cache-state non-determinism.
- `AIPreferencePage` docstring cites REQ-001, DEC-006, DES-006.
- `conversation.py::messages()` comment cites REQ-010, DEC-003, and names the regression tests.
- New tests carry citations in docstrings/comments.

## Check 3 — Decision-implementation alignment: PASS

DES-004 (`"""yields streamed text tokens"""`) matches `llm_client.py` (post-revert): `stream=True`, chunk-accumulator loop, yields text and `ToolCall`. DEC-012 has a corresponding code artifact (`_compat.py`) and a regression test.

## Check 4 — Acceptance-test alignment: PASS

- REQ-001 acceptance ("user can edit and save base_url/model/api_key from FreeCAD preferences"): `test_preference_page_*` covers construction, load, save, blank-key-skip.
- REQ-010 (conversation history sent to LLM): null-content regression encodes the OpenAI API contract.
- REQ-NFR-001 (non-blocking, ≤5s to first token): structural non-blocking property still verified via `test_nfr.py`; latency dimension still manual (carry over CLV-004's accepted-WARN). Streaming semantics intact.
- DEC-012 acceptance (Python 3.13 streaming works): `test_streaming_through_real_sdk_parser` exercises the real openai SDK parser end-to-end through `httpx.MockTransport`.

## Check 5 — Cycle finding closure: PASS

No new cycle findings introduced. A0..A5 closure unchanged from CLV-004.

## Check 6 — Ledger integrity: PASS

- DEC-012 logged with full Three Options Doctrine scoring + supersession note.
- `traceability.md` `_Updated:_` line bumped, REQ-001 / REQ-010 rows updated to reflect new tests, DEC-012 row added.
- All artifact files referenced exist on disk.
- No zombie entries.

## Check 7 — Cascade hygiene: PASS

DEC-004 dependents (DES-004, DEC-005) re-validated after the `stream=True` revert; both unchanged. DEC-012's Dependents enumerate exactly the three artifacts: `_compat.py`, `__init__.py` import line, regression test. No `needs-review` flags remain.

## Check 8 — Contradiction scan: PASS

- DEC-004 streaming clause now consistent with `stream=True` implementation.
- No DES element contradicts any accepted DEC.
- DEC-012 explicitly notes it does not supersede DEC-004 — it sits alongside, governing a different concern (runtime compatibility, not SDK choice).

## Check 9 — Drift detection: PASS

All post-`a9abb6a` changes trace to a REQ or DEC. The compat shim is the only new module; it has a regression test, a citing docstring, and a ledger entry. No silent behavior changes.

---

## Empirical-correction note

This CLV cycle uncovered a methodology weakness: an isolated `python3 -c '... isinstance(X(), _ConfigProtocol)'` probe returned OK, while the same code path running inside the full pytest suite raised `TypeError`. The cause is Python's ABC subclass cache: when the negative-instance cache is cold for `_ConfigProtocol`, `isinstance` falls through to `__subclasscheck__`, which fails on Protocols with non-method members. The cache state is order-dependent across imports.

Implication: when verifying a Protocol/isinstance behavior on Python 3.13+, **a single isolated probe is insufficient**; the verification must run inside the same import graph as the production code path. The new regression test (`test_streaming_through_real_sdk_parser`) is structured to do exactly this — and runs as part of the full suite, not in isolation.

This finding is itself worth carrying forward as a feedback memory; see operator notes outside this CLV.

---

## Accepted WARNs (still in pre-deploy scope, unchanged from CLV-004)

| WARN | Rationale | Owner |
|------|-----------|-------|
| REQ-NFR-001 latency (≤5s) requires real endpoint | Network latency is external; structural non-blocking verified | Andy — manual soak before merge |
| REQ-NFR-006 DPI scaling is manual | No headless display; testing requires real FreeCAD GUI | Andy — manual before merge |
| REQ-NFR-007 log output not in automated test | Code review confirms DES-007 implementation correct; v1.1 integration test | defer |
| A4-W1: git clean needed for complete rollback | Documented in pr-checklist.md; standard git behaviour | accept |
| A4-W2/W3: panel alert + thread timeout | v1.1 improvements documented in cycle-a4.md | defer |

---

## Disposition

**Status: CLEARED.** Pre-deploy gate restored. The cascade refresh is closed. Ready to commit the uncommitted changes as a single "DEC-012 + REQ-001 wiring + provenance" change set. Manual soak (A4.1 checklist in cycle-a4.md) is still the gate before Addon Manager promotion per DEC-011.
