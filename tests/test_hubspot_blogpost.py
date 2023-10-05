import json
import os

import pytest
from hubspot.cms.blogs.blog_posts.rest import RESTResponse
from urllib3 import HTTPResponse

from hubspot_tech_writing.core import delete_blogpost, upload


def mkresponse(data, status=200, reason="OK"):
    body = json.dumps(data).encode("utf-8")
    return RESTResponse(HTTPResponse(body=body, status=status, reason=reason))


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
    tmpfile = tmp_path / "foo.html"
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
