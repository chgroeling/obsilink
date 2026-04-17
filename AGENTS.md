# AGENTS.md

## Project description
This project provides a small, deterministic Python library for extracting and replacing
links in Markdown text. It supports Obsidian wikilinks, standard Markdown links, and plain URLs.

## Core behavior

### Extraction (`extract_links`)
- Parse Obsidian wikilinks (`[[Note]]`, `[[Note|Alias]]`, `![[Embed]]`), Markdown links
  (`[text](url)`), Markdown embeds (`![alt](path)`), and plain URLs.
- Return structured `Link` objects (`list[Link]`) in encounter order.
- Preserve duplicates.
- Ignore malformed or partial syntax.
- Accept input as `str` or a text file-like object with `.read()` returning `str`.
- Raise `TypeError` for unsupported input types or if `.read()` returns non-string data.
- Propagate exceptions raised by `.read()`.

### Replacement (`replace_links`)
- Accept a source text and a list of `(old_link, new_link)` pairs.
- Replace the first occurrence of each old link sequentially.
- Return the modified text and a list of booleans indicating which replacements were applied.
- Same input type rules as extraction (`str` or file-like).

## Scope boundaries
- This repository covers link extraction and replacement only.
- Do not add filesystem resolution features (depth traversal, basename/path searching).
- Do not add CLI/machine-output formatting concerns.
- Do not rely on environment variables such as `PROJECT_DIR` in parser code.

## API guidelines
- Keep the public API small and predictable.
- Public entry points:
  - `extract_links(source: str | TextReadable) -> list[Link]`
  - `replace_links(source: str | TextReadable, replacements: list[tuple[Link, Link]]) -> tuple[str, list[bool]]`
- Core data model: `Link` (frozen dataclass) and `LinkType` (enum).
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
