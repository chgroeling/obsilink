# AGENTS.md

## Project description
This project provides a small, deterministic Python library that extracts Obsidian-style
wikilink targets from input text.

## Core behavior
- Parse Obsidian links such as `[[Note]]`, `[[Note|Alias]]`, and `[[Folder/Note#Heading]]`.
- Accept input as either:
  - `str`
  - a text file-like object with a `.read()` method that returns `str`
- Return `list[str]` in encounter order.
- Preserve duplicates.
- Ignore malformed or partial wikilink syntax.
- Include embed targets (for example `![[Note]]`) by default.
- Raise `TypeError` for unsupported input types.
- Propagate exceptions raised by `.read()`.
- Raise `TypeError` if `.read()` returns non-string data.

## Scope boundaries
- This repository is extraction/parsing only.
- Do not add filesystem resolution features (depth traversal, basename/path searching).
- Do not add CLI/machine-output formatting concerns.
- Do not rely on environment variables such as `PROJECT_DIR` in parser code.

## API guidelines
- Keep the public API small and predictable.
- Main entry point:
  - `extract_obsidian_links(source: str | TextIO) -> list[str]`
- Optional extension point (if needed): `include_embeds: bool = True`.
- Validate input types and provide clear error messages.

## Non-goals
Do not implement the following in this library:
- recursive graph traversal (`depth`, BFS/DFS)
- file discovery by basename/path
- path escaping for shell/xargs
- CLI machine-output payloads
- `PROJECT_DIR` or other environment-based resolution

## Development workflows

### Environment and dependencies
- Sync: `uv sync`
- Update lockfile: `uv lock --upgrade`
- Add/remove packages: `uv add <pkg>`, `uv remove <pkg>`

### QA checks
Prefix commands with `uv run`.
- Format: `ruff format src/ tests/`
- Lint: `ruff check src/ tests/`
- Types: `mypy src/`
- Tests: `pytest`
- Full gate:
  `uv run ruff format src/ tests/ && uv run ruff check src/ tests/ && uv run mypy src/ && uv run pytest`

### Standards
- Follow SemVer (`MAJOR.MINOR.PATCH`).
- Use Conventional Commits (`feat:`, `fix:`, `chore:`, etc.).
- Never commit autonomously; only commit when explicitly requested.

## Coding standards
- Keep behavior deterministic and side-effect free.
- Use strict typing for `src/` and maintain `mypy` compatibility.
- Keep line length at 100 characters (`ruff` configuration).
- Prefer testing through the public API; avoid testing private symbols.
- Keep imports at module top level (no inline imports in tests).
