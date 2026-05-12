# CLV Validation-005 — Mid-Project Drift Scan

Date: 2026-05-12
Trigger: `/quality-gated-dev-workflow` invoked mid-project. CLV-004 PASS at commit `a9abb6a` (Phase 3.5 complete). 7 files modified after that commit, uncommitted. Skill requires CLV before resuming work.
Stricter rules: same as CLV-004 (pre-deploy gate still in scope — uncommitted changes are on the deploy candidate branch `feat/ai-addon`).
Artifacts read: prd.md (REQ-001, REQ-010, REQ-011, REQ-NFR-001, REQ-NFR-003), decisions.md (DEC-001..011), design.md (DES-004, DES-006), traceability.md, validation-004.md, full uncommitted diff.

## Summary

| Check | Result | Block? |
|-------|--------|--------|
| 1 — Coverage (top-down) | PASS | — |
| 2 — Provenance (bottom-up) | WARN | warn |
| 3 — Decision-implementation alignment | **FAIL** | **block** |
| 4 — Acceptance-test alignment | **FAIL** | **block** |
| 5 — Cycle finding closure | PASS | — |
| 6 — Ledger integrity | WARN | warn |
| 7 — Cascade hygiene | **FAIL** | **block** |
| 8 — Contradiction scan | **FAIL** | **block** |
| 9 — Drift detection | **FAIL** | **block** |

**Overall: FAIL — must not deploy or merge until cascade refresh complete.**

Tests on disk: 143 passed, 4 skipped (PYTHONPATH=. pytest tests/). Suite green but does not exercise the new behavior of the changed contract (see Check 3).

---

## Diff inventory

| File | Change | Maps to |
|------|--------|---------|
| `InitGui.py` | + `addPreferencePage(AIPreferencePage, "AI Addon")`; + Qt import fallback for PySide2/6; replaced `FreeCADGui.Qt.RightDockWidgetArea` with `Qt.RightDockWidgetArea` | REQ-001 (registration finally wired up), REQ-NFR-006 (Qt6 compat — not in PRD as REQ) |
| `freecad_ai/preferences.py` | + class `AIPreferencePage` (Qt widget; `__new__` factory; load/saveSettings) | REQ-001, DEC-006, DES-006 |
| `freecad_ai/conversation.py` | `messages()` now coerces `content=None` → `""` unless `tool_calls` present | DEC-003, REQ-010 (bug fix; no REQ encoded this) |
| `freecad_ai/llm_client.py` | (a) Python 3.13 monkeypatch of `openai._models._ConfigProtocol`; (b) **`stream=True` → `stream=False`**; removed chunk-accumulator logic | DEC-004, DES-004, REQ-011, REQ-NFR-001 |
| `package.xml` | `[user]` → `FONSECAMVP` in repo/readme URLs | DEC-011 (dependent) |
| `tests/test_a3_hardening.py` | Rewrote 2 LLM-client tests for non-stream mock | DEC-004 |
| `tests/test_llm_client.py` | Full rewrite of stream-mock helpers → non-stream MagicMock | DEC-004 |

---

## Check 1 — Coverage (top-down): PASS

Every must/should REQ still has ≥1 DEC, ≥1 DES, ≥1 TEST. New widget code (AIPreferencePage) attaches to existing REQ-001/DEC-006/DES-006/test_preferences.py spine. Note caveat: TEST for REQ-001 only covers data class `AIPreferences`; the new `AIPreferencePage` Qt widget has no direct test (see Check 4).

---

## Check 2 — Provenance (bottom-up): WARN

- `AIPreferencePage` (new class) has no docstring citing REQ-001. Trivial fix.
- `conversation.py` null-content coercion has no docstring/comment citing REQ-010 or a bug ID. Reader cannot trace *why* the special case exists from source alone.
- `llm_client.py` 3.13 monkeypatch has a long comment but cites no DEC/REQ — should reference DEC-004 (or its supersession) so future readers find the cascade record.

---

## Check 3 — Decision-implementation alignment: **FAIL**

**DES-004 source (`design.md:115-121`):**

```python
async def chat(...) -> AsyncIterator[str | ToolCall]:
    """Yields streamed text tokens and ToolCall objects."""
```

**Current `llm_client.py`:** `stream=False`. The function still yields, but it yields **at most one** full content string after the entire response arrives, then iterates completed tool calls. Streaming token-by-token delivery is gone.

This is a contract change, not a refactor. The DES-004 spec block in `design.md` is now a lie. Block-level FAIL.

---

## Check 4 — Acceptance-test alignment: **FAIL**

**REQ-NFR-001 (prd.md:54):** "Chat panel submit → first response token ≤ 5s on a 100Mbps connection (network-bound, not app-bound). **Criterion:** measure with local Ollama model on same machine; must be non-blocking."

