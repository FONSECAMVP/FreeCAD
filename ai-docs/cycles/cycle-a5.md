# Adversarial Cycle A5 — Post-Launch Retrospective

**Status: TEMPLATE — fill in after monitoring window elapses.**

Per PRD success metrics, the monitoring window is: first 2 weeks after v0.1.0 tag is
published on the external FreeCAD-AI-Addon repo and Addon Manager submission is made.

---

## A5.1 Did success metrics move as predicted?

PRD success metrics to evaluate:
1. **Beginner user creates padded PartDesign solid from natural language in ≤3 exchanges**
   - Predicted: achievable with current tool set
   - Actual: _[fill in after user testing]_

2. **All "must" REQs have passing tests in CI**
   - Predicted: YES (142 tests, 72% coverage)
   - Actual: _[fill in after CI runs on external repo]_

3. **Zero exec()/eval() calls in addon source**
   - Predicted: YES (CI + pre-commit gate enforce)
   - Actual: _[confirm on release tag]_

4. **Tool registry loads all 5 workbench plugins without error on FreeCAD startup**
   - Predicted: YES (validated by code review; test_registry.py covers registration)
   - Actual: _[fill in from manual soak]_

---

## A5.2 Surprises

_[Fill in: what broke that wasn't in A2's failure narratives or A4's chaos pass?]_

Known gaps to watch:
- PySide2 vs PySide6 compatibility on FreeCAD 1.0+ (uses PySide6)
- `FreeCADGui.Qt.RightDockWidgetArea` attribute path variance (A4-W2)
- Keyring daemon availability on headless/server Linux installs

---

## A5.3 User-facing issues

_[Fill in: did A1 persona walks accurately predict user behavior?]_

Personas to revisit:
- Novice user who doesn't know they need an API key
- Power user who sends very long context (>8000 tokens)
- User on macOS with system keychain (different keyring backend)

---

## A5.4 Costs vs. estimates

LLM cost model from A2:
- Estimated: ~$0.001–$0.01 per design request (GPT-4o-mini tier)
- Actual: _[fill in from real usage]_
- Token burn rate: _[fill in from conversation history logs]_

---

## A5.5 Findings for Phase 0 of v1.1

_[Fill in after retrospective is complete. Seed the next iteration's intake.md.]_

Known candidates for v1.1 based on A4 deferred items:
- Asyncio task cancellation in LLMWorker (A4-W3)
- Panel load failure alert with user action guidance (A4-W2)
- Cross-session conversation persistence (REQ-016 non-goal in v1)
- FEM/CAM tool coverage (REQ-017 non-goal in v1)
- Timing integration tests for REQ-NFR-007
