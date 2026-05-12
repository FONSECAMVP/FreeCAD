# Adversarial Cycle A4 — Pre-Production Hardening

Date: 2026-05-12
Phase: 3 pre-promotion
Output: this file + executor.py fix (A4-BLOCK-1) + test_executor.py regression test

---

## A4.1 Staging Soak

**Context:** FreeCAD cannot run headlessly — no GUI available in this environment. The soak
is performed as a code-path analysis against the test suite + code review, supplemented by
notes for manual validation with a real FreeCAD instance.

**Automated coverage standing (142 tests, 73% source coverage):**
- All executor paths: 97% covered
- Conversation/context/registry: 92–97% covered
- panel.py: 0% (Qt display required — accepted, documented in CLV-003)
- worker.py: 56% (asyncio + Qt paths require real event loop)

**Findings from load analysis:**

| # | Observation | Severity | Disposition |
|---|-------------|----------|-------------|
| S1 | `FreeCADGui.activateWorkbench()` is synchronous in FreeCAD's Python API — no race between activation and handler call | PASS | n/a |
| S2 | `FreeCADGui.Qt.RightDockWidgetArea` attribute path may vary by FreeCAD version; panel init is wrapped in `try/except` → degrades gracefully with warning | WARN | accept-with-rationale: v0.1; fix in next iteration when version matrix is known |
| S3 | Conversation history grows until `max_tokens` truncation; 8000-token default ≈ 32KB text — negligible for session scope | PASS | n/a |
| S4 | Staging soak with real FreeCAD + LLM endpoint is manual-only; cannot automate without FreeCAD runtime | DEFER | accept-with-rationale: document required manual soak below |

**Required manual soak (before merge to main):**
1. Launch FreeCAD with addon loaded; verify `[AI Addon] N tools registered.` in Report View
2. Create a new document; send 5 requests covering Part, PartDesign, Sketcher tools
3. Verify each operation appears on undo stack (Ctrl+Z removes it)
4. Verify Report View shows tool-call log entries (name, status, duration)
5. Verify chat panel remains responsive during LLM call (Qt event loop not blocked)
6. Run for 30 minutes with periodic requests; verify no memory growth in FreeCAD process

---

## A4.2 Rollback Drill

**Rollback performed:** switched to `main` branch, verified addon state, returned to `feat/ai-addon`.

**Result: PARTIAL PASS — one WARN.**

