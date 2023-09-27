from pathlib import Path

from hubspot_tech_writing.core import convert


def check_content(html: str):
    assert r'<h2 id="about">About</h2>' in html
    assert r'<a href="https://en.wikipedia.org/wiki/Time_series#Models">time series modeling</a>' in html
    assert (
        r'{% module_attribute "code" is_json="true" %}{% raw %}"<pre><code>'
        r"from merlion.models.defaults import DefaultDetectorConfig, DefaultDetector\n\n" in html
    )


def test_convert_file():
    infile = Path(__file__).parent / "data" / "hubspot-blog-post-original.md"
    html = convert(infile)
    check_content(html)


def test_convert_url():
    url = "https://github.com/crate-workbench/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md"
    html = convert(url)
    check_content(html)


def test_convert_io():
    infile = Path(__file__).parent / "data" / "hubspot-blog-post-original.md"
    fp = open(infile, "r")
    html = convert(fp)
    check_content(html)
