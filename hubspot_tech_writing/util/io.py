import contextlib
import io
import typing as t
from pathlib import Path

import requests


@contextlib.contextmanager
def to_io(source: t.Union[str, Path, t.IO]) -> t.Generator[t.IO, None, None]:
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
    yield fp
    fp.close()
