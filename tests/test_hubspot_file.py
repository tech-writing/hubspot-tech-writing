import os
import re

import pytest

from hubspot_tech_writing.core import delete_file, upload

from .util import mkresponse


def response_simulator_upload(self, method, url, **kwargs):
    if method == "GET" and url == "https://api.hubapi.com/files/v3/files/search":
        response = mkresponse({"total": 0, "results": []})
    elif method == "POST" and url == "https://api.hubapi.com/files/v3/files":
        response = mkresponse(
            {"id": "12345", "url": "https://site.example/hubfs/any.png"}, status=201, reason="Created"
        )
    elif method == "PUT" and url == "https://api.hubapi.com/files/v3/files/12345":
        response = mkresponse({"id": "12345", "url": "https://site.example/hubfs/any.png"})
    else:
        raise ValueError(f"No HTTP conversation mock for: method={method}, url={url}")
    return response


def response_simulator_delete(self, method, url, **kwargs):
    if method == "GET" and url == "https://api.hubapi.com/files/v3/files/search":
        response = mkresponse({"total": 1, "results": [{"id": "12345"}]})
    elif method == "GET" and url == "https://api.hubapi.com/files/v3/files/12345":
        response = mkresponse({"id": "12345"})
    elif method == "DELETE" and url == "https://api.hubapi.com/files/v3/files/12345":
        response = mkresponse({"id": "12345"})
    else:
        raise ValueError(f"No HTTP conversation mock for: method={method}, url={url}")
    return response


def test_upload_file_folder_id_success(mocker, caplog, tmp_path):
    tmpfile = tmp_path / "foo.png"
    tmpfile.write_bytes(b"foo")

    mocker.patch("hubspot.files.files.rest.RESTClientObject.request", response_simulator_upload)
    upload(
        access_token="pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2",  # noqa: S106
        source=tmpfile,
        name="hstw-test",
        folder_id="66833198083",
    )

    assert "Uploading file:" in caplog.text
    assert "Loading file: HubSpotFile identifier=None, name=hstw-test" in caplog.text
    assert "Saving file: HubSpotFile identifier=12345, name=hstw-test" in caplog.text


def test_upload_file_folder_path_success(mocker, caplog, tmp_path):
    tmpfile = tmp_path / "foo.png"
    tmpfile.write_bytes(b"foo")

    mocker.patch("hubspot.files.files.rest.RESTClientObject.request", response_simulator_upload)
    upload(
        access_token="pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2",  # noqa: S106
        source=tmpfile,
        name="hstw-test",
        folder_path="/path/to/testdrive",
    )

    assert "Uploading file:" in caplog.text
    assert "Loading file: HubSpotFile identifier=None, name=hstw-test" in caplog.text
    assert "Saving file: HubSpotFile identifier=12345, name=hstw-test" in caplog.text


def test_upload_file_fail_no_access_token():
    with pytest.raises(TypeError) as ex:
        upload(source=None, name=None)
    assert ex.match(re.escape("upload() missing 1 required positional argument: 'access_token'"))


def test_upload_file_fail_missing_folder():
    with pytest.raises(ValueError) as ex:
        upload(access_token="foo", source="/path/to/file.png", name=None)  # noqa: S106
    assert ex.match("Folder is required for uploading files")


def test_upload_file_fail_folder_id_and_path():
    with pytest.raises(ValueError) as ex:
        upload(
            access_token="foo",  # noqa: S106
            source="/path/to/file.png",
            name=None,
            folder_id="foo",
            folder_path="/path/to/foo",
        )
    assert ex.match("One of 'folder_id' or 'folder_path' must be specified, not both")


def test_delete_by_identifier(hubspot_access_token, mocker, caplog):
    mocker.patch.dict(os.environ, {"CONFIRM": "yes"})
    mocker.patch("hubspot.files.files.rest.RESTClientObject.request", response_simulator_delete)
    delete_file(access_token=hubspot_access_token, identifier="12345")
    assert "Deleting file with id '12345'" in caplog.messages


def test_delete_by_name(hubspot_access_token, mocker, caplog):
    mocker.patch.dict(os.environ, {"CONFIRM": "yes"})
    mocker.patch("hubspot.files.files.rest.RESTClientObject.request", response_simulator_delete)
    delete_file(access_token=hubspot_access_token, path="/path/to/testdrive")
    assert "Deleting files at path '/path/to/testdrive'" in caplog.messages


def test_delete_fail(hubspot_access_token, mocker, caplog):
    mocker.patch.dict(os.environ, {"CONFIRM": "yes"})
    with pytest.raises(ValueError) as ex:
        delete_file(access_token=hubspot_access_token)
    assert ex.match("Deleting files needs file id or path")
