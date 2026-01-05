import logging
import sys
import typing as t

import click
from click_aliases import ClickAliasedGroup

from hubspot_tech_writing.core import convert, delete_blogpost, delete_file, linkcheck, upload
from hubspot_tech_writing.util.cli import boot_click, docstring_format_verbatim, make_command

logger = logging.getLogger(__name__)


def help_convert():
    """
    Convert Markdown to HTML suitable for HubSpot blog posts.

    Synopsis
    ========

    # Convert Markdown file on workstation.
    hstw convert original.md converted.html

    # Convert remote Markdown resource.
    hstw convert https://github.com/tech-writing/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md

    """  # noqa: E501


def help_linkcheck():
    """
    Check a Markdown file for broken links.

    Synopsis
    ========

    # Check Markdown file on workstation.
    hstw linkcheck document.md

    # Check Markdown file at remote location.
    hstw linkcheck https://github.com/tech-writing/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md

    """  # noqa: E501


def help_upload():
    """
    Upload HTML, Markdown, or image files to the HubSpot API.

    Synopsis
    ========

    # For convenience, supply the HubSpot API access token as environment variable.
    export HUBSPOT_ACCESS_TOKEN=pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2

    # Upload HTML file from workstation.
    # The name of the blog post will be derived from the file name.
    hstw upload testdrive.html

    # Upload PNG image from workstation to folder path on hubfs.
    hstw upload testdrive.png --folder-path=/foo/bar

    # Upload PNG image under a different name.
    hstw upload testdrive.png --folder-path=/foo/bar --name=foo.png

    # Upload PNG image to folder, addressed by identifier.
    hstw upload testdrive.png --folder-id=138270606691

    Usage
    =====

    # When uploading a blog post, and it has not been created beforehand, you will need
    # to supply the Blog (content group) identifier. If you want to upload the blog post
    # or file under a different name, use the `--name=` option.
    hstw upload output.html --content-group-id=26956288532 --name=testdrive --access-token=pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2

    # You can also address a Markdown file at a remote location, convert it to HTML,
    # and upload to HubSpot in one go.
    hstw upload https://github.com/tech-writing/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md --name=testdrive

    """  # noqa: E501


def help_delete():
    """
    Delete blog posts or files.

    The program will prompt you about deleting items, per item, after
    presenting a representation to be able to identify it.

    In order to acknowledge delete operations upfront, define the environment
    variable `CONFIRM=yes`.

    Usage
    =====

    # Delete blog post by resource identifier.
    hstw delete post --id=138458225506

    # Delete blog post by name.
    hstw delete post --name=testdrive

    # Delete file by file identifier.
    hstw delete file --id=138270606692

    # Delete file by path.
    hstw delete file --path=/testdrive/foo.png
    """  # noqa: E501


id_option = click.option(
    "--id",
    "id_",
    type=str,
    required=False,
    help="The HubSpot resource identifier",
)
path_option = click.option(
    "--path",
    type=str,
    required=False,
    help="The path to the file on HubSpot hubfs",
)
access_token_option = click.option(
    "--access-token", type=str, required=False, envvar="HUBSPOT_ACCESS_TOKEN", help="HubSpot API access token"
)


@click.group(cls=ClickAliasedGroup)
@click.version_option(package_name="hubspot-tech-writing")
@click.option("--verbose", is_flag=True, required=False, help="Turn on logging")
@click.option("--debug", is_flag=True, required=False, help="Turn on logging with debug level")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool):
    return boot_click(ctx, verbose, debug)


@make_command(cli, "convert", help_convert)
@click.argument("source")
@click.argument("target", required=False)
def convert_cli(source: str, target: t.Optional[str] = None):
    html = convert(source)
    fp: t.IO
    if target:
        logger.info(f"Writing output to HTML: {target}")
        fp = open(target, "w")
    else:
        logger.info("Writing output to HTML: STDOUT")
        fp = sys.stdout
    print(html, file=fp)


@make_command(cli, "linkcheck", help_linkcheck)
@click.argument("source")
def linkcheck_cli(source: str):
    if not linkcheck(source):
        logger.error("Bad links were found. Exiting with an error.")
        raise SystemExit(22)


@make_command(cli, "upload", help_upload)
@click.argument("source")
@click.option(
    "--name",
    type=str,
    required=False,
    help="The name of the item. By default, the name will be derived from the file name.",
)
@click.option(
    "--content-group-id",
    type=str,
    required=False,
    help="The Blog (content group) identifier. Needed when creating a post",
)
@click.option(
    "--folder-id",
    type=str,
    required=False,
    help="The folder id for storing files. Alternatively, use folder name.",
)
@click.option(
    "--folder-path",
    type=str,
    required=False,
    help="The folder path for storing files. Alternatively, use folder id.",
)
@access_token_option
def upload_cli(access_token: str, source: str, name: str, content_group_id: str, folder_id: str, folder_path: str):
    upload(
        access_token=access_token,
        source=source,
        name=name,
        content_group_id=content_group_id,
        folder_id=folder_id,
        folder_path=folder_path,
    )


@cli.group(cls=ClickAliasedGroup, help=docstring_format_verbatim(help_delete.__doc__))
def delete():  # pragma: nocover
    pass


@make_command(delete, "post", help_delete, aliases=["blogpost"])
@id_option
@click.option(
    "--name",
    type=str,
    required=False,
    help="The name of the blog post.",
)
@access_token_option
def delete_blogpost_cli(access_token: str, id_: str, name: str):
    delete_blogpost(access_token=access_token, identifier=id_, name=name)


@make_command(delete, "file", help_delete)
@id_option
@path_option
@access_token_option
def delete_file_cli(access_token: str, id_: str, path: str):
    delete_file(access_token=access_token, identifier=id_, path=path)
