# OpenCode Commands for urban-garbanzo

This directory contains reusable OpenCode prompts and configuration for the urban-garbanzo project.

## Quick Start

All commands are available via the `/` prefix in OpenCode TUI. For example:

```
/init-project     # Bootstrap the project structure
/setup-dev        # Set up development environment
/test             # Run tests with coverage
/lint             # Check code quality
/format           # Auto-format code
/feature          # Plan a new feature
/review           # Review code quality
/explain          # Explain how code works
/debug            # Investigate and fix bugs
```

## Commands Overview

| Command | Purpose | Use When |
|---------|---------|----------|
| `init-project` | Bootstrap initial project structure | Starting the project from scratch |
| `setup-dev` | Set up local dev environment | First time setup or debugging env issues |
| `test` | Run tests with coverage | Before commits or to verify fixes |
| `lint` | Check code quality and style | Reviewing code quality |
| `format` | Auto-format code | Fixing style violations |
| `feature` | Plan a new feature | Planning architecture before building |
| `review` | Review code for best practices | Before merge or during code review |
| `explain` | Explain how code works | Understanding unfamiliar parts |
| `debug` | Investigate and fix bugs | Fixing issues or creating bug fixes |

## Structure

- `commands/` - Reusable prompt templates for common tasks
- `opencode.json` - Central config (in project root) that loads these commands

## Configuration

The project uses:
- **Instruction file**: `AGENTS.md` - Contains project-specific guidance
- **Config schema**: `opencode.json` - Defines commands and settings

## Extending

To add a new command:

1. Create a markdown file in `.opencode/commands/your-command.md`
2. Add YAML frontmatter with `description`, and optionally `agent`, `subtask`, `model`
3. Write the prompt template using `$ARGUMENTS` for user input or `$1`, `$2` for positional args
4. The command becomes available via `/your-command` immediately

Example:

```markdown
---
description: Do something useful
agent: build
---

Here's what I want you to do: $ARGUMENTS
```

Then in OpenCode TUI: `/your-command my request here`
