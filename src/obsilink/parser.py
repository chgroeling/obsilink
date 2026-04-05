"""Obsidian and Markdown links extraction utilities."""

from __future__ import annotations

import re
from typing import Protocol

from .models import Link, LinkType


_WIKILINK_PATTERN = re.compile(r"(!?)\[\[([^\[\]\r\n]+?)\]\]")
_MARKDOWN_LINK_PATTERN = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")


class TextReadable(Protocol):
    """Protocol for readable text sources."""

    def read(self) -> str:
        """Return full text content as a string."""


class _MatchWithSource:
    """Holds a regex match and its source type for unified sorting."""

    __slots__ = ("start", "match", "source")

    def __init__(self, match: re.Match[str], source: str) -> None:
        self.start = match.start()
        self.match = match
        self.source = source


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


def _parse_wikilink(match: re.Match[str]) -> Link | None:
    start = match.start()
    text = match.string
    if start > 0 and _is_word_char(text[start - 1]):
        return None

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
        return None

    link_type = LinkType.WIKILINK_EMBED if embed else LinkType.WIKILINK

    return Link(
        type=link_type,
        target=note,
        alias=alias,
        heading=heading,
        blockid=blockid,
    )


def _parse_markdown_link(match: re.Match[str]) -> Link:
    embed = match.group(1) == "!"
    text = match.group(2)
    url = match.group(3)

    link_type = LinkType.MARKDOWN_EMBED if embed else LinkType.MARKDOWN_LINK
    alias = text if text else None

    return Link(
        type=link_type,
        target=url,
        alias=alias,
        heading=None,
        blockid=None,
    )


def extract_links(source: str | TextReadable) -> list[Link]:
    """Extract Obsidian wikilinks and Markdown links from text.

    Args:
        source: Raw text or a text file-like object with ``.read()``.

    Returns:
        list[Link]: Parsed links in encounter order.

    Raises:
        TypeError: If source is unsupported or ``.read()`` does not return ``str``.
    """

    text = _source_to_text(source)
    matches: list[_MatchWithSource] = []

    for m in _WIKILINK_PATTERN.finditer(text):
        matches.append(_MatchWithSource(m, "wikilink"))
    for m in _MARKDOWN_LINK_PATTERN.finditer(text):
        matches.append(_MatchWithSource(m, "markdown"))

    matches.sort(key=lambda x: x.start)

    links: list[Link] = []
    for item in matches:
        if item.source == "wikilink":
            link = _parse_wikilink(item.match)
        else:
            link = _parse_markdown_link(item.match)
        if link is not None:
            links.append(link)

    return links
