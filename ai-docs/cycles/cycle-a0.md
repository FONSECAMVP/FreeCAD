# Adversarial Cycle A0 — Should We Build This?

Date: 2026-05-12

## Challenge 1: Does the problem actually exist?

FreeCAD's Python API is well-documented and powerful. Could the user just learn it?

**Finding:** Yes, the problem exists. FreeCAD's API requires knowing workbench activation, document creation, shape primitives, constraint syntax, and topological naming — easily 50+ concepts before a beginner produces a useful part. Natural language → geometry is a real capability gap.

**Disposition:** Accept — problem is real.

## Challenge 2: Is an LLM the right tool?

Alternatives: a wizard UI, scripted templates, a node-based visual programming interface.

**Finding:** LLMs uniquely handle open-ended intent — "make something that fits in my hand with a slot for a USB cable" can't be covered by templates. Wizard UIs cover known patterns only. LLM is appropriate for intent-to-API translation.

**Disposition:** Accept — LLM is appropriate.

## Challenge 3: Does FreeCAD's API actually support programmatic control of all stated features?

**Finding:** FreeCAD exposes a rich Python API (FreeCAD, FreeCADGui, Part, PartDesign, Sketcher modules). Most GUI operations have Python equivalents. Some operations (interactive sketch solving, certain GUI dialogs) are harder to drive programmatically. This is a scope risk, not a blocker.

**Disposition:** Accepted with risk — AMB-002 must bound scope to API-accessible features only.

## Challenge 4: What is the blast radius if the LLM generates bad Python?

**Finding:** If the LLM executes arbitrary Python inside FreeCAD, it could delete the active document, write to disk, or call any FreeCAD API destructively. This is a serious security and reliability risk.

**Disposition:** BLOCKING FINDING — AMB-009 must be resolved before Phase 1. Structured tool API (not raw Python exec) is strongly indicated. The design must include a safe execution boundary.

## Challenge 5: Is this buildable solo?

**Finding:** FreeCAD's codebase is large (C++ core + Python bindings + 20+ modules). Full coverage of all workbenches is not a solo MVP task. Scoping to a subset (e.g., Part + PartDesign + Sketcher) is viable.

**Disposition:** Accepted with scope constraint — AMB-002 resolution critical.

## Summary

| Finding | Severity | Status |
|---------|----------|--------|
| Problem is real | — | PASS |
| LLM is appropriate | — | PASS |
| API coverage risk | WARN | Deferred to AMB-002 resolution |
| Arbitrary Python execution risk | BLOCKING | Must resolve via AMB-009 before Phase 1 |
| Solo buildability | WARN | Requires bounded scope in AMB-002 |

**Overall A0 result:** CONDITIONAL PASS — blocking finding on execution safety must be resolved before Phase 1 exit.
