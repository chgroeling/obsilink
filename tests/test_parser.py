from __future__ import annotations

from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from obsilink import Link, LinkType, extract_links


def test_extracts_basic_note_links() -> None:
    text = "See [[Note]] and [[Another Note]]"
    assert extract_links(text) == [
        Link(type=LinkType.WIKILINK, target="Note", alias=None, heading=None, blockid=None),
        Link(type=LinkType.WIKILINK, target="Another Note", alias=None, heading=None, blockid=None),
    ]


def test_extracts_alias_links() -> None:
    text = "Use [[Note|Alias]] and [[Folder/Note#Heading|Display]]"
    assert extract_links(text) == [
        Link(type=LinkType.WIKILINK, target="Note", alias="Alias", heading=None, blockid=None),
        Link(
            type=LinkType.WIKILINK,
            target="Folder/Note",
            alias="Display",
            heading="Heading",
            blockid=None,
        ),
    ]


def test_extracts_heading_links() -> None:
    text = "[[Note#Heading]]"
    assert extract_links(text) == [
        Link(type=LinkType.WIKILINK, target="Note", alias=None, heading="Heading", blockid=None)
    ]


def test_extracts_blockid_links() -> None:
    text = "[[Note^blockid]]"
    assert extract_links(text) == [
        Link(type=LinkType.WIKILINK, target="Note", alias=None, heading=None, blockid="blockid")
    ]


def test_extracts_heading_and_blockid_links() -> None:
    text = "[[Note#Heading^blockid]]"
    assert extract_links(text) == [
        Link(
            type=LinkType.WIKILINK, target="Note", alias=None, heading="Heading", blockid="blockid"
        )
    ]


def test_includes_wikilink_embed_targets() -> None:
    text = "Embed ![[Diagram]] and normal [[Note]]"
    assert extract_links(text) == [
        Link(
            type=LinkType.WIKILINK_EMBED, target="Diagram", alias=None, heading=None, blockid=None
        ),
        Link(type=LinkType.WIKILINK, target="Note", alias=None, heading=None, blockid=None),
    ]


def test_ignores_malformed_or_partial_syntax() -> None:
    text = "[[Unclosed and Not[[Link]] and ]][["
    assert extract_links(text) == []


def test_preserves_duplicates_and_order() -> None:
    text = "[[A]] [[B]] [[A]] [[C]] [[B]]"
    assert extract_links(text) == [
        Link(type=LinkType.WIKILINK, target="A", alias=None, heading=None, blockid=None),
        Link(type=LinkType.WIKILINK, target="B", alias=None, heading=None, blockid=None),
        Link(type=LinkType.WIKILINK, target="A", alias=None, heading=None, blockid=None),
        Link(type=LinkType.WIKILINK, target="C", alias=None, heading=None, blockid=None),
        Link(type=LinkType.WIKILINK, target="B", alias=None, heading=None, blockid=None),
    ]


def test_accepts_text_file_like_input() -> None:
    source = StringIO("[[FileLike]] [[Second]]")
    assert extract_links(source) == [
        Link(type=LinkType.WIKILINK, target="FileLike", alias=None, heading=None, blockid=None),
        Link(type=LinkType.WIKILINK, target="Second", alias=None, heading=None, blockid=None),
    ]


def test_accepts_tempfile_opened_in_read_mode() -> None:
    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "notes.md"
        file_path.write_text("[[TempNote]] [[TempAlias|Alias]]", encoding="utf-8")

        with file_path.open("r", encoding="utf-8") as source:
            assert extract_links(source) == [
                Link(
                    type=LinkType.WIKILINK,
                    target="TempNote",
                    alias=None,
                    heading=None,
                    blockid=None,
                ),
                Link(
                    type=LinkType.WIKILINK,
                    target="TempAlias",
                    alias="Alias",
                    heading=None,
                    blockid=None,
                ),
            ]


