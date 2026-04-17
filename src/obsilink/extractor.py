"""Link extraction from text sources.

Supports extraction of Obsidian wikilinks (e.g., ``[[Note]]``, ``[[Note|Alias]]``),
Markdown links, and plain URLs from input text or file-like objects.
"""

from __future__ import annotations

import heapq
import re
from typing import Protocol

from .models import Link, LinkType

_WIKILINK_PATTERN = re.compile(r"(!?)\[\[([^\[\]\r\n]+?)\]\]")
_MARKDOWN_LINK_PATTERN = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
_PLAIN_URL_PATTERN = re.compile(
    r"((https?|ftp|file)://|mailto:)\b([-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))"
)

# Source-type tags for fast integer comparison in the merge loop.
_TAG_WIKILINK = 0
_TAG_MARKDOWN = 1
_TAG_PLAIN_URL = 2


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
    """Extract Obsidian wikilinks, Markdown links, and plain URLs from text.

    Parses the input source and returns structured ``Link`` objects for each
    match found. Supports:

    - Obsidian wikilinks: ``[[Note]]``, ``[[Note|Alias]]``, ``[[Note#Heading]]``, ``[[Note^block]]``
    - Wikilink embeds: ``![[Note]]``
    - Markdown links: ``[text](url)``
    - Markdown embeds: ``![alt](url)``
    - Plain URLs: standalone ``https://``, ``http://``, ``ftp://``, ``file://``, and ``mailto:`` links

    Links are returned in encounter order. Duplicates are preserved. Malformed
    or partial syntax is silently ignored. Embed targets (``![[...]]`` and
    ``![...](...)``) are included by default.

    Each ``Link`` is split into its constituent parts — the ``target`` field
    contains only the note/path/URL, while heading (``#``) and block-id (``^``)
    fragments are extracted into separate fields.

    Args:
        source: Raw text (``str``) or a text file-like object with a ``.read()``
            method that returns ``str``.

    Returns:
        A list of ``Link`` objects in the order they appear in the source.

    Raises:
        TypeError: If ``source`` is not a ``str`` or a file-like object with
            a callable ``.read()`` method.
        TypeError: If ``.read()`` does not return a ``str``.
    """

    text = _source_to_text(source)

    # Each finditer yields matches in start-position order, so heapq.merge
    # produces a single sorted stream in O(n) without materialising lists.
    merged = heapq.merge(
        ((m.start(), _TAG_WIKILINK, m) for m in _WIKILINK_PATTERN.finditer(text)),
        ((m.start(), _TAG_MARKDOWN, m) for m in _MARKDOWN_LINK_PATTERN.finditer(text)),
        ((m.start(), _TAG_PLAIN_URL, m) for m in _PLAIN_URL_PATTERN.finditer(text)),
    )

    links: list[Link] = []
    skip_until = 0  # high-water mark: skip anything starting before this offset

    for start, tag, match in merged:
        if start < skip_until:
            continue
        if tag == _TAG_WIKILINK:
            link = _parse_wikilink(match)
        elif tag == _TAG_MARKDOWN:
            link = _parse_markdown_link(match)
        else:
            link = _parse_plain_url(match)
        if link is not None:
            links.append(link)
            if tag != _TAG_PLAIN_URL:
                skip_until = match.end()

    return links
