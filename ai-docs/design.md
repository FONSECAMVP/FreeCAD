# System Design Document — FreeCAD AI Addon

Version: 0.1 | Date: 2026-05-12

---

## DES-001 — Tool Registry Interface (← DEC-002)

### Plugin registration API

```python
# freecad_ai/registry.py
class ToolRegistry:
    def register(
        self,
        name: str,           # e.g. "create_box"
        schema: dict,        # JSON Schema for args (OpenAI function-calling format)
        handler: Callable,   # fn(args: dict) -> dict  — called on main thread
        workbench: str,      # e.g. "Part" — activated before handler call (REQ-027)
    ) -> None: ...

    def get_tools_for_llm(self) -> list[dict]:
        """Returns OpenAI-format tools list."""

    def dispatch(self, name: str, args: dict) -> dict:
        """Validates args, activates workbench, wraps in transaction, calls handler.
        On validation failure returns: {"error": "validation", "field": str, "reason": str}
        On unknown tool returns: {"error": "unknown_tool", "name": str}
        On FreeCAD API exception returns: {"error": "execution", "message": str}
        """
```

### Tool schema format (OpenAI function-calling)

```json
{
  "type": "function",
  "function": {
    "name": "create_box",
    "description": "Create a rectangular solid (Part::Box) in the active document.",
    "parameters": {
      "type": "object",
      "properties": {
        "length": {"type": "number", "description": "Length in mm"},
        "width":  {"type": "number", "description": "Width in mm"},
        "height": {"type": "number", "description": "Height in mm"},
        "label":  {"type": "string", "description": "Object name in model tree"}
      },
      "required": ["length", "width", "height"]
    }
  }
}
```

---

## DES-002 — Plugin Module Structure (← DEC-002)

```
freecad_ai/
├── __init__.py              # Addon entry point; loads registry; activates chat panel
├── registry.py              # ToolRegistry class (DES-001)
├── executor.py              # Transaction wrapper, workbench switcher, arg validator
├── llm_client.py            # OpenAI SDK wrapper (DES-004)
├── worker.py                # QThread worker (DES-005)
├── preferences.py           # Prefs panel + keyring storage (DES-006)
├── panel.py                 # Qt chat panel (DES-008)
├── context.py               # Document context injector (DES-009)
└── tools/
    ├── __init__.py          # calls registry.register() for all tools in this package
    ├── part.py              # Part workbench tools (REQ-006)
    ├── partdesign.py        # PartDesign tools (REQ-007)
    ├── sketcher.py          # Sketcher tools (REQ-008)
    ├── inspection.py        # Model inspection tools (REQ-009)
    ├── draft.py             # Draft tools (REQ-013)
    └── bim.py               # BIM/Arch tools (REQ-014)
```

**Lazy import rule (REQ-019):** `tools/part.py` does NOT import `Part` at module level. Handler functions import inside the function body:
```python
def _handle_create_box(args: dict) -> dict:
    import Part  # lazy — safe if workbench not loaded at register time
    ...
```

---

## DES-003 — Conversation State Schema (← DEC-003)

```python
# In-memory on AIChatPanel instance
messages: list[dict] = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user",   "content": "create a 50mm box"},
    {"role": "assistant", "content": None, "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "...", "content": "{\"label\": \"Box\"}"},
]
```

Truncation (REQ-021): before each LLM call, trim oldest non-system messages until token estimate ≤ `max_tokens` (default 8000). Token estimate: `len(json.dumps(messages)) // 4` (rough approximation; acceptable for v1).

---

## DES-004 — LLM Client Wrapper (← DEC-004)

```python
# freecad_ai/llm_client.py
from openai import AsyncOpenAI

class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self._model = model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> AsyncIterator[str | ToolCall]:
        """Yields streamed text tokens and ToolCall objects."""
```

The worker (DES-005) calls `asyncio.run(client.chat(...))` inside QThread — safe because asyncio event loop is created fresh per call, not shared with Qt.

---

## DES-005 — Worker Thread Design (← DEC-005, resolves A1-C1)

```
Main thread (Qt)                    LLMWorker (QThread)
     │                                      │
     │ worker.start()                       │
     │──────────────────────────────────────►│
     │                                      │ asyncio.run(client.chat(...))
     │                                      │ — HTTP call —
     │◄─────────────────────────────────────│ emit token_received(str)
     │ slot: append token to chat           │
     │◄─────────────────────────────────────│ emit tool_call_ready(name, args)
     │ slot: registry.dispatch(name, args)  │  ← FreeCAD API HERE, main thread only
     │◄─────────────────────────────────────│ emit finished(tool_results)
     │ slot: send tool results back / done  │
```

`registry.dispatch()` is ONLY called from main thread slots — never from inside QThread.