def test_unsupported_input_type_raises_type_error() -> None:
    with pytest.raises(TypeError, match="source must be a str"):
        extract_links(42)  # type: ignore[arg-type]


def test_non_string_read_return_raises_type_error() -> None:
    class NonStringReader:
        def read(self) -> int:
            return 123

    with pytest.raises(TypeError, match="must return a str"):
        extract_links(NonStringReader())  # type: ignore[arg-type]


def test_read_exceptions_are_propagated() -> None:
    class ExplodingReader:
        def read(self) -> str:
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        extract_links(ExplodingReader())


def test_extracts_basic_markdown_links() -> None:
    text = "See [Example](https://example.com) and [Docs](https://docs.example.com)"
    assert extract_links(text) == [
        Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://example.com",
            alias="Example",
            heading=None,
            blockid=None,
        ),
        Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://docs.example.com",
            alias="Docs",
            heading=None,
            blockid=None,
        ),
    ]


def test_extracts_markdown_embeds() -> None:
    text = "![Logo](https://example.com/logo.png)"
    assert extract_links(text) == [
        Link(
            type=LinkType.MARKDOWN_EMBED,
            target="https://example.com/logo.png",
            alias="Logo",
            heading=None,
            blockid=None,
        ),
    ]


def test_extracts_markdown_link_with_empty_text() -> None:
    text = "[](https://example.com)"
    assert extract_links(text) == [
        Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://example.com",
            alias=None,
            heading=None,
            blockid=None,
        ),
    ]


def test_preserves_mixed_link_order() -> None:
    text = "[[Note]] [Link](https://example.com) ![[Embed]] ![Image](img.png) [[Another]]"
    assert extract_links(text) == [
        Link(type=LinkType.WIKILINK, target="Note", alias=None, heading=None, blockid=None),
        Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://example.com",
            alias="Link",
            heading=None,
            blockid=None,
        ),
        Link(type=LinkType.WIKILINK_EMBED, target="Embed", alias=None, heading=None, blockid=None),
        Link(
            type=LinkType.MARKDOWN_EMBED,
            target="img.png",
            alias="Image",
            heading=None,
            blockid=None,
        ),
        Link(type=LinkType.WIKILINK, target="Another", alias=None, heading=None, blockid=None),
    ]


def test_preserves_markdown_link_duplicates() -> None:
    text = "[A](url1) [B](url2) [A](url1)"
    assert extract_links(text) == [
        Link(type=LinkType.MARKDOWN_LINK, target="url1", alias="A", heading=None, blockid=None),
        Link(type=LinkType.MARKDOWN_LINK, target="url2", alias="B", heading=None, blockid=None),
        Link(type=LinkType.MARKDOWN_LINK, target="url1", alias="A", heading=None, blockid=None),
    ]


def test_ignores_partial_markdown_syntax() -> None:
    text = "[No closing paren(url) [text](no close"
    assert extract_links(text) == []


def test_markdown_link_with_parentheses_in_url() -> None:
    text = "[Wiki](https://en.wikipedia.org/wiki/Link_(disambiguation))"
    assert extract_links(text) == [
        Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://en.wikipedia.org/wiki/Link_(disambiguation",
            alias="Wiki",
            heading=None,
            blockid=None,
        ),
    ]


def test_markdown_embed_with_empty_alt() -> None:
    text = "![](https://example.com/transparent.png)"
    assert extract_links(text) == [
        Link(
            type=LinkType.MARKDOWN_EMBED,
            target="https://example.com/transparent.png",
            alias=None,
            heading=None,
            blockid=None,
        ),
    ]


def test_markdown_links_from_file_like_input() -> None:
    source = StringIO("[File](file.md) ![Img](img.png)")
    assert extract_links(source) == [
        Link(
            type=LinkType.MARKDOWN_LINK, target="file.md", alias="File", heading=None, blockid=None
        ),
        Link(
            type=LinkType.MARKDOWN_EMBED, target="img.png", alias="Img", heading=None, blockid=None
        ),
    ]
