import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def reset_environment() -> None:
    if "HUBSPOT_ACCESS_TOKEN" in os.environ:
        del os.environ["HUBSPOT_ACCESS_TOKEN"]


@pytest.fixture
def markdownfile() -> Path:
    return Path(__file__).parent / "data" / "hubspot-blog-post-original.md"


@pytest.fixture
def markdownfile_minimal_broken_links() -> Path:
    return Path(__file__).parent / "data" / "minimal-broken-links.md"
