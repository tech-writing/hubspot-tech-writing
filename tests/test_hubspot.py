import json

from hubspot.cms.blogs.blog_posts.rest import RESTResponse
from urllib3 import HTTPResponse

from hubspot_tech_writing.core import upload


def mkresponse(data, status=200, reason="OK"):
    body = json.dumps(data).encode("utf-8")
    return RESTResponse(HTTPResponse(body=body, status=status, reason=reason))


def response_simulator_create(self, method, url, **kwargs):
    global created

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


def test_upload_create(mocker, caplog, tmp_path):
    tmpfile = tmp_path / "foo.html"
    tmpfile.write_text("# Foobar\nFranz jagt im komplett verwahrlosten Taxi quer durch Bayern.")

    mocker.patch("hubspot.cms.blogs.blog_posts.rest.RESTClientObject.request", response_simulator_create)
    upload(
        source=tmpfile,
        name="hstw-test",
        content_group_id="55844199082",
        access_token="pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2",  # noqa: S106
    )

    assert "Uploading file:" in caplog.text
    assert "Loading: BlogArticle identifier=None, name=hstw-test" in caplog.text
    assert "Saving: BlogArticle identifier=12345, name=hstw-test" in caplog.text


def test_upload_update(mocker, caplog, tmp_path):
    tmpfile = tmp_path / "foo.html"
    tmpfile.write_text("# Foobar\nFranz jagt im komplett verwahrlosten Taxi quer durch Bayern.")

    mocker.patch("hubspot.cms.blogs.blog_posts.rest.RESTClientObject.request", response_simulator_update)
    upload(
        source=tmpfile,
        name="hstw-test",
        content_group_id="55844199082",
        access_token="pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2",  # noqa: S106
    )

    assert "Uploading file:" in caplog.text
    assert "Loading: BlogArticle identifier=None, name=hstw-test" in caplog.text
    assert "Saving: BlogArticle identifier=12345, name=hstw-test" in caplog.text
