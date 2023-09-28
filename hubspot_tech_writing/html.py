import json
import re
import uuid


class CodeBlockAddon:
    """
    Apply custom modules for beautiful code blocks.
    """

    def __init__(self, html: str):
        self.html = html

    # Template contains `%%UUID%%` and `%%CODE%%` placeholders.
    TEMPLATE = """
    {% module_block module "widget_%%UUID%%" %}
    {% module_attribute "child_css" is_json="true" %}{% raw %}{}{% endraw %}{% end_module_attribute %}
    {% module_attribute "code" is_json="true" %}{% raw %}%%CODE%%{% endraw %}{% end_module_attribute %}
    {% module_attribute "css" is_json="true" %}{% raw %}{}{% endraw %}{% end_module_attribute %}
    {% module_attribute "definition_id" is_json="true" %}{% raw %}null{% endraw %}{% end_module_attribute %}
    {% module_attribute "field_types" is_json="true" %}{% raw %}{"code":"richtext","language":"choice","line_wraps":"boolean","margin_after_module":"number","show_copy_button":"boolean","show_line_numbers":"boolean"}{% endraw %}{% end_module_attribute %}
    {% module_attribute "label" is_json="true" %}{% raw %}null{% endraw %}{% end_module_attribute %}
    {% module_attribute "module_id" is_json="true" %}{% raw %}111341816899{% endraw %}{% end_module_attribute %}
    {% module_attribute "path" is_json="true" %}{% raw %}"/sf2-crate/modules/Code Block"{% endraw %}{% end_module_attribute %}
    {% module_attribute "schema_version" is_json="true" %}{% raw %}2{% endraw %}{% end_module_attribute %}
    {% module_attribute "show_copy_button" is_json="true" %}{% raw %}true{% endraw %}{% end_module_attribute %}
    {% module_attribute "show_line_numbers" is_json="true" %}{% raw %}true{% endraw %}{% end_module_attribute %}
    {% module_attribute "smart_objects" is_json="true" %}{% raw %}null{% endraw %}{% end_module_attribute %}
    {% module_attribute "smart_type" is_json="true" %}{% raw %}"NOT_SMART"{% endraw %}{% end_module_attribute %}
    {% module_attribute "tag" is_json="true" %}{% raw %}"module"{% endraw %}{% end_module_attribute %}
    {% module_attribute "type" is_json="true" %}{% raw %}"module"{% endraw %}{% end_module_attribute %}
    {% module_attribute "wrap_field_tag" is_json="true" %}{% raw %}"div"{% endraw %}{% end_module_attribute %}
    {% end_module_block %}
    """  # noqa: E501

    PATTERN = re.compile(
        r"""<pre><code(?:\sclass.+?)>(?P<code>.+?)</code></pre>""", re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def mkcodeblock(self, code: str) -> str:
        code = f"<pre><code>{code}</code></pre>"
        code = json.dumps(code)
        return self.TEMPLATE.replace("%%UUID%%", str(uuid.uuid4())).replace("%%CODE%%", code)

    def process(self) -> "CodeBlockAddon":
        def replacer(match: re.Match):
            return self.mkcodeblock(match.group("code"))

        self.html = self.PATTERN.sub(replacer, self.html)
        return self


class HeaderLinkAddon:
    """
    Add permalink handles to all headers.

    Effectively, converge all headers like:
    <h2 id="overview">Overview</h2>

    into:
    <h2 id="overview">Overview <a class="headerlink" href="#overview" title="Permalink to heading Overview">¶</a></h2>
    """

    PATTERN = re.compile(
        r"""(?P<full><(?P<tag>h\d)\sid="(?P<id>.+?)">(?P<title>.+?)</h\d>)""", re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    def __init__(self, html: str):
        self.html = html

    @staticmethod
    def mkheaderlink(reference: str, title: str, html: str) -> str:
        return f'<a class="headerlink" href="#{reference}" title="Permalink to heading {title}">{html}</a>'

    @staticmethod
    def mkheader(tag: str, identifier: str, html: str) -> str:
        return f'<{tag} id="{identifier}">{html}</{tag}>'

    def process(self) -> "HeaderLinkAddon":
        def replacer(match: re.Match):
            headerlink = self.mkheaderlink(reference=match.group("id"), title=match.group("title"), html="¶")
            inner_html = match.group("title") + " " + headerlink
            return self.mkheader(tag=match.group("tag"), identifier=match.group("id"), html=inner_html)

        self.html = self.PATTERN.sub(replacer, self.html) + self.get_css()
        return self

    @staticmethod
    def get_css():
        """
        CSS styles from the Sphinx project.
        Copyright (c) 2007-2023 by the Sphinx team.
        License: Two clause BSD licence.

        https://github.com/sphinx-doc/sphinx
        /sphinx/themes/basic/static/basic.css_t
        /sphinx/themes/classic/static/classic.css_t
        :return:
        """
        return """

        <style>
        /* basic.css */

        /*
        a.headerlink {
            visibility: hidden;
        }
        */

        h1:hover > a.headerlink,
        h2:hover > a.headerlink,
        h3:hover > a.headerlink,
        h4:hover > a.headerlink,
        h5:hover > a.headerlink,
        h6:hover > a.headerlink,
        dt:hover > a.headerlink,
        caption:hover > a.headerlink,
        p.caption:hover > a.headerlink,
        div.code-block-caption:hover > a.headerlink {
            visibility: visible;
            text-decoration: none;
        }

        /* classic.css */
        a.headerlink {
            color: %(text_color_default)s;
            font-size: 0.8em;
            padding: 0 4px 0 4px;
            text-decoration: none;
        }

        a.headerlink:hover {
            color: %(text_color_hover)s;
        }
        </style>
        """ % {
            "text_color_default": "#dddddd",
            "text_color_hover": "#888888",
        }


def postprocess(html: str) -> str:
    """
    Process Markdown `<pre><code>` blocks.
    """

    # Add permalink symbols to all headers.
    html = HeaderLinkAddon(html).process().html

    # Add a newline before each heading, to improve readability.
    html = re.sub("(<h.)", "\n\\1", html, flags=re.MULTILINE | re.DOTALL | re.VERBOSE)

    # Use dedicated modules for beautiful code blocks.
    return CodeBlockAddon(html).process().html
