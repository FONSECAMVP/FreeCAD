# Ambiguities

| ID | Term / Assumption | Status | Notes |
|----|-------------------|--------|-------|
| AMB-001 | "infrastructure" — FreeCAD Addon/Mod, external server, or MCP server? | **RESOLVED** | FreeCAD Addon (in-process) |
| AMB-002 | "all kind of features" — which workbenches are in scope for v1? | **RESOLVED** | Part, PartDesign, Sketcher, Draft, BIM/Arch |
| AMB-003 | "interact with" — read-only (inspect model) or read-write (create/modify geometry)? | **RESOLVED** | Both — read (inspect) + write (create/modify) |
| AMB-004 | Which LLM provider? Claude API, OpenAI, local (Ollama), or provider-agnostic? | **RESOLVED** | Provider-agnostic (OpenAI-compatible interface) |
| AMB-005 | Where does the LLM run relative to FreeCAD? In-process, sidecar, remote service? | **RESOLVED** | LLM client lives in-process inside FreeCAD Addon |
| AMB-006 | User interaction modality — chat panel inside FreeCAD GUI, CLI, external app? | **RESOLVED** | Dockable chat panel inside FreeCAD Qt GUI |
| AMB-007 | "design of pieces" — mechanical parts only, or also architecture (BIM), FEM analysis, CAM toolpaths? | **RESOLVED** | Part + PartDesign + Sketcher + Draft + BIM/Arch (v1 scope) |
| AMB-008 | Persistence — does the LLM maintain conversation context across sessions? | **RESOLVED** | Session-only (v1); no cross-session memory |
| AMB-009 | Does the LLM execute Python directly in FreeCAD, or call a structured tool API? | **RESOLVED** | Structured tools only — no raw Python exec |
| AMB-010 | Target user — FreeCAD beginner, power user, or both? | **RESOLVED** | Beginner-first |
