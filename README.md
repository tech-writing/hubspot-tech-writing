# Technical Writing on HubSpot

[![Tests](https://github.com/crate-workbench/hubspot-tech-writing/actions/workflows/main.yml/badge.svg)](https://github.com/crate-workbench/hubspot-tech-writing/actions/workflows/main.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/crate-workbench/hubspot-tech-writing.svg)](https://codecov.io/gh/crate-workbench/hubspot-tech-writing/)
[![Python versions](https://img.shields.io/pypi/pyversions/hubspot-tech-writing.svg)](https://pypi.org/project/hubspot-tech-writing/)

[![License](https://img.shields.io/github/license/crate-workbench/hubspot-tech-writing.svg)](https://github.com/crate-workbench/hubspot-tech-writing/blob/main/LICENSE)
[![Status](https://img.shields.io/pypi/status/hubspot-tech-writing.svg)](https://pypi.org/project/hubspot-tech-writing/)
[![PyPI](https://img.shields.io/pypi/v/hubspot-tech-writing.svg)](https://pypi.org/project/hubspot-tech-writing/)
[![Downloads](https://pepy.tech/badge/hubspot-tech-writing/month)](https://pypi.org/project/hubspot-tech-writing/)


<!-- » [Documentation] -->

» [Changelog]
| [PyPI]
| [Issues]
| [Source code]
| [License]

[Changelog]: https://github.com/crate-workbench/hubspot-tech-writing/blob/main/CHANGES.md
[Documentation]: https://hubspot-tech-writing.readthedocs.io/
[Issues]: https://github.com/crate-workbench/hubspot-tech-writing/issues
[License]: https://github.com/crate-workbench/hubspot-tech-writing/blob/main/LICENSE
[PyPI]: https://pypi.org/project/hubspot-tech-writing/
[Source code]: https://github.com/crate-workbench/hubspot-tech-writing


## About

- [Markdown] to HTML converter with features relevant to generate HubSpot blog posts.
- Supports writing technical documentation on [HubSpot].
- Upload blog posts to the HubSpot API, using the [hubspot-api-python] package.
- See [Markdown Support for Technical Bloggers].


## Setup

```shell
pip install --upgrade 'git+https://github.com/crate-workbench/hubspot-tech-writing'
```

After installation, you can verify if it was successful.
```shell
hstw --version
```


## Usage

### Convert
You can convert a Markdown file on your workstation, and write the output to an HTML file.
```shell
wget -O original.md https://github.com/crate-workbench/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md
hstw convert original.md converted.html
```

Alternatively, convert a Markdown file at a remote location, and write the output to STDOUT.
```shell
hstw convert https://github.com/crate-workbench/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md
```

### Linkcheck

In order to report about missing links to the web, or inline images, run the
link checker on your Markdown documents.
```shell
hstw linkcheck original.md
```

Alternatively, you can also use a remote resource here.
```shell
hstw linkcheck https://github.com/crate-workbench/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md
```


### HubSpot Upload

Uploading to HubSpot is an iterative process, mostly. So, we recommend to define a
corresponding environment variable for storing your access token.
```shell
export HUBSPOT_ACCESS_TOKEN=pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2
hstw upload testdrive.html
```

For more detailed information about this feature, please refer to the inline help:
```shell
hstw upload --help
```


## Prior Art

- https://github.com/verypossible/hubmd
- https://github.com/danjamescrosby/markdown-to-hubspot-blog


[HubSpot]: https://www.hubspot.com/
[hubspot-api-python]: https://github.com/HubSpot/hubspot-api-python
[Markdown]: https://daringfireball.net/projects/markdown/
[Markdown Support for Technical Bloggers]: https://community.hubspot.com/t5/HubSpot-Ideas/Markdown-Support-for-Technical-Bloggers/idi-p/15724
