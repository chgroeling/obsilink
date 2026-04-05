"""Link extraction from text sources.

Supports extraction of Obsidian wikilinks (e.g., ``[[Note]]``, ``[[Note|Alias]]``),
Markdown links, and plain URLs from input text or file-like objects.
"""

from __future__ import annotations

import re
from typing import Protocol

from .models import Link, LinkType


_WIKILINK_PATTERN = re.compile(r"(!?)\[\[([^\[\]\r\n]+?)\]\]")
_MARKDOWN_LINK_PATTERN = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
_PLAIN_URL_PATTERN = re.compile(
    r"((https?|ftp|file)://|mailto:)\b([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"
)


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


def _parse_plain_url(match: re.Match[str]) -> Link:
    url = match.group(0)
    return Link(
        type=LinkType.PLAIN_URL,
        target=url,
        alias=None,
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
    for m in _PLAIN_URL_PATTERN.finditer(text):
        matches.append(_MatchWithSource(m, "plain_url"))

    matches.sort(key=lambda x: x.start)

    links: list[Link] = []
    skip_ranges: list[tuple[int, int]] = []

    for item in matches:
        start, end = item.match.start(), item.match.end()
        for skip_start, skip_end in skip_ranges:
            if skip_start <= start < skip_end:
                break
        else:
            if item.source == "wikilink":
                link = _parse_wikilink(item.match)
            elif item.source == "markdown":
                link = _parse_markdown_link(item.match)
            else:
                link = _parse_plain_url(item.match)
            if link is not None:
                links.append(link)
                if item.source in ("wikilink", "markdown"):
                    skip_ranges.append((start, end))

    return links