Under `stream=False`, "first response token" is identical to "complete response" — there are no intermediate tokens. The acceptance criterion's semantics change: ≤5s to *first token* effectively becomes ≤5s to *full response*, which is far stricter for any non-trivial response. The structural non-blocking property (CLV-004 accepted-WARN) still holds via QThread, but the latency dimension of REQ-NFR-001 is materially different.

Additionally:
- `AIPreferencePage` widget: no test. REQ-001 acceptance criterion ("user can edit and save base_url/model/api_key") needs at least a smoke construction test (pytest-qt can do this).
- `conversation.py` null-content coercion: no test. Edge case ("assistant message with no content and no tool_calls is sent as empty string") is unverified.

Block-level FAIL on the REQ-NFR-001 semantic drift; the two missing tests are individually WARN-level but stack onto Check 4.

---

## Check 5 — Cycle finding closure: PASS

No new cycle findings introduced by the diff. A0..A5 closure unchanged from CLV-004.

---

## Check 6 — Ledger integrity: WARN

- `decisions.md` has no DEC for the streaming-disabled decision. A workaround that defeats DES-004 needs either: (a) a new DEC superseding DEC-004's streaming clause, or (b) DEC-004 amended with status `needs-review` and an Addendum.
- `traceability.md` Updated line still reads "Phase 3.5. 142 tests passing." Now 143 pass; no row added for the new AIPreferencePage code path or the conversation null-content fix.
- `decisions.md` Dependents on DEC-001 list "DEC-008 (testing toolchain)" but DEC-008's listed Dependents are file paths, not DECs — no graph break but inconsistent format. Pre-existing, not caused by this diff. Note only.

---

## Check 7 — Cascade hygiene: **FAIL**

DEC-004 chosen option ("openai SDK with built-in **streaming**, retry, error handling") is now materially weakened. Per skill rule 4 (Cascade refresh on change):

> When a DEC's chosen option changes (or its status flips to `needs-review`), walk its Dependents list forward and mark each dependent as `needs-review`.

DEC-004's Dependents: DES-004, DEC-005. Both must be marked `needs-review` and re-validated. None are marked. FAIL.

---

## Check 8 — Contradiction scan: **FAIL**

- DES-004 docstring `"""Yields streamed text tokens"""` contradicts `stream=False` implementation.
- Comment in `llm_client.py:56-57` says "Re-enable streaming when SDK is fixed" — implicitly admits the decision is provisional, but no DEC captures that provisional state.

---

## Check 9 — Drift detection: **FAIL**

Two high-impact one-way-or-medium-door changes since CLV-004:

1. `stream=True → stream=False` — affects DEC-004, DES-004, REQ-NFR-001 latency dimension. **Cascade refresh required.**
2. Python 3.13 monkeypatch of `openai._models._ConfigProtocol` — global module mutation at import time. Affects all callers of openai SDK in the process. No DEC, no DES note, no test that verifies the patch holds across SDK upgrades.

The preferences-page wiring (`AIPreferencePage`) is medium-impact but cleanly attached to REQ-001/DEC-006/DES-006 — not drift in the destructive sense, but missing a test and a ledger note.

---

## Required actions to clear FAIL (before any merge or deploy)

The skill mandates the Three Options Doctrine on every decision-in-motion. The user must pick one of these on the streaming question before this CLV can re-run clean:

- **Option A — Accept stream=False as the new normal.** Supersede the streaming clause of DEC-004 with a new DEC (e.g. DEC-012 "Streaming disabled until openai SDK + Python 3.13 fix"). Update DES-004 docstring + design.md. Renegotiate REQ-NFR-001 acceptance criterion to "≤5s to *complete response*" or split into two metrics. Add a test that documents the non-stream contract.
- **Option B — Restore stream=True; fix the 3.13 isinstance bug differently.** Pin openai SDK to a known-good version, OR vendor a forked `_models.py`, OR drop Python 3.13 from supported versions in `pyproject.toml`. Revert llm_client.py to streaming code; revert test rewrites.
- **Option C — Defer with a kill-switch.** Keep `stream=False` as a feature-flagged degraded mode. Add `AIPreferences.streaming_enabled` (default False on Python 3.13, True elsewhere). DEC-012 captures the version-gated decision. DES-004 and tests cover both code paths.

Plus, regardless of A/B/C:

1. Add a test for `AIPreferencePage` construction + load/saveSettings round-trip (pytest-qt).
2. Add a test for the `conversation.py` null-content → empty-string coercion (encode it as a regression test for the OpenAI API contract).
3. Update `traceability.md` "Updated" line and row counts.
4. Add provenance comments/docstrings noted in Check 2.

After A/B/C selected and dependents refreshed, re-run CLV. Target: validation-006.md PASS before merge/deploy.

---

## Disposition

**Status: BLOCKING.** Do not merge `feat/ai-addon` to `main`, do not promote to Addon Manager release, do not amend CLV-004 to PASS until a cascade refresh on DEC-004 completes and a new CLV produces overall PASS.
