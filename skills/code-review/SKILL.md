---
name: code-review
description: "Review a code change (diff or file) before it merges or commits: correctness, style, edge cases, test coverage."
allowed-tools: [read_file, grep, glob]
---

# Code Review

Use this skill when asked to review code or a diff.

1. Read the change: `git diff` output or the given file(s).
2. Correctness — does the change do what it claims? Check edge cases
   (empty input, missing files, error paths).
3. Style — does it match project conventions? (AGENTS.md)
4. Tests — is new or changed behavior covered by tests?
5. Report findings as a short list: `[blocker]`, `[nit]`, or `[suggestion]`.
