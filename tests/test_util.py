from hubspot_tech_writing.util.common import ContentTypeResolver
from hubspot_tech_writing.util.io import open_url, path_without_scheme


def test_content_type_resolver_local_html():
    ctr = ContentTypeResolver("/path/to/document.html")
    assert ctr.is_file() is False
    assert ctr.is_text() is True
    assert ctr.is_markup() is False
    assert ctr.is_html() is True
    assert ctr.suffix == ".html"


def test_content_type_resolver_local_markdown():
    ctr = ContentTypeResolver("/path/to/document.md")
    assert ctr.is_file() is False
    assert ctr.is_text() is True
    assert ctr.is_markup() is True
    assert ctr.is_html() is False
    assert ctr.suffix == ".md"


def test_content_type_resolver_local_text():
    ctr = ContentTypeResolver("/path/to/document.txt")
    assert ctr.is_file() is False
    assert ctr.is_text() is True
    assert ctr.is_markup() is False
    assert ctr.is_html() is False
    assert ctr.suffix == ".txt"


def test_content_type_resolver_local_image():
    ctr = ContentTypeResolver("/path/to/document.png")
    assert ctr.is_file() is True
    assert ctr.is_text() is False
    assert ctr.is_markup() is False
    assert ctr.is_html() is False
    assert ctr.suffix == ".png"


def test_content_type_resolver_remote_https():
    ctr = ContentTypeResolver("https://site.example/path/to/document.md")
    assert ctr.is_file() is False
    assert ctr.is_text() is True
    assert ctr.is_markup() is True
    assert ctr.is_html() is False
    assert ctr.suffix == ".md"


def test_content_type_resolver_remote_github():
    ctr = ContentTypeResolver("github://site.example/path/to/document.md")
    assert ctr.is_file() is False
    assert ctr.is_text() is True
    assert ctr.is_markup() is True
    assert ctr.is_html() is False
    assert ctr.suffix == ".md"


def test_content_type_resolver_remote_github_https():
    ctr = ContentTypeResolver("github+https://site.example/path/to/document.md")
    assert ctr.is_file() is False
    assert ctr.is_text() is True
    assert ctr.is_markup() is True
    assert ctr.is_html() is False
    assert ctr.suffix == ".md"


def test_path_without_scheme_local():
    assert str(path_without_scheme("/path/to/document.md")) == "/path/to/document.md"


def test_path_without_scheme_url():
    assert str(path_without_scheme("https://site.example/path/to/document.md")) == "//site.example/path/to/document.md"


def test_path_from_url(markdownurl_github_https_bare, markdownurl_github_https_raw, markdownurl_github_https_blob):
    reference = "github://tests/data/hubspot-blog-post-original.md"
    assert str(open_url(markdownurl_github_https_bare)) == reference
    assert str(open_url(markdownurl_github_https_raw)) == reference
    assert str(open_url(markdownurl_github_https_blob)) == reference
