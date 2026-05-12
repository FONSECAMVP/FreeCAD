# Product Requirements Document — FreeCAD AI Addon

Version: 0.1 | Date: 2026-05-12 | Status: draft

## Goals

Enable a beginner FreeCAD user to describe design intent in natural language and have an LLM agent execute the corresponding FreeCAD operations via a structured tool API, without the user needing to know workbench names, API calls, or constraint syntax.

## User Stories

### US-001 — Configure LLM connection
As a user, I want to enter my LLM API endpoint, model name, and API key in FreeCAD Preferences so that the addon connects to my chosen provider.

**Acceptance:** Preferences panel exists under Edit > Preferences > AI Addon. Fields: base_url, model, api_key. On save, a test ping to the endpoint succeeds and shows confirmation, or shows error message on failure.

### US-002 — Open chat panel
As a user, I want a dockable chat panel in the FreeCAD main window so I can type natural language requests.

**Acceptance:** Menu item View > Panels > AI Chat opens a Qt dockable panel. Panel persists across workbench switches within the session.

### US-003 — Send design request
As a user, I want to type "create a 50x30x10mm box" and have the addon create that box in the active FreeCAD document.

**Acceptance:** After submit, a Part::Box appears in the model tree with correct dimensions. The operation is on FreeCAD's undo stack (Ctrl+Z removes it).

### US-004 — Inspect active model
As a user, I want the LLM to know what objects are in my document so it can refer to them.

**Acceptance:** LLM receives current document object list and selected object(s) as context before each request.

### US-005 — Parametric feature creation
As a user, I want to say "add a 10mm pocket to the top face of the box" and have a PartDesign Pocket created.

**Acceptance:** PartDesign Body + Pocket feature created with correct depth. Operation undoable.

### US-006 — Sketch creation
As a user, I want to say "sketch a 40mm circle on the XY plane" and have a constrained Sketcher sketch created.

**Acceptance:** Sketcher sketch on XY plane containing a circle with radius 20mm, fully constrained.

### US-007 — Error feedback
As a user, when an LLM tool call fails (invalid args, FreeCAD API error), I want to see a plain-language error message in the chat panel.

**Acceptance:** Failed tool calls display a human-readable error in chat. FreeCAD document state is unchanged (no partial geometry).

### US-008 — Loading state
As a user, I want to see a visual indicator while the LLM is thinking so I know the addon is working.

**Acceptance:** Spinner or "Thinking…" indicator appears from submit until first response token arrives. Panel is not frozen (Qt event loop not blocked).

## Non-Functional Requirements

### Performance
- REQ-NFR-001: Chat panel submit → first response token ≤ 5s on a 100Mbps connection (network-bound, not app-bound). **Criterion:** measure with local Ollama model on same machine; must be non-blocking.
- REQ-NFR-002: Tool execution (FreeCAD API call) ≤ 2s for any single tool. **Criterion:** timed in unit tests with mock FreeCAD API.

### Security
- REQ-NFR-003: No raw Python exec path exists in the addon. **Criterion:** grep for `exec(` and `eval(` in addon source returns 0 results (excluding test fixtures).
- REQ-NFR-004: API key stored in FreeCAD's credential store, never written to plain-text files or logged. **Criterion:** code review + automated secret scan.

### Reliability
- REQ-NFR-005: Tool executor catches all FreeCAD API exceptions and rolls back partial document changes before surfacing error to LLM. **Criterion:** test suite covers exception paths for every tool.

### Accessibility / UX
- REQ-NFR-006: Chat panel functional at 100%, 125%, 150% Qt DPI scaling. **Criterion:** manual test on each scale factor.

### Observability
- REQ-NFR-007: Each tool call logs tool name, args (redacted if containing sensitive strings), result status, and duration to FreeCAD's Report View. **Criterion:** log output verified in integration tests.

## Requirements Table

| ID | Title | Category | Priority |
|----|-------|----------|----------|
| REQ-001 | LLM preferences panel (base_url, model, api_key) | Config | must |
| REQ-002 | Dockable Qt chat panel | UI | must |
| REQ-003 | Tool registry — plugin registration interface | Core | must |
| REQ-004 | Tool executor — validate args, call FreeCAD API, undo support | Core | must |
| REQ-005 | Document context injection (object list, selection) | Core | must |
| REQ-006 | Part workbench tools: box, cylinder, sphere, cone, boolean (union/cut/common), export shape | Tools | must |
| REQ-007 | PartDesign workbench tools: new body, pad, pocket, fillet, chamfer | Tools | must |
| REQ-008 | Sketcher workbench tools: new sketch, line, circle, arc, polyline, coincident/distance/radius constraints | Tools | must |
| REQ-009 | Model inspection tools: list objects, get properties, get selection | Tools | must |
| REQ-010 | Session conversation history sent to LLM on each request | Core | must |
| REQ-011 | Async LLM call (non-blocking Qt event loop) with loading indicator | UI | must |
| REQ-012 | Human-readable error display in chat on tool failure | UI | must |
| REQ-013 | Draft workbench tools: line, rectangle, circle, bspline, array, move, rotate | Tools | should |
| REQ-014 | BIM/Arch workbench tools: wall, slab, column, stair, roof | Tools | should |
| REQ-015 | Tool call detail collapsible in chat (show/hide tool name + args) | UI | nice |
| REQ-016 | Cross-session conversation persistence | Core | non-goal (v1) |
| REQ-017 | FEM/CAM tool coverage | Tools | non-goal (v1) |
| REQ-018 | Raw Python execution path | Security | non-goal (excluded) |
| REQ-019 | Workbench tool plugins use lazy import (import on first call, not at registration) | Core | must |
| REQ-020 | Tool executor wraps each call in FreeCAD openTransaction/commitTransaction; abortTransaction on exception | Core | must |
| REQ-021 | Conversation history truncated to configurable max_tokens (default 8000) using last-N strategy | Core | must |
| REQ-022 | System prompt instructs LLM to ask for missing required params rather than guess | Core | must |
| REQ-023 | Each tool call is independent undo unit; multi-tool sequence = multiple undo entries | Core | should |
| REQ-024 | String args validated: alphanumeric + space + underscore + hyphen, max 128 chars | Security | must |
| REQ-025 | Tool executor checks for active document; if none, returns error message to user | Core | must |
| REQ-026 | Chat panel skipped in headless mode; tool registry and executor work headless | Core | should |
| REQ-027 | Tool executor activates required workbench before tool execution if not already active | Core | should |
| REQ-028 | Addon checks for openai + keyring deps at load; shows install instructions and disables panel if missing (no crash) | Core | must |

## Explicit Non-Goals (v1)
- Cross-session memory / conversation history persistence
- FEM, CAM, Mesh, Spreadsheet workbench tools
- Multi-document operations
- Collaborative / multi-user sessions
- Raw Python exec (permanently excluded by design)

## Success Metrics
- Beginner user creates a padded PartDesign solid from natural language in ≤ 3 exchanges
- All "must" REQs have passing tests in CI
- Zero `exec(`/`eval(` calls in addon source
- Tool registry loads all 5 workbench plugins without error on FreeCAD startup
