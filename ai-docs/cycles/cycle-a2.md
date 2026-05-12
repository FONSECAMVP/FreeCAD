# Adversarial Cycle A2 — Design Pre-Mortem

Date: 2026-05-12

## Scenario 1: "The LLM keeps failing to use tools correctly"

Six months post-launch: users report the LLM frequently calls tools with wrong arg types, ignores required params, or calls non-existent tools. Addon feels unreliable.

**Root cause:** JSON Schema validation rejects calls but the error message sent back to the LLM ("invalid args") is not specific enough for the LLM to self-correct.

**Finding A2-S1:** DES-001 dispatch returns a generic error. LLM needs the validation error detail (which field, what constraint failed) to retry correctly.
- Severity: WARN
- Disposition: Tool executor returns structured validation error: `{"error": "validation", "field": "length", "reason": "must be > 0"}`. Add to DES-001.

## Scenario 2: "FreeCAD crashes mid-session, user loses work"

The LLM worker thread emits a signal while FreeCAD's C++ core is in a state transition (workbench switch, document load). Qt slot fires and calls FreeCAD API → segfault.

**Root cause:** DES-005 says "FreeCAD API only on main thread" but doesn't specify what to do if a workbench switch is in progress when a tool_call_ready signal fires.

**Finding A2-S2:** No guard against calling FreeCAD API during document load or workbench switch events.
- Severity: WARN
- Disposition: Add a `_busy` flag on the panel; set True during workbench switch events (connect to `FreeCADGui.activateWorkbench` signal); tool dispatch returns "busy" error if flag set. Add to DES-005.

## Scenario 3: "Addon works great but nobody can contribute new tools"

Six months in: only the original 5 workbench tool files exist. Other developers want to add tools for Spreadsheet, FEM, etc. but the registration API is undocumented and each plugin file has different patterns.

**Root cause:** No contributor guide for writing a new tool plugin. DES-002 shows file layout but no worked example.

**Finding A2-S3:** Missing canonical example tool implementation.
- Severity: WARN (solo project — but surfaces for future)
- Disposition: Add `tools/example_tool.py` with fully annotated template as part of Phase 2 scaffold.

## Chaos Questions

**Q: What if `keyring` is not installed in FreeCAD's bundled Python?**
FreeCAD ships its own Python env. `keyring` may not be available. DEC-006 specifies fallback to env var, but if neither exists, the LLM client has no API key and every call fails with 401.
- Finding A2-C1: Preferences panel must detect missing API key at startup and show a prominent warning, not silently fail on first user message.
- Severity: WARN → add to DES-006.

**Q: What if the openai SDK is not installed in FreeCAD's Python?**
`openai` is not bundled with FreeCAD. Importing it at addon load will raise `ModuleNotFoundError`, crashing the addon before the user sees anything.
- Finding A2-C2 (BLOCKING): Addon must check for `openai` and `keyring` at load time; if missing, show install instructions in Report View and disable chat panel gracefully. Do not crash FreeCAD.
- Disposition: Add REQ-028: addon checks required deps at load; surfaces install instructions if missing.

**Q: What if the user's FreeCAD document has 500 objects?**
Context injector (DES-009) sends full object list. 500 objects × ~30 chars each = ~15KB injected into every message. Combined with conversation history, may blow token budget before user message.
- Finding A2-C3: Context injector must be bounded. Send only selected objects + first N objects of document (default N=20).
- Severity: WARN → update DES-009.

## Cost Worst-Case

Each user message → ~8000 tokens in + ~1000 tokens out (tool calls + response) = ~9000 tokens/message.
At GPT-4o pricing ($5/1M in, $15/1M out): ~$0.055/message. At 50 messages/session: ~$2.75/session.
At Claude Sonnet pricing ($3/1M in, $15/1M out): ~$0.039/message.
**No cost gate in v1** — user controls their own API key and pays directly. Not a blocker. Document in README.

## Migration Trap

If conversation history format (DES-003 message list) changes in v2 (e.g., adding metadata fields), in-memory sessions are unaffected (they're transient). No migration needed. ✓

## Summary

| Finding | Severity | Disposition |
|---------|----------|-------------|
| A2-S1 generic validation errors | WARN | Update DES-001 |
| A2-S2 FreeCAD busy guard | WARN | Update DES-005 |
| A2-S3 contributor example tool | WARN | Phase 2 scaffold |
| A2-C1 missing API key warning | WARN | Update DES-006 |
| A2-C2 missing openai/keyring | BLOCKING | New REQ-028 |
| A2-C3 context size bound | WARN | Update DES-009 |

**Overall A2 result:** CONDITIONAL PASS — one blocking finding (A2-C2) must be dispositioned. All others are WARN, dispositioned inline.
