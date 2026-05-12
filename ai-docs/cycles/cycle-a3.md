# Adversarial Cycle A3 — Test Hardening

Date: 2026-05-12

## Mutation targets covered

| Area | Test | Finding |
|------|------|---------|
| Registry dispatch | unknown tool never raises | PASS |
| Registry handler exception | absorbed by executor, never propagates raw | PASS |
| Executor string validation | 7 invalid patterns parametrized | BUG FOUND: space-only " " passed regex — fixed |
| Executor string validation | 6 valid patterns at boundary | PASS |
| Executor required arg missing | validation error with field name | PASS |
| Executor wrong type arg | validation error | PASS |
| Executor busy flag | dispatch blocked when busy | PASS |
| Executor transaction abort | abortTransaction called, commitTransaction not | PASS |
| Conversation system message | never dropped under truncation | PASS |
| Conversation truncation | never exceeds max_tokens at 200 messages | PASS |
| Context cap | 25 objects → only 20 in output | PASS |
| Context length | 20 long-label objects → ≤500 chars | PASS |
| No exec/eval | grep all source files | PASS |
| LLM client empty tools | sends None not [] | PASS |
| LLM client with tools | list forwarded correctly | PASS |

## Bug fixed

**A3-BUG-001:** `_validate_string_arg` in `executor.py` used `[\w\s\-]{1,128}` regex.
`\s` matches space, so `" "` (space-only) passed validation. Added `value.strip()` empty
check before regex. Fix: `executor.py:_validate_string_arg`.

## Summary

15 hardening tests added. 1 real bug caught and fixed. All 134 tests pass.
No surviving mutation targets in executor string validation, transaction handling,
or conversation truncation.
