---
name: write-tests
description: Write or extend pytest tests for code changes. Tests live in test/, and use fake models so they run without a local Ollama.
allowed-tools: [read_file, glob]
---

# Write Tests

Use this skill when adding tests for a change.

1. Add or extend `test/test_<module>.py`.
2. Cover the normal path, the error/reject path, and "gating disabled" paths.
3. Prefer fake models (`GenericFakeChatModel` subclass with `bind_tools`)
   so tests run without Ollama; see `test/test_hitl.py`.
4. Run: `uv run pytest -q`.
