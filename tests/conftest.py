from pathlib import Path

import pytest


@pytest.fixture
def markdownfile() -> Path:
    return Path(__file__).parent / "data" / "hubspot-blog-post-original.md"


@pytest.fixture
def markdownfile_minimal_broken_links() -> Path:
    return Path(__file__).parent / "data" / "minimal-broken-links.md"
