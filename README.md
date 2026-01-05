# Technical Writing on HubSpot

[![Tests](https://github.com/tech-writing/hubspot-tech-writing/actions/workflows/main.yml/badge.svg)](https://github.com/tech-writing/hubspot-tech-writing/actions/workflows/main.yml)
[![Test coverage](https://img.shields.io/codecov/c/gh/tech-writing/hubspot-tech-writing.svg)](https://codecov.io/gh/tech-writing/hubspot-tech-writing/)
[![Python versions](https://img.shields.io/pypi/pyversions/hubspot-tech-writing.svg)](https://pypi.org/project/hubspot-tech-writing/)

[![License](https://img.shields.io/github/license/tech-writing/hubspot-tech-writing.svg)](https://github.com/tech-writing/hubspot-tech-writing/blob/main/LICENSE)
[![Status](https://img.shields.io/pypi/status/hubspot-tech-writing.svg)](https://pypi.org/project/hubspot-tech-writing/)
[![PyPI](https://img.shields.io/pypi/v/hubspot-tech-writing.svg)](https://pypi.org/project/hubspot-tech-writing/)
[![Downloads](https://pepy.tech/badge/hubspot-tech-writing/month)](https://pypi.org/project/hubspot-tech-writing/)


<!-- » [Documentation] -->

» [Changelog]
| [PyPI]
| [Issues]
| [Source code]
| [License]

[Changelog]: https://github.com/tech-writing/hubspot-tech-writing/blob/main/CHANGES.md
[Documentation]: https://hubspot-tech-writing.readthedocs.io/
[Issues]: https://github.com/tech-writing/hubspot-tech-writing/issues
[License]: https://github.com/tech-writing/hubspot-tech-writing/blob/main/LICENSE
[PyPI]: https://pypi.org/project/hubspot-tech-writing/
[Source code]: https://github.com/tech-writing/hubspot-tech-writing


## About

- Support writing technical documentation on [HubSpot].
- [Markdown] to HTML converter with a few bells and whistles relevant for creating
  HubSpot blog posts.
- Upload blog posts and files to the HubSpot API, using the [hubspot-api-python] package.
- See community request about »[Markdown Support for Technical Bloggers]«.


## Setup

```shell
pip install --upgrade hubspot-tech-writing
```

After installation, you can verify if it was successful.
```shell
hstw --version
```


## Usage

### Markup Conversion
You can convert a Markdown file on your workstation, and write the output to an HTML file.
```shell
wget -O original.md https://github.com/tech-writing/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md
hstw convert original.md converted.html
```

Alternatively, convert a Markdown file at a remote location, and write the output to STDOUT.
```shell
hstw convert https://github.com/tech-writing/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md
```

### Link Checker

In order to report about missing links to the web, or inline images, run the
link checker on your Markdown documents.
```shell
hstw linkcheck original.md
```

Alternatively, you can also use a remote resource here.
```shell
hstw linkcheck https://github.com/tech-writing/hubspot-tech-writing/raw/main/tests/data/hubspot-blog-post-original.md
```

### HubSpot Upload

Uploading to HubSpot is mostly an iterative process, so you will most likely need to use the
program multiple times on the same resource. In order ease invocation, we recommend to define
an environment variable for storing your access token to the HubSpot API.
```shell
export HUBSPOT_ACCESS_TOKEN=pat-na1-e8805e92-b7fd-5c9b-adc8-2299569f56c2
```

Upload HTML file from workstation.
The name of the blog post will be derived from the file name.
```shell
hstw upload testdrive.html
```

Upload PNG image from workstation to folder path on hubfs.
```shell
hstw upload testdrive.png --folder-path=/foo/bar
```

Convert Markdown to HTML, upload the document under a different name, and also upload all
referenced images.
```shell
hstw upload /path/to/document.md --name=a-different-name --folder-path=/blog/2023/topic
```

For more detailed information about this feature, please refer to the inline help:
```shell
hstw upload --help
```

### HubSpot Delete

You can delete blog post and file entities, by their unique resource identifiers,
or by name resp. path.

```shell
# Delete blog post by resource identifier.
hstw delete post --id=138458225506
```

```shell
# Delete file by path.
hstw delete file --path=/testdrive/foo.png
```

For more detailed information about this feature, please refer to the inline help:
```shell
hstw delete --help
```


## Troubleshooting

### Blog posts may not contain embedded images

If you are uploading directly from GitHub, and run such a command,
```
hstw upload https://github.com/acme/foo-repo/raw/main/article.md --name=testdrive
```
only to receive an error message like this,
```json
{
  "correlationId": "4836e94d-e42b-47a1-afff-597d8b67ba93",
  "errorType": "BLOG_POST_CONTAINS_EMBEDDED_IMAGES",
  "message": "Blog posts may not contain embedded images. Please upload images to File Manager.",
  "status": "error"
}
```
you are most certainly using a "private" repository, where `hstw` does not have
access permissions to.


## Prior Art

- https://github.com/verypossible/hubmd
- https://github.com/danjamescrosby/markdown-to-hubspot-blog


[HubSpot]: https://www.hubspot.com/
[hubspot-api-python]: https://github.com/HubSpot/hubspot-api-python
[Markdown]: https://daringfireball.net/projects/markdown/
[Markdown Support for Technical Bloggers]: https://community.hubspot.com/t5/HubSpot-Ideas/Markdown-Support-for-Technical-Bloggers/idi-p/15724
