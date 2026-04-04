from __future__ import annotations

from io import StringIO

import pytest

from obsilink import extract_obsidian_links


def test_extracts_basic_note_links() -> None:
    text = "See [[Note]] and [[Another Note]]"
    assert extract_obsidian_links(text) == ["Note", "Another Note"]


def test_extracts_alias_links_as_targets_only() -> None:
    text = "Use [[Note|Alias]] and [[Folder/Note#Heading|Display]]"
    assert extract_obsidian_links(text) == ["Note", "Folder/Note#Heading"]


def test_extracts_folder_and_heading_targets() -> None:
    text = "[[Folder/Note]] then [[Folder/Note#Heading]]"
    assert extract_obsidian_links(text) == ["Folder/Note", "Folder/Note#Heading"]


def test_includes_embed_targets() -> None:
    text = "Embed ![[Diagram]] and normal [[Note]]"
    assert extract_obsidian_links(text) == ["Diagram", "Note"]


def test_ignores_malformed_or_partial_syntax() -> None:
    text = "[[Unclosed and Not[[Link]] and ]][["
    assert extract_obsidian_links(text) == []


def test_preserves_duplicates_and_order() -> None:
    text = "[[A]] [[B]] [[A]] [[C]] [[B]]"
    assert extract_obsidian_links(text) == ["A", "B", "A", "C", "B"]


def test_accepts_text_file_like_input() -> None:
    source = StringIO("[[FileLike]] [[Second]]")
    assert extract_obsidian_links(source) == ["FileLike", "Second"]


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
