---
description: Review changes, update GitHub workflows, commit separately, and push
agent: build
---

Review the current branch changes and complete this sequence in order.

Additional context, if provided: $ARGUMENTS

1. Read the current worktree first.
- Run `git status` and inspect staged and unstaged diffs before editing anything.
- Identify the logical change groups and decide whether `.github/workflows/` needs to change to support the current work.

2. Update GitHub workflows.
- Inspect `.github/workflows/` and make the minimal CI changes required by the current code, tests, or tooling changes.
- Keep workflow edits separate from application, docs, and test changes when possible.
- If no workflow update is actually needed, say that clearly and skip a workflow-only commit.

3. Commit with separate messages.
- Stage and commit each logical change group separately.
- Use distinct, concise commit messages that explain why each commit exists.
- Prefer a dedicated commit for workflow changes and one or more additional commits for the remaining work.
- Never commit secrets or unrelated generated files.

4. Push to remote.
- Push the current branch to its tracked remote.
- If the branch has no upstream, push with `-u origin <branch>`.

Rules:
- Follow `AGENTS.md`.
- Do not rewrite or squash existing commits unless I explicitly ask.
- Do not revert unrelated local changes.
- Show the commit messages used and the final push result.
