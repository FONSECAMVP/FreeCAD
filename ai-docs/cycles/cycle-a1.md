# Adversarial Cycle A1 — Requirements Red Team

Date: 2026-05-12

## Hat 1: Lawyer (exact wording, gaps, contradictions)

**Finding A1-L1:** REQ-003 says "plugin registration interface" but does not specify WHEN plugins register. If a workbench plugin registers tools before FreeCAD loads that workbench, the FreeCAD module may not be importable yet, causing ImportError at startup.
- Severity: BLOCKING
- Disposition: Add REQ to defer workbench tool imports to first-use (lazy import), or register at workbench activation event.

**Finding A1-L2:** REQ-004 says "undo support" but FreeCAD's undo API requires wrapping operations in `openTransaction`/`commitTransaction`. If a tool calls multiple FreeCAD API calls, a partial failure mid-sequence could corrupt the document unless the transaction is explicitly aborted.
- Severity: BLOCKING
- Disposition: Add REQ that tool executor wraps every tool call in a single FreeCAD transaction; on exception, calls `abortTransaction`.

**Finding A1-L3:** REQ-001 acceptance criterion says "test ping succeeds" but doesn't define what a ping looks like for arbitrary OpenAI-compatible endpoints. Some local providers (Ollama) don't implement `/models` or respond differently.
- Severity: WARN
- Disposition: Acceptance criterion narrowed: ping = attempt a minimal chat completion with zero tokens; success = HTTP 2xx or expected error body. Document in DES.

**Finding A1-L4:** REQ-010 says "session conversation history sent to LLM" but sets no upper bound on history length. LLMs have context windows; unbounded history will cause token limit errors.
- Severity: BLOCKING
- Disposition: Add REQ: conversation history truncated to configurable max_tokens before sending (default: 8000 tokens, last-N strategy).

## Hat 2: Persona

### Novice user
**Finding A1-P1:** User types "make a box" with no dimensions. LLM must ask for dimensions, but the PRD has no REQ for clarification turns. If LLM just guesses 10x10x10, user doesn't understand why.
- Severity: WARN
- Disposition: Add REQ: LLM system prompt instructs it to ask for missing required parameters rather than guess. Acceptance: test with under-specified prompt.

### Power user
**Finding A1-P2:** Power user wants to chain 5 operations in one message. PRD has no REQ for multi-tool calls per message. LLM may attempt sequential tool calls; if tool call 3 fails, state of calls 1-2 is unclear.
- Severity: WARN
- Disposition: Add REQ: each tool call is an independent undo unit; multi-step sequences create multiple undo entries.

### Malicious actor (inside the app)
**Finding A1-P3:** LLM tool args are user-controlled. A user could craft a message that causes the LLM to emit `{"name": "create_box", "args": {"label": "../../etc/passwd"}}`. Tool executor must sanitize string args used in file system operations.
- Severity: WARN (most tool args are numeric, but label/name string args exist)
- Disposition: Add REQ: string args validated against allowlist pattern (alphanumeric + space + underscore + hyphen, max 128 chars) before passing to FreeCAD API.

## Hat 3: Edge Cases

**Finding A1-E1:** No active document when user sends first message. Most FreeCAD API calls require `FreeCAD.ActiveDocument`. Tool executor will crash with AttributeError.
- Severity: BLOCKING
- Disposition: Add REQ: tool executor checks for active document before any tool call; if none, auto-creates a new document or returns error asking user to create one.

**Finding A1-E2:** FreeCAD running headless (no GUI). REQ-002 assumes Qt GUI. Some CI/test environments run FreeCAD without GUI.
- Severity: WARN
- Disposition: Add REQ: chat panel gracefully degrades / is skipped in headless mode; tool executor and registry work headless (testable without GUI).

**Finding A1-E3:** User switches active workbench mid-conversation. Some tools (PartDesign) require the PartDesign workbench to be active. Calling them from the wrong workbench context causes errors.
- Severity: WARN
- Disposition: Add REQ: tool executor activates the required workbench before executing a tool if not already active.

## Hat 4: Contradictions

**Finding A1-C1:** REQ-011 (async LLM call) conflicts with FreeCAD's Python GIL. FreeCAD's C++ core is not fully thread-safe; running LLM HTTP calls on a background thread and then calling FreeCAD API from that thread risks segfault.
- Severity: BLOCKING
- Disposition: LLM HTTP call on Qt worker thread; FreeCAD API calls dispatched back to main thread via Qt signal/slot. This is a critical architectural constraint — must become a DES entry.

**Finding A1-C2:** REQ-NFR-001 (≤5s response) is network-bound, not testable in unit tests. Criterion references "local Ollama on same machine" but unit tests use mocks. Need separate integration test tier.
- Severity: WARN
- Disposition: Split test tiers: unit (mocked) + optional integration (real endpoint). CI runs unit only; integration is opt-in.

## Summary

| ID | Severity | Status |
|----|----------|--------|
| A1-L1 lazy import | BLOCKING | → new REQ-019 |
| A1-L2 transaction abort | BLOCKING | → new REQ-020 |
| A1-L3 ping definition | WARN | → narrow REQ-001 acceptance |
| A1-L4 history truncation | BLOCKING | → new REQ-021 |
| A1-P1 clarification turns | WARN | → new REQ-022 |
| A1-P2 multi-tool undo | WARN | → new REQ-023 |
| A1-P3 string arg injection | WARN | → new REQ-024 |
| A1-E1 no active document | BLOCKING | → new REQ-025 |
| A1-E2 headless mode | WARN | → new REQ-026 |
| A1-E3 workbench activation | WARN | → new REQ-027 |
| A1-C1 GIL/thread safety | BLOCKING | → DES constraint |
| A1-C2 NFR-001 testability | WARN | → split test tiers |

**Blocking findings (4):** A1-L1, A1-L2, A1-L4, A1-E1, A1-C1 — all must be dispositioned before Phase 1 exit.
