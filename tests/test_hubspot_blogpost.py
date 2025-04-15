import os

import pytest

from hubspot_tech_writing.core import delete_blogpost, upload
from tests.test_hubspot_file import response_simulator_upload
from tests.util import mkresponse


def response_simulator_create(self, method, url, **kwargs):
    if method == "GET" and url == "https://api.hubapi.com/cms/v3/blogs/posts":
        response = mkresponse({"total": 0, "results": []})
    elif method == "POST" and url == "https://api.hubapi.com/cms/v3/blogs/posts":
        response = mkresponse({"id": "12345"}, status=201, reason="Created")
    elif method == "PATCH" and url == "https://api.hubapi.com/cms/v3/blogs/posts/12345":
        response = mkresponse({"id": "12345"})
    else:
        raise ValueError(f"No HTTP conversation mock for: method={method}, url={url}")
    return response


def response_simulator_create_with_image(self, method, url, **kwargs):
    if method == "GET" and url == "https://api.hubapi.com/cms/v3/blogs/posts":
        response = mkresponse({"total": 0, "results": []})
    elif method == "POST" and url == "https://api.hubapi.com/cms/v3/blogs/posts":
        response = mkresponse({"id": "12345"}, status=201, reason="Created")
    elif method == "PATCH" and url == "https://api.hubapi.com/cms/v3/blogs/posts/12345":
        response = mkresponse({"id": "12345"})
    else:
        raise ValueError(f"No HTTP conversation mock for: method={method}, url={url}")
    return response


def response_simulator_update(self, method, url, **kwargs):
    if method == "GET" and url == "https://api.hubapi.com/cms/v3/blogs/posts":
        response = mkresponse({"total": 1, "results": [{"id": "12345"}]})
    elif method == "PATCH" and url == "https://api.hubapi.com/cms/v3/blogs/posts/12345":
        response = mkresponse({"id": "12345"})
    else:
        raise ValueError(f"No HTTP conversation mock for: method={method}, url={url}")
    return response


def response_simulator_delete_id(self, method, url, **kwargs):
    if method == "GET" and url == "https://api.hubapi.com/cms/v3/blogs/posts/12345":
        response = mkresponse({"total": 1, "results": [{"id": "12345"}]})
    elif method == "DELETE" and url == "https://api.hubapi.com/cms/v3/blogs/posts/12345":
        response = mkresponse({"id": "12345"})
    else:
        raise ValueError(f"No HTTP conversation mock for: method={method}, url={url}")
    return response


def response_simulator_delete_name(self, method, url, **kwargs):
    if method == "GET" and url == "https://api.hubapi.com/cms/v3/blogs/posts":
        response = mkresponse({"total": 1, "results": [{"id": "12345"}]})
    elif method == "GET" and url == "https://api.hubapi.com/cms/v3/blogs/posts/12345":
        response = mkresponse({"total": 1, "results": [{"id": "12345"}]})
    elif method == "DELETE" and url == "https://api.hubapi.com/cms/v3/blogs/posts/12345":
        response = mkresponse({"id": "12345"})
    else:
        raise ValueError(f"No HTTP conversation mock for: method={method}, url={url}")
    return response


def test_upload_blogpost_create_from_html(hubspot_access_token, mocker, caplog, tmp_path):
    tmpfile = tmp_path / "foo.html"
    tmpfile.write_text("<h1>Foobar</h1>\n<p>Franz jagt im komplett verwahrlosten Taxi quer durch Bayern.</p>")

    mocker.patch("hubspot.cms.blogs.blog_posts.rest.RESTClientObject.request", response_simulator_create)
    upload(
        access_token=hubspot_access_token,
        source=tmpfile,
        name="hstw-test",
        content_group_id="55844199082",
    )

    assert "Uploading file:" in caplog.text
    assert "Loading blog post: HubSpotBlogPost identifier=None, name=hstw-test" in caplog.text
    assert "Saving blog post: HubSpotBlogPost identifier=12345, name=hstw-test" in caplog.text


