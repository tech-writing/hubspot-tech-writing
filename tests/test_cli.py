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
