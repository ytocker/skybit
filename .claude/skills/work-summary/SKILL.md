---
name: work-summary
description: >-
  Produce a structured work-summary Markdown document for a finished effort —
  what shipped, how it works, files touched, tests, and follow-ups. Use after
  completing a significant multi-commit feature or fix, or whenever the user asks
  to "summarize / recap / write up / document the work we did." Gathers the
  effort's commits + diff and writes a durable doc under docs/work-summaries/.
  Does NOT commit or push unless the user asks.
---

# Work Summary — generate a structured write-up of a finished effort

Turn a completed body of work into one durable Markdown document that a teammate
(or future-you) can read to understand **what** was built, **why**, **how**, and
**what's left**. Mirrors the tone and depth of `docs/achievements/README.md`.

## When to run
- After a significant multi-commit effort (a feature, system, or sizeable fix).
- Whenever the user asks to summarize / recap / document / write up the work.
- Trivial one-off changes don't need this — skip for typo/one-liner work.

## Scope — figure out what to summarize first
Determine the commit range for the effort (read-only git):
1. If the user names a base ref or range, use it.
2. Else default to the current branch's commits vs its base (e.g.
   `git log --oneline main..HEAD` — try the project's default branch; for Skybit
   the deployment base is `main`/`v5_skybit`), and confirm the span looks right.
3. Gather context with `git log` (messages) and `git diff --stat <base>..HEAD`
   (files + churn). Read key changed files as needed for the "how it works" depth.
4. If the span is ambiguous (long-lived branch, mixed efforts), ask the user which
   range / which feature to summarize before writing.

## Output
- Path: `docs/work-summaries/<YYYY-MM-DD>-<slug>.md` (slug = short kebab name of
  the effort, e.g. `2026-06-20-achievements`). Confirm/adjust the slug with the
  user; let them override the path.
- Create `docs/work-summaries/` if it doesn't exist.
- Match the repo's doc voice: clear, skimmable, WHY-focused, tables where they help.

## Required sections (template)
```
# <Effort name>

## Overview
One short paragraph: what this is and why it was done (the problem / intended outcome).

## What shipped
The user-facing result — bullet the capabilities/behaviour a player or user now gets.

## How it works
Architecture: the key modules/files and the data/control flow. Name the important
functions and how they connect. Keep it to what a maintainer needs.

## Files touched
A table or list of the files added/changed and a one-line role for each.

## Key decisions
The notable design choices and their rationale (and any rejected alternatives worth recording).

## Tests & verification
What proves it works — tests added/run (with counts/results), manual/headless checks,
both-build-target notes if relevant.

## Follow-ups / open items
Anything deferred, tunable, or worth doing next.

## Commits
The commit list for the effort (short SHAs + subjects) and, when useful, GitHub blob
links to the main artifacts on the working branch.
```
Drop a section only if it genuinely doesn't apply; don't pad.

## Repo rules to respect
- **Do not commit or push** unless the user explicitly asks (follow the global git
  policy). Just write the file and hand back its path.
- **Share visuals as git links only** — reference images by their GitHub blob URL
  on the working branch; never embed images in chat.
- Comments/prose stay WHY-focused; don't restate every line of the diff.
- `.claude/` and `docs/` are out of the pygbag bundle, so this adds no runtime or
  build weight.

## Finish
After writing, tell the user the file path (and its GitHub blob URL on the current
branch), and offer to commit/push it if they want it persisted to the remote.
