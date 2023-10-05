import re

import pytest

from hubspot_tech_writing.hubspot_api import HubSpotAdapter, HubSpotBlogPost, HubSpotFile


@pytest.fixture()
def hubspot_adapter(hubspot_access_token):
    return HubSpotAdapter(access_token=hubspot_access_token)


@pytest.fixture()
def tmpfile_unknown(tmp_path):
    tmpfile = tmp_path / "foo.unknown"
    tmpfile.write_bytes(b"")
    yield tmpfile


def test_blogpost_without_identifier_or_name(hubspot_adapter):
    with pytest.raises(ValueError) as ex:
        HubSpotBlogPost(hubspot_adapter=hubspot_adapter)
    assert ex.match("One of 'identifier' or 'name' must be specified")


def test_get_or_create_blogpost_without_name(mocker, hubspot_adapter):
    mocker.patch("hubspot_tech_writing.hubspot_api.HubSpotBlogPost.load")
    post = HubSpotBlogPost(hubspot_adapter=hubspot_adapter, identifier="12345")
    with pytest.raises(ValueError) as ex:
        hubspot_adapter.get_or_create_blogpost(post)
    assert ex.match("Blog post needs a 'name'")


def test_blogpost_with_identifier_and_name(mocker, hubspot_adapter):
    mocker.patch("hubspot_tech_writing.hubspot_api.HubSpotBlogPost.load")
    with pytest.raises(ValueError) as ex:
        HubSpotBlogPost(hubspot_adapter=hubspot_adapter, identifier="12345", name="testdrive")
    assert ex.match("Either 'identifier' or 'name' must be specified, not both")


def test_blogpost_without_content_group_identifier(mocker, hubspot_adapter):
    mocker.patch("hubspot_tech_writing.hubspot_api.HubSpotAdapter.get_blogpost_by_name", side_effect=FileNotFoundError)
    with pytest.raises(ValueError) as ex:
        HubSpotBlogPost(hubspot_adapter=hubspot_adapter, name="testdrive")
    assert ex.match(re.escape("Blog (content group) identifier is required for creating a blog post"))


def test_file_without_identifier_or_path(tmpfile_unknown, hubspot_adapter):
    with pytest.raises(ValueError) as ex:
        HubSpotFile(hubspot_adapter=hubspot_adapter, source=tmpfile_unknown)
    assert ex.match("One of 'identifier' or 'name' must be specified")


def test_file_without_folder(tmpfile_unknown, hubspot_adapter):
    with pytest.raises(ValueError) as ex:
        HubSpotFile(
            hubspot_adapter=hubspot_adapter,
            source=tmpfile_unknown,
            identifier="12345",
        )
    assert ex.match("Folder is required for uploading files, please specify either `folder_id` or `folder_path`")


def test_file_with_folder_path_and_identifier_model(tmpfile_unknown, hubspot_adapter):
    with pytest.raises(ValueError) as ex:
        HubSpotFile(
            hubspot_adapter=hubspot_adapter,
            source=tmpfile_unknown,
            identifier="12345",
            folder_path="/path/to/foo",
            folder_id="12345",
        )
    assert ex.match("One of 'folder_id' or 'folder_path' must be specified, not both")


def test_get_or_create_file_without_name(mocker, tmpfile_unknown, hubspot_adapter):
    mocker.patch("hubspot_tech_writing.hubspot_api.HubSpotFile.load")
    file = HubSpotFile(
        hubspot_adapter=hubspot_adapter,
        source=tmpfile_unknown,
        identifier="12345",
        folder_path="/path/to/foo",
    )
    with pytest.raises(ValueError) as ex:
        hubspot_adapter.get_or_create_file(file)
    assert ex.match("File name missing")


def test_get_or_create_file_with_folder_path_and_identifier(mocker, tmpfile_unknown, hubspot_adapter):
    mocker.patch("hubspot_tech_writing.hubspot_api.HubSpotAdapter.get_file_by_name", side_effect=FileNotFoundError)
    mocker.patch("hubspot_tech_writing.hubspot_api.HubSpotFile.load")
    file = HubSpotFile(
        hubspot_adapter=hubspot_adapter,
        source=tmpfile_unknown,
        name="testdrive",
        folder_path="/path/to/foo",
    )
    file.folder_id = "12345"
    with pytest.raises(ValueError) as ex:
        hubspot_adapter.get_or_create_file(file)
    assert ex.match("Use either `folder_id` or `folder_path`, but not both")
