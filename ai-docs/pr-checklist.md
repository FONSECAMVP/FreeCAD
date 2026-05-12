# AI Addon — PR Self-Review Checklist

Used for every PR on `feat/ai-addon` → `main`. Complete before requesting merge.

---

## Required PR body fields

Fill these in the PR description (augments FreeCAD's default PR template):

```
## AI Addon — Change Summary
**Change:** [what changed in one sentence]
**Why:** [REQ/DEC/issue motivation]
**REQ/DEC IDs touched:** REQ-NNN, DEC-NNN, ...
**Test approach:** [unit / integration / manual — which tests cover this]
**Risk:** [low / medium / high — blast radius if something is wrong]
**Rollback plan:** [revert commit SHA; no doc changes needed / ...]
```

---

## Self-review checklist

### Code
- [ ] All changed files pass `pre-commit run` (ruff, mypy, exec/eval gate, fast tests)
- [ ] `python3 -m pytest tests/ -q` — 0 failures
- [ ] No `exec(` or `eval(` in `freecad_ai/` source
- [ ] No API key or credential in any changed file
- [ ] No new imports at module top-level in tool files (lazy import rule — REQ-019)

### Traceability
- [ ] Every new/changed REQ has ≥1 test
- [ ] `traceability.md` updated with commit SHA for touched REQs
- [ ] `decisions.md` updated if any DEC was revisited or added

### CLV
- [ ] CLV pass run (`validations/validation-NNN.md` created)
- [ ] No FAIL in CLV output

### PR mechanics
- [ ] Branch is up to date with `main` (rebased or merged)
- [ ] Commit messages cite REQ/TEST/DEC IDs
- [ ] PR targets `main` (not another feature branch)
- [ ] "Allow edits by maintainers" enabled (FreeCAD convention)
