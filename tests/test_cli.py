from pathlib import Path

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


def test_convert_file_to_stdout():
    infile = Path(__file__).parent / "data" / "hubspot-blog-post-original.md"
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=f"--debug convert '{infile}'",
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_convert_file_to_file(tmp_path):
    infile = Path(__file__).parent / "data" / "hubspot-blog-post-original.md"
    outfile = tmp_path / "converted.html"
    runner = CliRunner()

    result = runner.invoke(
        cli,
        args=f"convert '{infile}' '{outfile}'",
        catch_exceptions=False,
    )
    assert result.exit_code == 0
