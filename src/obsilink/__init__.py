"""Public API for extracting links from Obsidian and Markdown text."""

from importlib.metadata import version

from .models import Link, LinkType
from .parser import extract_links
from .replacer import replace_links

__version__ = version("obsilink")

__all__ = ["Link", "LinkType", "__version__", "extract_links", "replace_links"]
