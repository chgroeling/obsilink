"""Replace Obsidian and Markdown links in text."""

from __future__ import annotations

from .extractor import TextReadable, _source_to_text
from .models import Link, LinkType


def _link_to_text(link: Link) -> str:
    """Reconstruct the text representation of a Link."""
    if link.type in (LinkType.WIKILINK, LinkType.WIKILINK_EMBED):
        prefix = "!" if link.type == LinkType.WIKILINK_EMBED else ""
        inner = link.target
        if link.heading is not None:
            inner += f"#{link.heading}"
        if link.blockid is not None:
            inner += f"^{link.blockid}"
        if link.alias is not None:
            inner += f"|{link.alias}"
        return f"{prefix}[[{inner}]]"

    if link.type in (LinkType.MARKDOWN_LINK, LinkType.MARKDOWN_EMBED):
        prefix = "!" if link.type == LinkType.MARKDOWN_EMBED else ""
        display = link.alias or ""
        return f"{prefix}[{display}]({link.target})"

    # PLAIN_URL
    return link.target


def replace_links(
    source: str | TextReadable,
    replacements: list[tuple[Link, Link]],
) -> tuple[str, list[bool]]:
    """Replace links in text based on a list of (old_link, new_link) pairs.

    For each pair, the first occurrence of the old link's text form in the
    (progressively modified) source is replaced with the new link's text form.
    Replacements are applied sequentially.

    Args:
        source: Raw text (``str``) or a text file-like object with a ``.read()``
            method that returns ``str``.
        replacements: A list of ``(old_link, new_link)`` tuples. Each *old_link*
            is searched for in the text and, if found, replaced by *new_link*.

    Returns:
        A tuple of the modified text and a list of booleans. Each boolean
        indicates whether the corresponding replacement was found and applied.

    Raises:
        TypeError: If ``source`` is not a ``str`` or a file-like object with
            a callable ``.read()`` method.
        TypeError: If ``.read()`` does not return a ``str``.
    """
    text = _source_to_text(source)
    results: list[bool] = []

    for old_link, new_link in replacements:
        old_text = _link_to_text(old_link)
        new_text = _link_to_text(new_link)

        if old_text in text:
            text = text.replace(old_text, new_text, 1)
            results.append(True)
        else:
            results.append(False)

    return text, results
