from __future__ import annotations

from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from obsilink import Link, extract_obsidian_links


def test_extracts_basic_note_links() -> None:
    text = "See [[Note]] and [[Another Note]]"
    assert extract_obsidian_links(text) == [
        Link(note="Note", alias=None, heading=None, blockid=None, embed=False),
        Link(note="Another Note", alias=None, heading=None, blockid=None, embed=False),
    ]


def test_extracts_alias_links() -> None:
    text = "Use [[Note|Alias]] and [[Folder/Note#Heading|Display]]"
    assert extract_obsidian_links(text) == [
        Link(note="Note", alias="Alias", heading=None, blockid=None, embed=False),
        Link(
            note="Folder/Note",
            alias="Display",
            heading="Heading",
            blockid=None,
            embed=False,
        ),
    ]


def test_extracts_heading_links() -> None:
    text = "[[Note#Heading]]"
    assert extract_obsidian_links(text) == [
        Link(note="Note", alias=None, heading="Heading", blockid=None, embed=False)
    ]


def test_extracts_blockid_links() -> None:
    text = "[[Note^blockid]]"
    assert extract_obsidian_links(text) == [
        Link(note="Note", alias=None, heading=None, blockid="blockid", embed=False)
    ]


def test_extracts_heading_and_blockid_links() -> None:
    text = "[[Note#Heading^blockid]]"
    assert extract_obsidian_links(text) == [
        Link(note="Note", alias=None, heading="Heading", blockid="blockid", embed=False)
    ]


def test_includes_embed_targets() -> None:
    text = "Embed ![[Diagram]] and normal [[Note]]"
    assert extract_obsidian_links(text) == [
        Link(note="Diagram", alias=None, heading=None, blockid=None, embed=True),
        Link(note="Note", alias=None, heading=None, blockid=None, embed=False),
    ]


def test_ignores_malformed_or_partial_syntax() -> None:
    text = "[[Unclosed and Not[[Link]] and ]][["
    assert extract_obsidian_links(text) == []


def test_preserves_duplicates_and_order() -> None:
    text = "[[A]] [[B]] [[A]] [[C]] [[B]]"
    assert extract_obsidian_links(text) == [
        Link(note="A", alias=None, heading=None, blockid=None, embed=False),
        Link(note="B", alias=None, heading=None, blockid=None, embed=False),
        Link(note="A", alias=None, heading=None, blockid=None, embed=False),
        Link(note="C", alias=None, heading=None, blockid=None, embed=False),
        Link(note="B", alias=None, heading=None, blockid=None, embed=False),
    ]


def test_accepts_text_file_like_input() -> None:
    source = StringIO("[[FileLike]] [[Second]]")
    assert extract_obsidian_links(source) == [
        Link(note="FileLike", alias=None, heading=None, blockid=None, embed=False),
        Link(note="Second", alias=None, heading=None, blockid=None, embed=False),
    ]


def test_accepts_tempfile_opened_in_read_mode() -> None:
    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "notes.md"
        file_path.write_text("[[TempNote]] [[TempAlias|Alias]]", encoding="utf-8")

        with file_path.open("r", encoding="utf-8") as source:
            assert extract_obsidian_links(source) == [
                Link(note="TempNote", alias=None, heading=None, blockid=None, embed=False),
                Link(note="TempAlias", alias="Alias", heading=None, blockid=None, embed=False),
            ]


def test_unsupported_input_type_raises_type_error() -> None:
    with pytest.raises(TypeError, match="source must be a str"):
        extract_obsidian_links(42)  # type: ignore[arg-type]


def test_non_string_read_return_raises_type_error() -> None:
    class NonStringReader:
        def read(self) -> int:
            return 123

    with pytest.raises(TypeError, match="must return a str"):
        extract_obsidian_links(NonStringReader())  # type: ignore[arg-type]


def test_read_exceptions_are_propagated() -> None:
    class ExplodingReader:
        def read(self) -> str:
            raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        extract_obsidian_links(ExplodingReader())