**Busy guard (A2-S2):** Panel sets `_busy = True` when connected to FreeCADGui workbench-switch and document-load signals. `dispatch()` returns `{"error": "busy"}` if `_busy` is True, preventing FreeCAD API calls during unsafe transitions.

---

## DES-006 — Preferences Module (← DEC-006)

Fields stored:
| Field | Storage | Notes |
|-------|---------|-------|
| `base_url` | FreeCAD Preferences XML | Not sensitive |
| `model` | FreeCAD Preferences XML | Not sensitive |
| `api_key` | OS keychain via `keyring` | Falls back to `FC_AI_API_KEY` env var |
| `max_tokens` | FreeCAD Preferences XML | Default 8000 |

Preferences panel: Edit > Preferences > AI Addon (Qt preferences page, `FreeCADGui.addPreferencePage`).

**Missing credential guard (A2-C1):** On addon load, if API key is absent from keyring and `FC_AI_API_KEY` env var is unset, `FreeCAD.Console.PrintWarning` + chat panel shows banner: "API key not configured — open Edit > Preferences > AI Addon."

---

## DES-007 — Logging Strategy (← DEC-007)

```python
import FreeCAD
import logging

log = logging.getLogger("freecad_ai")

def _log_tool_call(name: str, args: dict, status: str, duration_ms: float):
    # Redact string args that look like keys (contain "key", "token", "secret")
    safe_args = {k: ("***" if any(s in k.lower() for s in ("key","token","secret")) else v)
                 for k, v in args.items()}
    FreeCAD.Console.PrintLog(
        f"[AI] tool={name} status={status} duration={duration_ms:.0f}ms args={safe_args}\n"
    )
```

---

## DES-008 — Qt Chat Panel (← REQ-002, REQ-011, REQ-012, REQ-015)

```
┌─ AI Chat ──────────────────────────────────────┐
│ ┌──────────────────────────────────────────┐   │
│ │ [assistant] Box created: 50×30×10mm     │   │
│ │ ▸ tool: create_box {length:50, ...}     │   │  ← collapsible (REQ-015)
│ │ [user] add a 10mm pocket on top         │   │
│ │ ● Thinking…                             │   │  ← loading indicator (REQ-011)
│ └──────────────────────────────────────────┘   │
│ [___________________________] [Send]            │
└────────────────────────────────────────────────┘
```

- `QTextBrowser` for history (supports HTML for collapsible tool detail)
- `QLineEdit` + `QPushButton` for input
- Send button disabled during LLM call (re-enabled on `finished` signal)

---

## DES-009 — Document Context Injector (← REQ-004, REQ-005)

Before each LLM call, a context snapshot is prepended to the user message:

```
[Context]
Active document: MyPart (3 objects)
Objects: Box (Part::Box), Sketch (Sketcher::SketchObject), Body (PartDesign::Body)
Selection: Box
```

Generated by `context.py::build_context()` — reads `FreeCAD.ActiveDocument` on main thread before handing off to worker.

**Bounded output (A2-C3):** Object list capped at 20 items (configurable). If document has >20 objects, include selected objects first, then first N by label sort. Total context string target: ≤500 chars.

---

## Failure Modes Table

| Scenario | Detection | Recovery |
|----------|-----------|----------|
| No active document | `FreeCAD.ActiveDocument is None` in executor | Return error message to LLM; display in chat |
| FreeCAD API exception in tool | try/except around handler call | `abortTransaction()`; error message to chat; doc unchanged |
| LLM HTTP error (4xx/5xx) | openai SDK raises exception in worker | emit `error` signal; display in chat; no doc change |
| LLM returns invalid tool name | `name not in registry` check in dispatch | Return error to LLM as tool result; LLM can retry |
| Token limit exceeded | Truncation in DES-003 before send | Transparent to user; oldest messages dropped |
| keyring unavailable | `keyring.errors.NoKeyringError` in prefs | Fallback to env var; warn in Report View |

---

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| LLM hallucinated tool args causing invalid API calls | JSON Schema validation in executor before handler call |
| String arg injection (path traversal, code injection) | REQ-024 allowlist validation on all string args |
| API key in plaintext | DEC-006: keyring storage; redacted in logs (DES-007) |
| Arbitrary Python execution | No exec/eval in codebase; REQ-NFR-003 enforced by CI scan |
| Unbounded LLM context cost | REQ-021 max_tokens truncation |

---

## Observability Plan

- Tool call: name, args (redacted), status, duration → FreeCAD Report View
- LLM HTTP errors → FreeCAD Report View + chat panel
- Addon startup / plugin registration count → `FreeCAD.Console.PrintMessage`
- Debug verbose logging → Python `logging` module (opt-in via env `FC_AI_DEBUG=1`)
