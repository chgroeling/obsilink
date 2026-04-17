# obsilink

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)
[![PyPI](https://img.shields.io/pypi/v/obsilink.svg)](https://pypi.org/project/obsilink/)

`obsilink` is a small, deterministic Python library for extracting and replacing links in Markdown text.

It supports:

- Obsidian wikilinks like `[[Note]]`, `[[Note|Alias]]`, and `![[Embedded]]`
- Markdown links like `[Docs](https://example.com)` and embeds like `![Logo](logo.png)`
- Plain URLs like `https://example.com`, `ftp://files.example.com`, and `mailto:user@example.com`

The parser returns structured `Link` objects in encounter order and preserves duplicates.
Links can also be replaced in-place using structured `(old, new)` pairs.

## Features

- Deterministic parsing with stable ordering
- Two public functions: `extract_links(...)` and `replace_links(...)`
- Accepts either raw `str` or file-like input with `.read()`
- Preserves duplicates instead of deduplicating
- Strict, typed API compatible with `mypy` strict mode
- Links are split into structured fields (`target`, `alias`, `heading`, `blockid`) — heading (`#`) and block-id (`^`) fragments are extracted separately and never included in `target`

## Installation

### With uv (recommended)

```bash
uv add obsilink
```

### With pip

```bash
pip install obsilink
```

### From source

```bash
git clone https://github.com/chgroeling/obsilink.git
cd obsilink
uv sync
```

If the package is not yet published to your package index, use the source install method.

## Quick start

```python
from obsilink import extract_links

text = """
See [[Project/Plan#Milestones|Roadmap]],
![Logo](assets/logo.png),
and https://example.com.
"""

links = extract_links(text)

for link in links:
    print(link.type.value, link.target, link.alias)
```

### Replacing links

```python
from obsilink import Link, LinkType, replace_links

text = "See [[OldNote]] for details."

old = Link(type=LinkType.WIKILINK, target="OldNote", alias=None, heading=None, blockid=None)
new = Link(type=LinkType.WIKILINK, target="NewNote", alias=None, heading=None, blockid=None)

result_text, applied = replace_links(text, [(old, new)])
print(result_text)   # See [[NewNote]] for details.
print(applied)       # [True]
```

### More complex Obsidian wikilink example

```python
from obsilink import extract_links

text = """
[[Project/Plan#Milestones|Roadmap]]
![[Assets/Diagrams/System Overview#v2]]
[[People/Ada Lovelace#Biography^early-life|Ada]]
[[Project/Plan#Milestones|Roadmap]]
[[Malformed
"""

links = extract_links(text)

for link in links:
    print(
        link.type.value,
        link.target,
        link.alias,
        link.heading,
        link.blockid,
    )

# Encounter order is preserved, duplicates are kept, and malformed
# wikilinks (like "[[Malformed") are ignored.
```

## API

### `extract_links(source)`

Extracts links from:

- `str`
- text file-like object with `.read()` returning `str`

Returns:

- `list[Link]` in encounter order

Raises:

- `TypeError` for unsupported source types
- `TypeError` if `.read()` returns non-string data
- Any exception raised by `.read()` is propagated

### `replace_links(source, replacements)`

Replaces links in text based on a list of `(old_link, new_link)` pairs.

Accepts:

- `source`: `str` or text file-like object with `.read()` returning `str`
- `replacements`: `list[tuple[Link, Link]]`

Returns:

- `tuple[str, list[bool]]` — the modified text and a boolean per pair indicating whether the replacement was applied

Replacements are applied sequentially; each pair replaces only the first occurrence.

Raises:

- `TypeError` for unsupported source types
- `TypeError` if `.read()` returns non-string data
- Any exception raised by `.read()` is propagated

### `Link`

`Link` is a frozen dataclass with these fields:

- `type: LinkType`
- `target: str`
- `alias: str | None`
- `heading: str | None`
- `blockid: str | None`

Convenience properties:

- `link.is_url` -> `True` for URL targets (`http`, `https`, `ftp`, `file`, `mailto`)
- `link.as_path` -> `pathlib.Path` for non-URL targets (raises `ValueError` for URLs)

## Supported link types

- `LinkType.WIKILINK`
- `LinkType.WIKILINK_EMBED`
- `LinkType.MARKDOWN_LINK`
- `LinkType.MARKDOWN_EMBED`
- `LinkType.PLAIN_URL`

## How links are split

Each link is split into its constituent parts. The `target` field
contains only the note, path, or URL — heading (`#`) and block-id (`^`) fragments are
extracted into their own fields and are **not** included in `target`.

### Obsidian wikilinks

| Input                             | `target`      | `alias`   | `heading` | `blockid` |
| --------------------------------- | ------------- | --------- | --------- | --------- |
| `[[Note]]`                        | `Note`        | `None`    | `None`    | `None`    |
| `[[Note\|Alias]]`                 | `Note`        | `Alias`   | `None`    | `None`    |
| `[[Folder/Note#Heading]]`         | `Folder/Note` | `None`    | `Heading` | `None`    |
| `[[Note^abc123]]`                 | `Note`        | `None`    | `None`    | `abc123`  |
| `[[Note#Section^block\|Display]]` | `Note`        | `Display` | `Section` | `block`   |
| `![[Embedded]]`                   | `Embedded`    | `None`    | `None`    | `None`    |

### Markdown links

For Markdown links, `heading` and `blockid` are always `None`. The `target` is the URL or path inside parentheses, and `alias` is the link text inside brackets.

| Input                         | `target`              | `alias` | `heading` | `blockid` |
| ----------------------------- | --------------------- | ------- | --------- | --------- |
| `[Docs](https://example.com)` | `https://example.com` | `Docs`  | `None`    | `None`    |
| `![Logo](assets/logo.png)`    | `assets/logo.png`     | `Logo`  | `None`    | `None`    |
| `[](relative/path.md)`        | `relative/path.md`    | `None`  | `None`    | `None`    |

## Development

This project uses `uv`, `ruff`, `mypy`, and `pytest`.

```bash
uv sync
uv run ruff format src/ tests/
uv run ruff check src/ tests/
uv run mypy src/
uv run pytest
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
