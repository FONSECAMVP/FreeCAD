# Traceability Matrix

_Updated: 2026-05-12 — Phase 2 complete. 138 tests passing. A3 done. CLV-003 remediations applied._

| REQ | DEC | DES | TEST file | COMMIT |
|-----|-----|-----|-----------|--------|
| REQ-001 (prefs panel) | DEC-006 | DES-006 | test_preferences.py | — |
| REQ-002 (chat panel) | DEC-005 | DES-008 | test_panel_integration.py (skipped/manual) | — |
| REQ-003 (tool registry) | DEC-002 | DES-001 | test_registry.py | — |
| REQ-004 (tool executor) | DEC-002 | DES-001 | test_executor.py | — |
| REQ-005 (doc context) | DEC-003 | DES-009 | test_context.py | — |
| REQ-006 (Part tools) | DEC-002 | DES-002 | test_tools_part.py | — |
| REQ-007 (PartDesign tools) | DEC-002 | DES-002 | test_tools_partdesign.py | — |
| REQ-008 (Sketcher tools) | DEC-002 | DES-002 | test_tools_sketcher.py | — |
| REQ-009 (inspection tools) | DEC-002 | DES-002 | test_tools_inspection.py | — |
| REQ-010 (conversation history) | DEC-003 | DES-003 | test_conversation.py | — |
| REQ-011 (async + loading) | DEC-004, DEC-005 | DES-004, DES-005 | test_llm_client.py, test_worker_logic.py | — |
| REQ-012 (error display) | DEC-005 | DES-008 | test_panel_integration.py (skipped/manual) | — |
| REQ-013 (Draft tools) | DEC-002 | DES-002 | test_tools_draft.py | — |
| REQ-014 (BIM tools) | DEC-002 | DES-002 | test_tools_bim.py | — |
| REQ-015 (tool detail collapsible) | DEC-005 | DES-008 | test_panel_integration.py (skipped/manual) | — |
| REQ-019 (lazy import) | DEC-002 | DES-002 | test_registry.py | — |
| REQ-020 (transaction abort) | DEC-002 | DES-001 | test_executor.py | — |
| REQ-021 (history truncation) | DEC-003 | DES-003 | test_conversation.py | — |
| REQ-022 (system prompt clarify) | DEC-004 | DES-004 | test_llm_client.py | — |
| REQ-023 (multi-tool undo units) | DEC-002 | DES-001 | test_executor.py | — |
| REQ-024 (string arg validation) | DEC-002 | DES-001 | test_executor.py | — |
| REQ-025 (no active doc guard) | DEC-002 | DES-001 | test_executor.py | — |
| REQ-026 (headless mode) | DEC-005 | DES-008 | test_worker_logic.py (partial; panel-skip untested) | — |
| REQ-027 (workbench activation) | DEC-002 | DES-001 | test_executor.py | — |
| REQ-028 (dep check on load) | DEC-001 | DES-002 | test_deps.py | — |
| A3 hardening (cross-cutting) | DEC-002, DEC-003 | DES-001, DES-003 | test_a3_hardening.py | — |
