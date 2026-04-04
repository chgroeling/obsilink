# AGENTS.md

## Project description
This project provides a small, deterministic Python library that extracts Obsidian-style wikilink targets from input text.
It accepts either a plain string or a text file-like object and returns extracted note targets.

## Core behavior
- Parse Obsidian links (for example: `[[Note]]`, `[[Note|Alias]]`, `[[Folder/Note#Heading]]`).
- Accept input as either:
  - `str`
  - text file-like object (any object with `.read()` that returns `str`)
- Return `list[str]` containing discovered links in input order.
- Preserve duplicate links in parser output.
- Keep behavior deterministic and side-effect free.
- Ignore malformed/partial wikilink syntax.
- Include embed targets (for example: `![[Note]]`) by default.
- For unsupported input types, raise `TypeError` with a clear error message.
- If `.read()` raises, propagate the underlying exception.
- If `.read()` returns non-string data, raise `TypeError`.

## Scope boundaries
- This repo is for parsing/extraction only.
- Do not add filesystem resolution features (depth traversal, basename/path searching).
- Do not add CLI/machine-output formatting concerns here.
- Do not depend on environment variables such as `PROJECT_DIR` in core parser code.

## Development workflows

### Environment and dependencies
- **Sync/install:** `uv sync`.
- **Add package:** `uv add <pkg>` (use `--dev` for development-only dependencies).
- **Remove package:** `uv remove <pkg>`.
- **Run tools:** prefix with `uv run`.

### Quality checks
- **Format:** `uv run ruff format src/ tests/`
- **Lint:** `uv run ruff check src/ tests/`
- **Types:** `uv run mypy src/`
- **Tests:** `uv run pytest`

### Pre-commit gate
- `uv run ruff format src/ tests/ && uv run ruff check src/ tests/ && uv run mypy src/ && uv run pytest`

## Coding standards
- Prefer explicit type hints for all public functions.
- Keep imports ordered: stdlib -> third-party -> local.
- Remove unused imports immediately.
- Use `pathlib` over `os` where possible.
- Keep functions focused and test behavior through public APIs.
- Avoid inline imports inside tests.

## API guidelines
- Public API should stay small and predictable.
- Recommended main entry point:
  - `extract_obsidian_links(source: str | TextIO) -> list[str]`
- Optional extension point (if needed): embed inclusion toggle (e.g., `include_embeds: bool = True`).
- Accept broad file-like inputs through protocol-style typing when practical.
- Validate input types and raise clear errors for unsupported inputs.

## Testing guidelines
- Add unit tests for each supported link shape and edge case.
- Cover both input modes: raw `str` and file-like object.
- Verify order preservation and duplicate-handling behavior.
- Include negative tests for malformed or partial link syntax.
- Include tests for embed link handling behavior.
- Include tests for input validation and read-related error handling.

## Non-goals
Do not implement the following in this library:
- recursive graph traversal (`depth`, BFS/DFS/dir modes)
- file discovery by basename/path
- path escaping for shell/xargs
- CLI machine output payloads
- `PROJECT_DIR`/environment-based resolution

## Documentation guidelines
- Use concise docstrings in Google style for public APIs.
- Keep examples executable and aligned with actual behavior.
- Update docs whenever parsing rules or return contract changes.

## Git and release conventions
- Follow Conventional Commits (for example: `feat:`, `fix:`, `chore:`).
- Follow SemVer for versioning.
- Never commit autonomously; only commit when explicitly requested.
