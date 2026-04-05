"""Public package API for obsilink."""

from .models import Link, LinkType
from .parser import extract_links

__all__ = ["Link", "LinkType", "extract_links"]