| Check | Result |
|-------|--------|
| `git checkout main` removes Init.py, InitGui.py, freecad_ai/*.py | PASS |
| `git checkout main` removes tests/ Python source files | PASS |
| Addon directories (`src/Mod/AIAddon/freecad_ai/`, `tests/`) persist on `main` | WARN — `__pycache__/` and `.venv/` are untracked; git leaves non-empty dirs |
| FreeCAD would not load addon after rollback (no Init.py on `main`) | PASS |
| Re-applying branch (`git checkout feat/ai-addon`) restores full state | PASS |

**Rollback timing:** `git checkout main` completes in < 1s on local ext-drive repo.

**WARN — A4-W1:** After `git checkout main`, `src/Mod/AIAddon/` directories persist with cache
artifacts. A complete rollback requires:
```bash
git checkout main
git clean -fdx src/Mod/AIAddon/
```
**Disposition:** accept-with-rationale — standard git behavior; document in PR description.
For user-facing rollback (addon removal): `rm -rf src/Mod/AIAddon/` is sufficient and clean.

---

## A4.3 Chaos Pass

### Scenario 1 — LLM endpoint unreachable (network down)
`openai.APIConnectionError` → subclass of `APIError` → caught in `LLMClient.chat()` → re-raised
as `LLMError` → worker catches, emits `error(str(exc))` signal → panel `_on_error()` shows in
chat → `_cleanup_worker()` called → state clean.
**Result: PASS** (covered by test_worker_logic.py::test_run_chat_handles_llm_error)

### Scenario 2 — keyring unavailable (system has no keyring daemon)
`keyring.errors.NoKeyringError` → preferences.py `_NoKeyring` sentinel → fallback to
`FC_AI_API_KEY` env var → if absent, `api_key` returns None → `_on_send` shows
"API key not set" error in chat. No crash.
**Result: PASS** (covered by test_preferences.py)

### Scenario 3 — openai 429 rate limit
`openai.RateLimitError` → subclass of `APIError` → same path as Scenario 1.
**Result: PASS** (structural — same exception hierarchy)

### Scenario 4 — Document closed during tool handler execution
**BLOCKING FINDING A4-BLOCK-1 (fixed this session):**
`executor.py`: after `openTransaction()`, if `ActiveDocument` becomes None during handler
execution, the bare `FreeCAD.ActiveDocument.abortTransaction()` raised `AttributeError`.
This propagated out of the `except` block into the Qt slot → unhandled exception → potential
FreeCAD crash.

**Fix applied:** wrapped `abortTransaction()` in guarded try/except:
```python
try:
    if FreeCAD.ActiveDocument:
        FreeCAD.ActiveDocument.abortTransaction()
except Exception:
    pass  # document was closed during handler — transaction already gone
```
**Regression test added:** `test_executor.py::test_dispatch_document_closed_during_handler`
**Result: FIXED** — 142 tests pass.

### Scenario 5 — LLM returns malformed tool call JSON
`json.JSONDecodeError` in `llm_client.py` accumulator → caught → `args = {}` →
executor `_validate_args()` returns validation error (missing required fields) →
error returned to LLM as tool result → LLM can ask user to retry.
**Result: PASS** (covered by test_llm_client.py)

### Scenario 6 — User spam-clicks Send
`self._worker is not None` guard in `_on_send()` blocks second submit while first is in
flight. Button is also disabled (`_set_busy(True)`).
**Result: PASS** (structural, confirmed by code review)

### Scenario 7 — Worker thread still running when cleanup is called
`_cleanup_worker()` calls `self._worker.quit()` + `wait(2000)`. If asyncio loop inside the
thread doesn't finish within 2s, the thread continues running as a zombie. The old thread's
signals remain connected; it will emit `finished`/`error` after `_worker` is set to None.
Those slots will still fire (panel still exists). For v0.1, the risk window is small
(only if a single LLM response takes >2s of *Python execution time*, not streaming time).
**Disposition: defer-with-rationale** — low probability in v0.1; fix in v1.1 by adding
asyncio task cancellation + extending wait or using a daemon thread.

---

## A4.4 Alert Dry-Run

Each "alert" is a FreeCAD Report View message or in-chat error.

| Alert | Trigger | Fires? | Content adequate? |
|-------|---------|--------|-------------------|
| Missing deps on startup | `openai` or `keyring` ImportError in `__init__.py` | YES — `FreeCAD.Console.PrintWarning` | YES — lists missing pkg + pip install command |
| API key not configured | `_prefs.is_configured == False` at startup | YES — `FreeCAD.Console.PrintWarning` | YES — directs to Edit > Preferences |
| Panel load failure | `AIChatPanel()` raises in `InitGui.py` | YES — `FreeCAD.Console.PrintWarning(f"Panel failed to load: {exc}")` | WARN — exc message only; no user action suggested |
| Tool execution error | handler raises or validation fails | YES — chat `_append_error()` | YES — human-readable message in chat |
| LLM HTTP error | `APIError` caught in worker | YES — chat `_append_error()` | YES |
| Worker thread timeout | `wait(2000)` expires | NO — silent | WARN — user sees no indication thread is orphaned |

**A4-W2:** Panel load failure alert lacks user action guidance.
**Disposition:** accept-with-rationale — the exception message usually contains enough context;
improving it is a v1.1 UX task.

**A4-W3:** Worker thread timeout is silent.
**Disposition:** defer-with-rationale — tied to A4.3 Scenario 7; fix together in v1.1.

---

## Summary

| Finding | Type | Disposition |
|---------|------|-------------|
| A4-BLOCK-1: `abortTransaction()` on None doc → AttributeError | BLOCKING | **FIXED** — executor.py + regression test |
| A4-W1: git rollback leaves cache dirs (`__pycache__`, `.venv`) | WARN | accept — document `git clean -fdx` in PR |
| A4-W2: panel load failure alert has no user action | WARN | accept — v1.1 UX task |
| A4-W3: worker thread timeout is silent | WARN | defer — v1.1 with asyncio cancellation |
| S4: staging soak with real FreeCAD is manual-only | DEFER | accept — document manual checklist above |

**A4 result: PASS (one blocking finding found and fixed; four non-blocking findings accepted/deferred).**
Pre-production gate cleared pending manual soak.
