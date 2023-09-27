import json
import re
import uuid

CODE_BLOCK_TEMPLATE = """
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


def mkcodeblock(code: str) -> str:
    code = f"<pre><code>{code}</code></pre>"
    code = json.dumps(code)
    return CODE_BLOCK_TEMPLATE.replace("%%UUID%%", str(uuid.uuid4())).replace("%%CODE%%", code)


def process_code_blocks(html: str) -> str:
    def replacer(match: re.Match):
        return mkcodeblock(match.group("code"))

    # Apply custom modules.
    code_block_re = re.compile(
        r"""<pre><code(?:\sclass.+?)>(?P<code>.+?)</code></pre>""", re.MULTILINE | re.DOTALL | re.VERBOSE
    )
    return code_block_re.sub(replacer, html)


def postprocess(html: str) -> str:
    """
    Process Markdown `<pre><code>` blocks.
    """
    html = process_code_blocks(html)

    # Add a newline before each heading, to improve readability.
    return re.sub("(<h.)", "\n\\1", html, flags=re.MULTILINE | re.DOTALL | re.VERBOSE)
