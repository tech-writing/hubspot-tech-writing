import contextlib
import io
import typing as t
from pathlib import Path

from pathlibfs import Path as PathPlus
from yarl import URL


@contextlib.contextmanager
def to_io(source: t.Union[str, Path, t.IO]) -> t.Generator[t.IO, None, None]:
    fp: t.IO
    if isinstance(source, io.TextIOWrapper):
        fp = source
    elif isinstance(source, (str, Path, PathPlus)):
        source = str(source)
        path = path_from_url(source)
        fp = path.open(mode="rt")
        """
        if source.startswith("http://") or source.startswith("https://"):
            response = requests.get(source, timeout=10.0)
            fp = io.StringIO(response.text)
        else:
            fp = open(source, "r")
        """
    else:
        raise TypeError(f"Unable to converge to IO handle. type={type(source)}, value={source}")
    yield fp
    fp.close()


def path_from_url(url: str) -> PathPlus:
    """
    Convert GitHub HTTP URL to pathlibfs / fsspec URL.

    Input URLs
    ----------
    github+https://foobar:ghp_lalala@github.com/acme/sweet-camino/path/to/document.md
    github+https://foobar:ghp_lalala@github.com/acme/sweet-camino/blob/main/path/to/document.md

    Output Path
    -----------
    fs = Path("github://path/to/document.md", username="foobar", token="ghp_lalala", org="acme", repo="sweet-camino")
    """
    uri = URL(url)

    if uri.scheme.startswith("github+https"):
        path_fragments = uri.path.split("/")[1:]
        path_kwargs = {
            "username": uri.user,
            "token": uri.password,
            "org": path_fragments[0],
            "repo": path_fragments[1],
        }

        real_path_fragments = path_fragments[2:]
        if path_fragments[2] == "blob":
            real_path_fragments = path_fragments[4:]

        downstream_url = "github://" + "/".join(real_path_fragments)
        path = PathPlus(downstream_url, **path_kwargs)

    else:
        path = PathPlus(url)
    return path
