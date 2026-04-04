"""Wikilink extraction utilities."""

from __future__ import annotations

import re
from typing import Protocol


_WIKILINK_PATTERN = re.compile(r"(!?)\[\[([^\[\]\r\n]+?)\]\]")


class TextReadable(Protocol):
    """Protocol for readable text sources."""

    def read(self) -> str:
        """Return full text content as a string."""


def _source_to_text(source: str | TextReadable) -> str:
    if isinstance(source, str):
        return source

    read = getattr(source, "read", None)
    if not callable(read):
        msg = "source must be a str or a text file-like object with a .read() method"
        raise TypeError(msg)

    text = read()
    if not isinstance(text, str):
        msg = "source.read() must return a str"
        raise TypeError(msg)
    return text


def _is_word_char(char: str) -> bool:
    return char.isalnum() or char == "_"


def extract_obsidian_links(source: str | TextReadable) -> list[str]:
    """Extract Obsidian wikilink targets from text.

    Args:
        source: Raw text or a text file-like object with ``.read()``.

    Returns:
        list[str]: Wikilink targets in encounter order.

    Raises:
        TypeError: If source is unsupported or ``.read()`` does not return ``str``.
    """

    text = _source_to_text(source)
    links: list[str] = []

    for match in _WIKILINK_PATTERN.finditer(text):
        start = match.start()
        if start > 0 and _is_word_char(text[start - 1]):
            continue

        target_with_optional_alias = match.group(2)
        target, *_ = target_with_optional_alias.split("|", 1)
        if target:
            links.append(target)

    return links
