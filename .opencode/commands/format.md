---
description: Auto-format code to project standards
agent: build
---

Auto-format the codebase using the project's configured formatters.

1. Run code formatter (black, prettier, or similar)
2. Sort imports if applicable
3. Report what was changed
4. Verify no errors were introduced after formatting

This should fix style violations automatically without requiring manual review.
