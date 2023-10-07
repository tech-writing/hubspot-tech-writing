import functools
import logging
import typing as t
import warnings
from pathlib import Path
from tempfile import NamedTemporaryFile

import hubspot
import markdown
import mkdocs_linkcheck as lc
from hubspot.cms.blogs.blog_posts import BlogPost

from hubspot_tech_writing.html import postprocess
from hubspot_tech_writing.hubspot_api import HubSpotAdapter, HubSpotBlogPost, HubSpotFile
from hubspot_tech_writing.util.common import ContentTypeResolver
from hubspot_tech_writing.util.html import HTMLImageTranslator
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
    logger.info(f"Converting to HTML: {source}")
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


def upload(
    access_token: str,
    source: t.Union[str, Path],
    name: str,
    content_group_id: t.Optional[str] = None,
    folder_id: t.Optional[str] = None,
    folder_path: t.Optional[str] = None,
):
    source_path = Path(source)

    ctr = ContentTypeResolver(name=source_path)

    logger.info(f"Uploading file: {source}")
    hsa = HubSpotAdapter(access_token=access_token)

    # Upload text files as blog posts.
    if ctr.is_text():
        # Convert markup to HTML.
        if ctr.is_markup():
            html = convert(source)
        elif ctr.is_html():
            html = Path(source).read_text()
        else:
            raise ValueError(f"Unknown file type: {ctr.suffix}")

        # Collect and converge images.
        if not folder_id and not folder_path:
            logger.warning("Images will not be uploaded, please supply folder id or folder name")
        else:
            uploader = functools.partial(
                upload, access_token=access_token, folder_id=folder_id, folder_path=folder_path
            )
            hit = HTMLImageTranslator(html=html, source_path=source_path, uploader=uploader)
            hit.discover().process()
            html = hit.html_out

        # Upload blog post.
        name = name or source_path.stem
        article = HubSpotBlogPost(hubspot_adapter=hsa, name=name, content_group_id=content_group_id)
        post: BlogPost = article.post
        post.post_body = html
        return article.save()

        # Only in emergency situations.
        # article.delete()  # noqa: ERA001

    # Upload other files as File objects.
    elif ctr.is_file():  # noqa: RET505
        name = name or source_path.name
        file = HubSpotFile(hubspot_adapter=hsa, source=source, name=name, folder_id=folder_id, folder_path=folder_path)
        return file.save()
    return None

    # Only in emergency situations.
    # file.delete()  # noqa: ERA001


def delete_blogpost(access_token: str, identifier: t.Optional[str] = None, name: t.Optional[str] = None):
    hsa = HubSpotAdapter(access_token=access_token)

    try:
        if identifier:
            logger.info(f"Deleting blog post with id '{identifier}'")
            article = HubSpotBlogPost(hubspot_adapter=hsa, identifier=identifier, autocreate=False)
        elif name:
            logger.info(f"Deleting blog post with name '{name}'")
            article = HubSpotBlogPost(hubspot_adapter=hsa, name=name, autocreate=False)
        else:
            raise ValueError("Deleting blog post needs post id or name")

        return article.delete()

    # May happen if the blog post item got found by an inquiry,
    # but is already gone when it is about to be deleted.
    except hubspot.cms.blogs.blog_posts.exceptions.NotFoundException:
        logger.warning(f"Blog post not found: id={identifier}, name={name}")  # pragma: nocover


def delete_file(access_token: str, identifier: t.Optional[str] = None, path: t.Optional[str] = None):
    hsa = HubSpotAdapter(access_token=access_token)

    if identifier:
        logger.info(f"Deleting file with id '{identifier}'")
        return hsa.delete_file_by_id(identifier)
    elif path:  # noqa: RET505
        logger.info(f"Deleting files at path '{path}'")
        return hsa.delete_files_by_path(path)
    else:
        raise ValueError("Deleting files needs file id or path")
