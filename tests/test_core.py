import pytest

from hubspot_tech_writing.core import convert, upload


def check_content(html: str):
    assert r'<h2 id="about">About' in html
    assert r'<a href="https://en.wikipedia.org/wiki/Time_series#Models">time series modeling</a>' in html


def test_convert_file(markdownfile):
    html = convert(markdownfile)
    check_content(html)


def test_convert_url():
    url = "https://github.com/tech-writing/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md"
    html = convert(url)
    check_content(html)


def test_convert_io(markdownfile):
    fp = open(markdownfile, "r")
    html = convert(fp)
    check_content(html)


def test_convert_addon_codeblock(markdownfile):
    html = convert(markdownfile)
    assert (
        r'{% module_attribute "code" is_json="true" %}{% raw %}"<pre><code>'
        r"from merlion.models.defaults import DefaultDetectorConfig, DefaultDetector\n\n" in html
    )


def test_convert_addon_headerlink(markdownfile):
    html = convert(markdownfile)
    # Verify augmented HTML.
    assert (
        '<h2 id="about">About <a class="headerlink" href="#about" title="Permalink to heading About">¶</a></h2>' in html
    )
    # Verify CSS.
    assert "a.headerlink {" in html


def test_upload_unknown_file_type(tmp_path):
    tmp_file = tmp_path / "foo.txt"
    with pytest.raises(ValueError) as ex:
        upload(access_token="unknown", source=tmp_file, name="foo", folder_path="/path/to/foo")  # noqa: S106
    assert ex.match("Unknown file type: .txt")
