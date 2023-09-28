import logging
import typing as t
import warnings
from pathlib import Path
from tempfile import NamedTemporaryFile

import markdown
import mkdocs_linkcheck as lc
from hubspot.cms.blogs.blog_posts import BlogPost

from hubspot_tech_writing.html import postprocess
from hubspot_tech_writing.hubspot_api import BlogArticle, HubSpotAdapter
from hubspot_tech_writing.util.io import to_io

logger = logging.getLogger(__name__)


def convert(source: t.Union[str, Path, t.IO]):
    """
    m = markdown2.Markdown(extras=[
        #"admonitions",
        "fenced-code-blocks",
        "links",
        #"footnotes", "header-ids", "strike", "tables", "toc",
    ])
    """
    logger.info(f"Converting Markdown to HTML: {source}")
    m = markdown.Markdown(
        extensions=[
            "admonition",
            "fenced_code",
            "footnotes",
            "tables",
            "toc",
        ]
    )
    with to_io(source) as fp:
        html = m.convert(fp.read())
    return postprocess(html)


def linkcheck(source: str):
    # Suppress unclosed socket warning from linkchecker.
    # sys:1: ResourceWarning: unclosed <socket.socket ...)>
    # ResourceWarning: Enable tracemalloc to get the object allocation traceback
    warnings.simplefilter(action="ignore", category=ResourceWarning)

    with NamedTemporaryFile(suffix=".md", mode="w") as tmpfile:
        with to_io(source) as fp:
            tmpfile.write(fp.read())
            tmpfile.flush()
        path = Path(tmpfile.name)
        logger.info(f"Checking links in Markdown file: {source}")
        outcome1 = not lc.check_links(path=path, ext=".md", use_async=False)

    html = convert(source)
    with NamedTemporaryFile(suffix=".html", mode="w") as tmpfile:
        tmpfile.write(html)
        tmpfile.flush()
        logger.info(f"Checking links in HTML file: {tmpfile.name}")
        outcome2 = not lc.check_links(path=Path(tmpfile.name), ext=".html", use_async=False)

    return outcome1 and outcome2


def upload(source: t.Union[str, Path], name: str, content_group_id: str, access_token: str):
    source = Path(source)

    if not name:
        name = source.stem

    if source.suffix.endswith(".md"):
        html = convert(source)
    else:
        html = Path(source).read_text()

    logger.info(f"Uploading file: {source}")

    hsa = HubSpotAdapter(access_token=access_token)

    article = BlogArticle(hubspot_adapter=hsa, name=name, content_group_id=content_group_id)
    post: BlogPost = article.post
    post.post_body = html
    article.save()

    # Only in emergency situations.
    # article.delete()  # noqa: ERA001
