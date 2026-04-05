"""Data models for parsed links."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LinkType(Enum):
    """Type of parsed link."""

    WIKILINK = "wikilink"
    WIKILINK_EMBED = "wikilink_embed"
    MARKDOWN_LINK = "markdown_link"
    MARKDOWN_EMBED = "markdown_embed"


@dataclass(frozen=True, slots=True)
class Link:
    """Structured representation of a parsed link."""

    type: LinkType
    target: str
    alias: str | None
    heading: str | None
    blockid: str | None
