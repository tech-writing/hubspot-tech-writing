import logging
import sys
import typing as t

import click
from click_aliases import ClickAliasedGroup

from hubspot_tech_writing.core import convert, linkcheck
from hubspot_tech_writing.util.cli import boot_click, make_command

logger = logging.getLogger(__name__)


def help_convert():
    """
    Convert Markdown to HTML suitable for HubSpot blog posts.

    Synopsis
    ========

    # Convert Markdown file on workstation.
    hstw convert original.md converted.html

    # Convert remote Markdown resource.
    hstw convert https://github.com/crate-workbench/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md

    """  # noqa: E501


def help_linkcheck():
    """
    Check a Markdown file for broken links.

    Synopsis
    ========

    # Check Markdown file on workstation.
    hstw linkcheck document.md

    # Check Markdown file at remote location.
    hstw linkcheck https://github.com/crate-workbench/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md

    """  # noqa: E501


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
