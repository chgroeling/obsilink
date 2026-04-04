"""Obsidian links extraction utilities."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Protocol


_WIKILINK_PATTERN = re.compile(r"(!?)\[\[([^\[\]\r\n]+?)\]\]")


class TextReadable(Protocol):
    """Protocol for readable text sources."""

    def read(self) -> str:
        """Return full text content as a string."""


@dataclass(frozen=True, slots=True)
class Link:
    """Structured representation of a parsed Obsidian wikilink."""

    note: str
    alias: str | None
    heading: str | None
    blockid: str | None
    embed: bool


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


def extract_obsidian_links(source: str | TextReadable) -> list[Link]:
    """Extract Obsidian wikilink targets from text.

    Args:
        source: Raw text or a text file-like object with ``.read()``.

    Returns:
        list[Link]: Parsed wikilinks in encounter order.

    Raises:
        TypeError: If source is unsupported or ``.read()`` does not return ``str``.
    """

    text = _source_to_text(source)
    links: list[Link] = []

    for match in _WIKILINK_PATTERN.finditer(text):
        start = match.start()
        if start > 0 and _is_word_char(text[start - 1]):
            continue

        embed = match.group(1) == "!"
        link_text = match.group(2)

        target_part: str
        alias: str | None
        if "|" in link_text:
            target_part, alias = link_text.split("|", 1)
        else:
            target_part = link_text
            alias = None

        target_base = target_part
        blockid: str | None = None
        if "^" in target_base:
            target_base, blockid = target_base.rsplit("^", 1)

        note = target_base
        heading: str | None = None
        if "#" in note:
            note, heading = note.split("#", 1)

        if not note:
            continue

        links.append(
            Link(
                note=note,
                alias=alias,
                heading=heading,
                blockid=blockid,
                embed=embed,
            )
        )

    return links
