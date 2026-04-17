from __future__ import annotations

from io import StringIO

import pytest

from obsilink import Link, LinkType
from obsilink.replacer import replace_links


class TestReplaceWikilinks:
    def test_replaces_basic_wikilink(self) -> None:
        text = "See [[Note]] for details"
        old = Link(type=LinkType.WIKILINK, target="Note", alias=None, heading=None, blockid=None)
        new = Link(type=LinkType.WIKILINK, target="NewNote", alias=None, heading=None, blockid=None)

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "See [[NewNote]] for details"
        assert results == [True]

    def test_replaces_wikilink_with_alias(self) -> None:
        text = "See [[Note|Display]] here"
        old = Link(
            type=LinkType.WIKILINK, target="Note", alias="Display", heading=None, blockid=None
        )
        new = Link(
            type=LinkType.WIKILINK, target="Other", alias="Changed", heading=None, blockid=None
        )

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "See [[Other|Changed]] here"
        assert results == [True]

    def test_replaces_wikilink_with_heading(self) -> None:
        text = "Go to [[Note#Section]]"
        old = Link(
            type=LinkType.WIKILINK, target="Note", alias=None, heading="Section", blockid=None
        )
        new = Link(type=LinkType.WIKILINK, target="Note", alias=None, heading="Other", blockid=None)

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "Go to [[Note#Other]]"
        assert results == [True]

    def test_replaces_wikilink_with_blockid(self) -> None:
        text = "Ref [[Note^abc]]"
        old = Link(type=LinkType.WIKILINK, target="Note", alias=None, heading=None, blockid="abc")
        new = Link(type=LinkType.WIKILINK, target="Note", alias=None, heading=None, blockid="xyz")

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "Ref [[Note^xyz]]"
        assert results == [True]

    def test_replaces_wikilink_embed(self) -> None:
        text = "Image ![[Diagram]] here"
        old = Link(
            type=LinkType.WIKILINK_EMBED,
            target="Diagram",
            alias=None,
            heading=None,
            blockid=None,
        )
        new = Link(
            type=LinkType.WIKILINK_EMBED,
            target="NewDiagram",
            alias=None,
            heading=None,
            blockid=None,
        )

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "Image ![[NewDiagram]] here"
        assert results == [True]

    def test_replaces_only_first_occurrence(self) -> None:
        text = "[[A]] and [[A]] and [[A]]"
        old = Link(type=LinkType.WIKILINK, target="A", alias=None, heading=None, blockid=None)
        new = Link(type=LinkType.WIKILINK, target="B", alias=None, heading=None, blockid=None)

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "[[B]] and [[A]] and [[A]]"
        assert results == [True]


class TestReplaceMarkdownLinks:
    def test_replaces_markdown_link(self) -> None:
        text = "Click [here](https://old.com) now"
        old = Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://old.com",
            alias="here",
            heading=None,
            blockid=None,
        )
        new = Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://new.com",
            alias="here",
            heading=None,
            blockid=None,
        )

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "Click [here](https://new.com) now"
        assert results == [True]

    def test_replaces_markdown_embed(self) -> None:
        text = "Image ![alt](img.png) shown"
        old = Link(
            type=LinkType.MARKDOWN_EMBED,
            target="img.png",
            alias="alt",
            heading=None,
            blockid=None,
        )
        new = Link(
            type=LinkType.MARKDOWN_EMBED,
            target="new.png",
            alias="alt",
            heading=None,
            blockid=None,
        )

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "Image ![alt](new.png) shown"
        assert results == [True]


class TestReplacePlainUrl:
    def test_replaces_plain_url(self) -> None:
        text = "Visit https://example.com today"
        old = Link(
            type=LinkType.PLAIN_URL,
            target="https://example.com",
            alias=None,
            heading=None,
            blockid=None,
        )
        new = Link(
            type=LinkType.PLAIN_URL,
            target="https://other.com",
            alias=None,
            heading=None,
            blockid=None,
        )

        result_text, results = replace_links(text, [(old, new)])
        assert result_text == "Visit https://other.com today"
        assert results == [True]


class TestMultipleReplacements:
    def test_applies_multiple_replacements_sequentially(self) -> None:
        text = "[[A]] and [[B]] and [[C]]"
        replacements = [
            (
                Link(type=LinkType.WIKILINK, target="A", alias=None, heading=None, blockid=None),
                Link(type=LinkType.WIKILINK, target="X", alias=None, heading=None, blockid=None),
            ),
            (
                Link(type=LinkType.WIKILINK, target="B", alias=None, heading=None, blockid=None),
                Link(type=LinkType.WIKILINK, target="Y", alias=None, heading=None, blockid=None),
            ),
        ]

        result_text, results = replace_links(text, replacements)
        assert result_text == "[[X]] and [[Y]] and [[C]]"
        assert results == [True, True]

    def test_reports_false_for_missing_link(self) -> None:
        text = "[[A]] only"
        replacements = [
            (
                Link(type=LinkType.WIKILINK, target="A", alias=None, heading=None, blockid=None),
                Link(type=LinkType.WIKILINK, target="X", alias=None, heading=None, blockid=None),
            ),
            (
                Link(type=LinkType.WIKILINK, target="Z", alias=None, heading=None, blockid=None),
                Link(type=LinkType.WIKILINK, target="Y", alias=None, heading=None, blockid=None),
            ),
        ]

        result_text, results = replace_links(text, replacements)
        assert result_text == "[[X]] only"
        assert results == [True, False]

    def test_replaces_duplicate_links_one_at_a_time(self) -> None:
        text = "[[A]] [[A]] [[A]]"
        old = Link(type=LinkType.WIKILINK, target="A", alias=None, heading=None, blockid=None)
        new = Link(type=LinkType.WIKILINK, target="B", alias=None, heading=None, blockid=None)

        result_text, results = replace_links(text, [(old, new), (old, new)])
        assert result_text == "[[B]] [[B]] [[A]]"
        assert results == [True, True]

    def test_empty_replacements(self) -> None:
        text = "[[A]]"
        result_text, results = replace_links(text, [])
        assert result_text == "[[A]]"
        assert results == []


class TestSourceTypes:
    def test_accepts_file_like_source(self) -> None:
        source = StringIO("[[Old]] link")
        old = Link(type=LinkType.WIKILINK, target="Old", alias=None, heading=None, blockid=None)
        new = Link(type=LinkType.WIKILINK, target="New", alias=None, heading=None, blockid=None)

        result_text, results = replace_links(source, [(old, new)])
        assert result_text == "[[New]] link"
        assert results == [True]

    def test_raises_type_error_for_invalid_source(self) -> None:
        with pytest.raises(TypeError):
            replace_links(42, [])  # type: ignore[arg-type]
