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


@pytest.fixture
def hubspot_access_token():
    """
    It is a defunct / invalid HubSpot access token, just used for testing purposes.
    """
    return "pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2"