def test_upload_blogpost_create_from_markdown(hubspot_access_token, mocker, caplog, tmp_path):
    tmpfile = tmp_path / "foo.md"
    tmpfile.write_text("# Foobar\nFranz jagt im komplett verwahrlosten Taxi quer durch Bayern.")

    mocker.patch("hubspot.cms.blogs.blog_posts.rest.RESTClientObject.request", response_simulator_create)
    upload(
        access_token=hubspot_access_token,
        source=tmpfile,
        name="hstw-test",
        content_group_id="55844199082",
    )

    assert "Converting to HTML:" in caplog.text
    assert "Uploading file:" in caplog.text
    assert "Loading blog post: HubSpotBlogPost identifier=None, name=hstw-test" in caplog.text
    assert "Saving blog post: HubSpotBlogPost identifier=12345, name=hstw-test" in caplog.text


def test_upload_blogpost_update(hubspot_access_token, mocker, caplog, tmp_path):
    tmpfile = tmp_path / "foo.md"
    tmpfile.write_text("# Foobar\nFranz jagt im komplett verwahrlosten Taxi quer durch Bayern.")

    mocker.patch("hubspot.cms.blogs.blog_posts.rest.RESTClientObject.request", response_simulator_update)
    upload(
        source=tmpfile,
        name="hstw-test",
        content_group_id="55844199082",
        access_token=hubspot_access_token,
    )

    assert "Uploading file:" in caplog.text
    assert "Loading blog post: HubSpotBlogPost identifier=None, name=hstw-test" in caplog.text
    assert "Saving blog post: HubSpotBlogPost identifier=12345, name=hstw-test" in caplog.text


def test_upload_blogpost_with_image(hubspot_access_token, mocker, caplog, tmp_path):
    mdfile = tmp_path / "foo.md"
    pngfile = tmp_path / "images" / "bar.png"
    pngfile.parent.mkdir()
    mdfile.write_text("![bar](images/bar.png)")
    pngfile.write_bytes(b"")

    mocker.patch("hubspot.cms.blogs.blog_posts.rest.RESTClientObject.request", response_simulator_create_with_image)
    mocker.patch("hubspot.files.files.rest.RESTClientObject.request", response_simulator_upload)
    upload(
        source=mdfile,
        name="hstw-test",
        content_group_id="55844199082",
        folder_path="/path/to/assets",
        access_token=hubspot_access_token,
    )

    assert "Uploading file:" in caplog.text

    assert "Loading file: HubSpotFile identifier=None, name=bar.png, folder=/path/to/assets" in caplog.text
    assert "Searching for 'bar.png' in folder path '/path/to/assets'" in caplog.text
    assert "File does not exist: bar.png" in caplog.text
    assert "Creating: HubSpotFile identifier=None, name=bar.png, folder=/path/to/assets" in caplog.text
    assert "Saving file: HubSpotFile identifier=12345, name=bar.png, folder=/path/to/assets" in caplog.text

    assert "Loading blog post: HubSpotBlogPost identifier=None, name=hstw-test" in caplog.text
    assert "Saving blog post: HubSpotBlogPost identifier=12345, name=hstw-test" in caplog.text


def test_delete_by_identifier(hubspot_access_token, mocker, caplog):
    mocker.patch.dict(os.environ, {"CONFIRM": "yes"})
    mocker.patch("hubspot.cms.blogs.blog_posts.rest.RESTClientObject.request", response_simulator_delete_id)
    delete_blogpost(access_token=hubspot_access_token, identifier="12345")
    assert "Deleting blog post with id '12345'" in caplog.messages


def test_delete_by_name(hubspot_access_token, mocker, caplog):
    mocker.patch.dict(os.environ, {"CONFIRM": "yes"})
    mocker.patch("hubspot.cms.blogs.blog_posts.rest.RESTClientObject.request", response_simulator_delete_name)
    delete_blogpost(access_token=hubspot_access_token, name="testdrive")
    assert "Deleting blog post with name 'testdrive'" in caplog.messages


def test_delete_fail(hubspot_access_token, mocker, caplog):
    mocker.patch.dict(os.environ, {"CONFIRM": "yes"})
    with pytest.raises(ValueError) as ex:
        delete_blogpost(access_token=hubspot_access_token)
    assert ex.match("Deleting blog post needs post id or name")
