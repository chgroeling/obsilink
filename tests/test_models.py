from __future__ import annotations

from pathlib import Path

import pytest

from obsilink import Link, LinkType


class TestLinkIsUrl:
    def test_returns_true_for_http_url(self) -> None:
        link = Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://example.com",
            alias="Example",
            heading=None,
            blockid=None,
        )
        assert link.is_url is True

    def test_returns_true_for_ftp_url(self) -> None:
        link = Link(
            type=LinkType.MARKDOWN_LINK,
            target="ftp://files.example.com/doc.pdf",
            alias="Doc",
            heading=None,
            blockid=None,
        )
        assert link.is_url is True

    def test_returns_true_for_file_url(self) -> None:
        link = Link(
            type=LinkType.MARKDOWN_LINK,
            target="file:///path/to/file.txt",
            alias="File",
            heading=None,
            blockid=None,
        )
        assert link.is_url is True

    def test_returns_true_for_mailto_url(self) -> None:
        link = Link(
            type=LinkType.PLAIN_URL,
            target="mailto:user@example.com",
            alias="Email",
            heading=None,
            blockid=None,
        )
        assert link.is_url is True

    def test_returns_false_for_wikilink_target(self) -> None:
        link = Link(
            type=LinkType.WIKILINK,
            target="Note",
            alias=None,
            heading=None,
            blockid=None,
        )
        assert link.is_url is False

    def test_returns_false_for_relative_path_target(self) -> None:
        link = Link(
            type=LinkType.MARKDOWN_LINK,
            target="folder/note.md",
            alias="Note",
            heading=None,
            blockid=None,
        )
        assert link.is_url is False

    def test_returns_false_for_windows_style_path(self) -> None:
        link = Link(
            type=LinkType.MARKDOWN_LINK,
            target="C:\\Users\\file.txt",
            alias="File",
            heading=None,
            blockid=None,
        )
        assert link.is_url is False


class TestLinkAsPath:
    def test_returns_path_for_wikilink_target(self) -> None:
        link = Link(
            type=LinkType.WIKILINK,
            target="Notes/MyNote",
            alias=None,
            heading=None,
            blockid=None,
        )
        assert link.as_path == Path("Notes/MyNote")

    def test_returns_path_for_relative_markdown_target(self) -> None:
        link = Link(
            type=LinkType.MARKDOWN_LINK,
            target="docs/readme.md",
            alias="Readme",
            heading=None,
            blockid=None,
        )
        assert link.as_path == Path("docs/readme.md")

    def test_raises_value_error_for_http_url(self) -> None:
        link = Link(
            type=LinkType.MARKDOWN_LINK,
            target="https://example.com",
            alias="Example",
            heading=None,
            blockid=None,
        )
        with pytest.raises(ValueError, match="Cannot convert URL target to Path"):
            _ = link.as_path

    def test_raises_value_error_for_ftp_url(self) -> None:
        link = Link(
            type=LinkType.MARKDOWN_LINK,
            target="ftp://server.com/file.txt",
            alias="File",
            heading=None,
            blockid=None,
        )
        with pytest.raises(ValueError, match="Cannot convert URL target to Path"):
            _ = link.as_path
