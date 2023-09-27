import io
import typing as t
from pathlib import Path

import markdown
import requests

from hubspot_tech_writing.hubspot import postprocess


def convert(source: t.Union[str, Path, t.IO]):
    """
    m = markdown2.Markdown(extras=[
        #"admonitions",
        "fenced-code-blocks",
        "links",
        #"footnotes", "header-ids", "strike", "tables", "toc",
    ])
    """
    m = markdown.Markdown(
        extensions=[
            "admonition",
            "fenced_code",
            "footnotes",
            "tables",
            "toc",
        ]
    )
    if isinstance(source, (str, Path)):
        source = str(source)
        fp: t.IO
        if source.startswith("http://") or source.startswith("https://"):
            response = requests.get(source, timeout=10.0)
            fp = io.StringIO(response.text)
        else:
            fp = open(source, "r")
    else:
        fp = source
    html = m.convert(fp.read())
    return postprocess(html)
