from pathlib import Path

import pytest

from hubspot_tech_writing.core import convert


@pytest.fixture
def markdownfile() -> Path:
    return Path(__file__).parent / "data" / "hubspot-blog-post-original.md"


def check_content(html: str):
    assert r'<h2 id="about">About' in html
    assert r'<a href="https://en.wikipedia.org/wiki/Time_series#Models">time series modeling</a>' in html


def test_convert_file(markdownfile):
    html = convert(markdownfile)
    check_content(html)


def test_convert_url():
    url = "https://github.com/crate-workbench/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md"
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
