# Repository Guidelines

## Project Structure & Module Organization

This repository currently contains only Codex/Claude configuration and skill assets. Key paths:

- `.claude/agents/` ? agent prompt templates (example: `simple-demo.md`).
- `.claude/skills/` ? local skills (each skill has a `SKILL.md`).
- `.claude/settings.json` ? local agent settings.

If application code is added later, document where source, tests, and assets live (for example, `src/`, `tests/`, `assets/`).

## Build, Test, and Development Commands

No build or test tooling is defined yet (no package manifests or scripts found). When you add tooling, list the exact commands here and what they do (for example, `npm run dev`, `pytest`, or `make build`).

## Coding Style & Naming Conventions

No formatter, linter, or style guide is configured. Follow existing file conventions in this repo:

- Prefer ASCII text and concise Markdown.
- Name files descriptively (e.g., `SKILL.md`, `simple-demo.md`).
- Keep directory names lowercase and single-purpose.

If you introduce a language toolchain, add the formatter/linter commands and naming rules here.

## Testing Guidelines

No test framework is present. If you add tests, standardize on a single location and naming pattern and document how to run them (for example, `tests/` with `test_*.py` or `__tests__/` with `*.test.ts`).

## Commit & Pull Request Guidelines

This directory is not a Git repository yet, so no history-based conventions exist. Before first commit, agree on:

- Commit message format (for example, `type: short description`).
- PR requirements (summary, motivation, test evidence, and linked issues if applicable).

## Security & Configuration Tips

Avoid storing secrets in `.claude/skills/` or agent templates. Use environment variables or local, uncommitted config files for sensitive values.
