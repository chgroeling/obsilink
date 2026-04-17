"""Public API for extracting links from Obsidian and Markdown text."""

from importlib.metadata import version

from .extractor import extract_links
from .models import Link, LinkType
from .replacer import replace_links

__version__ = version("obsilink")

__all__ = ["Link", "LinkType", "__version__", "extract_links", "replace_links"]
