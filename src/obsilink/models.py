"""Data models for parsed Obsidian and Markdown links."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class LinkType(Enum):
    """Type of parsed link."""

    WIKILINK = "wikilink"
    WIKILINK_EMBED = "wikilink_embed"
    MARKDOWN_LINK = "markdown_link"
    MARKDOWN_EMBED = "markdown_embed"
    PLAIN_URL = "plain_url"


@dataclass(frozen=True, slots=True)
class Link:
    """Structured representation of a parsed link.

    Attributes:
        type: The kind of link (wikilink, embed, markdown, plain URL).
        target: The note name, file path, or URL without heading or block-id fragments.
        alias: Display text (e.g. ``[[Note|Alias]]`` → ``"Alias"``). ``None`` if not provided.
        heading: The heading fragment after ``#`` (e.g. ``[[Note#Section]]`` → ``"Section"``). ``None`` if absent.
        blockid: The block-id fragment after ``^`` (e.g. ``[[Note^abc123]]`` → ``"abc123"``). ``None`` if absent.
    """

    type: LinkType
    target: str
    alias: str | None
    heading: str | None
    blockid: str | None

    @property
    def is_url(self) -> bool:
        """Check if the target is a URL."""
        return bool(re.match(r"^(https?|ftp|file)://", self.target)) or bool(
            re.match(r"^mailto:", self.target)
        )

    @property
    def is_file(self) -> bool:
        """Check if the target is a file path."""
        return not self.is_url

    @property
    def as_path(self) -> Path:
        """Return the target as a Path object.

        Raises:
            ValueError: If the target is a URL.
        """
        if self.is_url:
            msg = f"Cannot convert URL target to Path: {self.target!r}"
            raise ValueError(msg)
        return Path(self.target)
