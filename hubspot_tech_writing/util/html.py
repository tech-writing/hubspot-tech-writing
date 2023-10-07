import dataclasses
import logging
import typing as t
from copy import deepcopy
from pathlib import Path

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class HTMLImage:
    alt: str
    src: str


class HTMLImageTranslator:
    """
    Translate local image references into remote ones, by uploading them.
    After that, replace URLs in HTML document.
    """

    def __init__(self, html: str, source_path: t.Union[str, Path], uploader: t.Optional[t.Callable] = None):
        self.html_in: str = html
        self.html_out: t.Optional[str] = None
        self.source_path = source_path
        self.uploader = uploader
        self.images_in: t.List[HTMLImage] = []
        self.images_local: t.List[HTMLImage] = []
        self.images_remote: t.List[HTMLImage] = []

    def __str__(self):
        return (
            f"HTMLImageTranslator:\nin:     {self.images_in}\nlocal:  {self.images_local}\nremote: {self.images_remote}"
        )

    def discover(self):
        self.scan().resolve()
        return self

    def process(self):
        self.upload()
        self.produce()
        return self

    def scan(self) -> "HTMLImageTranslator":
        """
        Scan input HTML for all <img ...> tags.
        """
        soup = BeautifulSoup(self.html_in, features="html.parser")
        images = soup.find_all(name="img")
        self.images_in = []
        for image in images:
            self.images_in.append(HTMLImage(src=image.get("src"), alt=image.get("alt")))
        return self

    def resolve(self) -> "HTMLImageTranslator":
        """
        Process discovered image elements, computing effective paths.
        """
        if self.source_path is None:
            return self
        parent_path = Path(self.source_path)
        if parent_path.is_file():
            parent_path = parent_path.parent
        self.images_local = []
        for image in self.images_in:
            image_new = deepcopy(image)
            if not image.src.startswith("http://") and not image.src.startswith("https://"):
                # Use absolute paths 1:1.
                if image.src.startswith("/"):
                    pass

                # Relative paths are relative to the original document.
                else:
                    image_new.src = str(Path(parent_path) / image.src)
            self.images_local.append(image_new)
        return self

    def upload(self) -> "HTMLImageTranslator":
        """
        Upload images to HubSpot API, and store URLs.
        """
        if self.uploader is None:
            logger.warning("No upload without uploader")
            return self
        for image_local in self.images_local:
            hs_file = self.uploader(source=image_local.src, name=Path(image_local.src).name)
            image_url = hs_file.url
            image_remote: HTMLImage = deepcopy(image_local)
            image_remote.src = image_url
            self.images_remote.append(image_remote)
        return self

    def produce(self) -> "HTMLImageTranslator":
        """
        Produce HTML output, with all image references replaced by their remote targets.
        """
        html = self.html_in
        for image_in, image_remote in zip(self.images_in, self.images_remote):
            html = html.replace(image_in.src, image_remote.src)
        self.html_out = html
        return self
