# Decision Ledger

## DEC-001 — Top-level solution shape

- **Date:** 2026-05-12
- **Status:** accepted
- **Question:** What is the top-level architecture of the LLM–FreeCAD integration?
- **Alternatives:** (A) thin tool shim, (B) tool registry with workbench plugins, (C) LLM macro generation
- **Scores:**

| Pillar | A | B | C |
|--------|---|---|---|
| Reliability | 4 | 4 | 2 |
| Scalability | 3 | 5 | 4 |
| Maintainability | 5 | 4 | 2 |
| Best Practices | 4 | 5 | 1 |

- **Choice:** B — tool registry with workbench plugins
- **Rationale:** Scalability to new workbenches without core changes; plugin pattern enables contributor growth; matches OpenAI function-calling / MCP tool conventions.
- **Reversibility:** Medium — switching to A is a simplification (downgrade); switching to C excluded by AMB-009.
- **Dependents:** DEC-002 (tool registry interface), DEC-003 (conversation state), DEC-004 (LLM API integration), DEC-008 (testing toolchain)

---

## DEC-002 — Tool Registry Interface

- **Date:** 2026-05-12 | **Status:** accepted
- **Question:** How do workbench plugins register tools with the registry?
- **Choice:** B — explicit `registry.register(tool_name, schema, handler)` call per plugin module
- **Rationale:** Predictable, grep-able, no magic. Matches explicit registration patterns in FastAPI/LangChain.
- **Reversibility:** High — registration call is one line per tool; easy to restructure.
- **Dependents:** DES-001 (registry interface spec), DES-002 (plugin module structure)

---

## DEC-003 — Conversation State Storage

- **Date:** 2026-05-12 | **Status:** accepted
- **Question:** Where does session conversation history live?
- **Choice:** A — in-memory list on panel object, truncated per REQ-021
- **Rationale:** Simplest; matches v1 session-only scope. SQLite can replace it in v2 without touching tool layer.
- **Reversibility:** High — swap storage backend without affecting registry or tools.
- **Dependents:** DES-003 (conversation state schema)

---

## DEC-004 — LLM API Client

- **Date:** 2026-05-12 | **Status:** accepted
- **Question:** How does the addon call the LLM?
- **Choice:** B — `openai` Python SDK with `base_url` override for provider-agnostic support
- **Rationale:** Built-in retry, streaming, error handling. `AsyncOpenAI` pairs with Qt worker thread (DEC-005).
- **Reversibility:** Medium — swapping SDK requires rewriting client wrapper only.
- **Dependents:** DES-004 (LLM client wrapper), DEC-005 (thread model)

---

## DEC-005 — Qt Thread Model

- **Date:** 2026-05-12 | **Status:** accepted
- **Question:** How to run async LLM calls without blocking Qt or violating FreeCAD thread safety?
- **Choice:** A — QThread worker for HTTP; pyqtSignal delivers results to main thread; FreeCAD API called from main thread slot only
- **Rationale:** FreeCAD-native pattern. Eliminates GIL/segfault risk. Resolves A1-C1 blocking finding.
- **Reversibility:** Medium — thread model touches panel and worker classes.
- **Dependents:** DES-005 (worker thread design)

---

## DEC-006 — API Key Storage

- **Date:** 2026-05-12 | **Status:** accepted
- **Question:** Where to store LLM API key?
- **Choice:** B — `keyring` lib (OS keychain); fallback to env var if keyring unavailable
- **Rationale:** Satisfies REQ-NFR-004. Plain XML (option A) fails the no-plaintext-credential requirement.
- **Reversibility:** High — storage backend isolated in preferences module.
- **Dependents:** DES-006 (preferences module)

---

## DEC-007 — Observability / Logging

- **Date:** 2026-05-12 | **Status:** accepted
- **Question:** Where do tool call logs go?
- **Choice:** A — `FreeCAD.Console.PrintLog` for tool events; Python `logging` module for debug output
- **Rationale:** FreeCAD convention; zero config; visible in Report View by default.
- **Reversibility:** High — logging calls are isolated, easy to redirect.
- **Dependents:** DES-007 (logging strategy)

---

## DEC-008 — Testing Toolchain

- **Date:** 2026-05-12 | **Status:** accepted
- **Choice:** B — pytest + pytest-qt + pytest-asyncio + pytest-cov
- **Rationale:** De-facto standard; fixture system scales cleanly; pytest-qt enables Qt widget tests without display.
- **Reversibility:** High.
- **Dependents:** pyproject.toml, tests/conftest.py

---

## DEC-009 — Style/Quality Toolchain

- **Date:** 2026-05-12 | **Status:** accepted
- **Choice:** B — ruff (lint + format) + mypy (type checking)
- **Rationale:** Single tool replaces flake8+isort+pyupgrade. One config block in pyproject.toml.
- **Reversibility:** High.
- **Dependents:** pyproject.toml, .pre-commit-config.yaml

---

## DEC-010 — Pre-commit Automation

- **Date:** 2026-05-12 | **Status:** accepted
- **Choice:** B — pre-commit hooks: ruff, mypy, exec/eval grep gate, pytest fast-unit marker
- **Rationale:** Automatic gate on every commit; prevents bad history; zero manual discipline required.
- **Reversibility:** High.
- **Dependents:** .pre-commit-config.yaml

---

## DEC-011 — Rollout Strategy

- **Date:** 2026-05-12 | **Status:** accepted
- **Question:** How does AI Addon v0.1 reach end users?
- **Alternatives:** (A) merge to FreeCAD upstream main, (B) standalone FreeCAD Addon Manager package, (C) local personal deploy only
- **Scores:**

| Pillar | A | B | C |
|--------|---|---|---|
| Reliability | 2 | 4 | 5 |
| Scalability | 5 | 4 | 1 |
| Maintainability | 2 | 4 | 5 |
| Best Practices | 3 | 5 | 4 |

- **Choice:** B — standalone FreeCAD Addon Manager package in separate GitHub repo
- **Rationale:** Correct FreeCAD pattern for experimental addons (how SheetMetal, A2plus, AutoFEM launched). Independent release cycle; opt-in install; low blast radius; rollback = uninstall. Upstream merge (A) premature for v0.1 without community validation.
- **Reversibility:** Medium — moving from B to A later requires FreeCAD maintainer buy-in and passing their CI/review process.
- **Dependents:** package.xml, README.md, external `FreeCAD-AI-Addon` GitHub repo
