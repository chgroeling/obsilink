"""Data models for parsed links."""

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
    """Structured representation of a parsed link."""

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
    def as_path(self) -> Path:
        """Return the target as a Path object.

        Raises:
            ValueError: If the target is a URL.
        """
        if self.is_url:
            msg = f"Cannot convert URL target to Path: {self.target!r}"
            raise ValueError(msg)
        return Path(self.target)
