"""Public API for extracting links from Obsidian and Markdown text."""

from .models import Link, LinkType
from .parser import extract_links

__all__ = ["Link", "LinkType", "extract_links"]
