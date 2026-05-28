# Codex Goal Mode Guide

## Pattern

1. Start with `/plan` when the task is ambiguous.
2. Convert the plan to `/goal` when the objective and test command are clear.
3. Ask for compact progress reports: checkpoint, verified result, remaining work, blocker.
4. Keep one branch/worktree per P0 ticket.
5. Do not let a goal modify public claims, product scope, or architecture without updating source-of-truth docs.

## Good goal shape

```text
/goal Implement <specific feature>. Files likely affected: <paths>. Do not add product scope. Definition of done: <tests/commands>. Pause if <condition>.
```

## Required closing summary from Codex

```text
Changed files:
Tests run:
Verified behavior:
Evidence/logs:
Remaining risk:
Next recommended ticket:
```
