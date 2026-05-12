# Intake

## Verbatim Request (2026-05-12)

> "the task is to create the infrastructure to allow and llm interact with the software and must interact with all kind of features of the app, and helps the user in the design of pieces in a easy way"

## 5-Whys Trace

**Why** build LLM infrastructure for FreeCAD?
→ So an LLM can interact with all features of the app.

**Why** does the LLM need to interact with all features?
→ So it can help users design pieces easily.

**Why** can't users design pieces easily today?
→ FreeCAD has a steep learning curve; users must know which workbench, which tool, which parameter sequence to use.

**Why** is the learning curve steep?
→ The tool surface is large (Part, PartDesign, Sketcher, BIM, FEM, CAM, Draft, etc.); each workbench has its own paradigm; parametric modeling requires understanding constraint systems.

**Why** is that a problem worth solving with an LLM?
→ An LLM can translate intent ("make a 50mm cube with a 10mm hole through it") into the correct FreeCAD API call sequence, hiding complexity from the user.

**Root motivation:** Lower the skill floor for parametric CAD by exposing FreeCAD's Python API to an LLM agent that can receive natural-language design intent and execute it.

## Status
- [ ] Reviewed and approved by user
