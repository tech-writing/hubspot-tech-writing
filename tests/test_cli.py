from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from hubspot_tech_writing.cli import cli


def test_version():
    """
    CLI test: Invoke `hstw --version`
    """
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args="--version",
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_convert_file_to_stdout(markdownfile):
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=f"--debug convert '{markdownfile}'",
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_convert_file_to_file(tmp_path, markdownfile):
    outfile = tmp_path / "converted.html"
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=f"convert '{markdownfile}' '{outfile}'",
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_linkcheck_broken(caplog, markdownfile_minimal_broken_links):
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=f"--debug linkcheck '{markdownfile_minimal_broken_links}'",
        catch_exceptions=False,
    )
    assert result.exit_code == 22

    assert "Total files checked: 1" in result.output
    assert "Broken image: images/bar.png" in caplog.text
    assert "[✖] images/bar.png" in result.output
    assert "[✖] https://foo.example.org/" in result.output


def test_upload_no_access_token(markdownfile):
    runner = CliRunner()

    with pytest.raises(ValueError) as ex:
        runner.invoke(
            cli,
            args=f"--debug upload '{markdownfile}'",
            catch_exceptions=False,
        )
    assert ex.match("Communicating with the HubSpot API needs an access token")


def test_delete_blogpost(mocker):
    runner = CliRunner()
    delete_blogpost: Mock = mocker.patch("hubspot_tech_writing.cli.delete_blogpost")
    runner.invoke(
        cli,
        args="--debug delete post --id=138458225506 --access-token=foo",
        catch_exceptions=False,
    )
    delete_blogpost.assert_called_once_with(access_token="foo", identifier="138458225506", name=None)  # noqa: S106


def test_delete_file(mocker):
    runner = CliRunner()
    delete_file: Mock = mocker.patch("hubspot_tech_writing.cli.delete_file")
    runner.invoke(
        cli,
        args="--debug delete file --id=138458225506 --access-token=foo",
        catch_exceptions=False,
    )
    delete_file.assert_called_once_with(access_token="foo", identifier="138458225506", path=None)  # noqa: S106
