import readability
from gfeeds.reader_mode_style import CSS, DARK_MODE_CSS
from lxml.html import html5parser, tostring as html_tostring
from gettext import gettext as _

import pygments
import pygments.lexers
from pygments.formatters import HtmlFormatter


# Thanks to Eloi Rivard (azmeuk) for the contribution on the media block
def _build_media_text(title, content):
    return '''
        <p>
            <strong>{0}:</strong>
            {1}
        </p>'''.format(title, content.replace("\n", "<br />"))


def _build_media_link(title, content, link):
    return _build_media_text(
        title, f'<a href="{link}">{content}</a>'
    )


# thumbnails aren't supposed to be links, images can be?
# funnily enough, using `#` as a link opens the main content url
# that's because the webkitview sets the base url to the feed item link
def _build_media_img(title, imgurl, link='#'):
    return _build_media_link(
        title, f'<br /><img src="{imgurl}" />', link
    )


def build_syntax_highlight(root):
    syntax_highlight_css = ""

    code_nodes = root.xpath(
        '//x:pre/x:code',
        namespaces={'x': 'http://www.w3.org/1999/xhtml'}
    )
    lexer = None
    for code_node in code_nodes:
        classes = code_node.attrib.get("class", "").split(" ")
        for klass in classes:
            try:
                lexer = pygments.lexers.get_lexer_by_name(
                    klass.replace("language-", ""),
                    stripall=True,
                )
                break
            except pygments.util.ClassNotFound:
                pass

        if not lexer:
            try:
                lexer = pygments.lexers.guess_lexer(code_node.text)
            except pygments.util.ClassNotFound:
                continue

        formatter = HtmlFormatter(style='solarized-dark')

        if not syntax_highlight_css:
            syntax_highlight_css = formatter.get_style_defs()

        newtext = pygments.highlight(code_node.text, lexer, formatter)
        newhtml = html5parser.fromstring(newtext)

        pre_node = code_node.getparent()
        pre_node.getparent().replace(pre_node, newhtml)

    return syntax_highlight_css, root


def build_syntax_highlight_from_raw_html(raw_html):
    return build_syntax_highlight(
        html5parser.fromstring(
            raw_html if type(raw_html) == str else raw_html.decode()
        )
    )


def build_reader_html(og_html, dark_mode=False, fp_item=None):
    def build_media_block():
        if not fp_item:
            return ''
        media_s = '<hr />'
        for el in fp_item:
            if el[:6].lower() == 'media_':
                try:
                    if el.lower() == 'media_thumbnail':
                        media_s += _build_media_img(
                            _('Thumbnail'),
                            fp_item["media_thumbnail"][0]["url"]
                        )
                    else:
                        for subel in fp_item[el]:
                            media_s += _build_media_text(
                                subel.capitalize(),
                                fp_item[el][subel]
                            )
                except Exception:
                    continue
        return media_s if media_s != '<hr />' else ''

    doc = readability.Document(og_html)
    content = doc.summary(True)
    syntax_highlight_css, root = build_syntax_highlight_from_raw_html(content)
    content = html_tostring(
        root
    ).decode().replace('<html:', '<').replace('</html:', '</')
    content += build_media_block()
    return f'''<html>
        <head>
            <style>
                {CSS}
                {DARK_MODE_CSS if dark_mode else ""}
                {syntax_highlight_css}
            </style>
            <title>{doc.short_title()}</title>
        </head>
        <body>
            <article>
                <h1>{doc.short_title() or fp_item["title"]}</h1>
                {content}
            </article>
        </body>
    </html>'''
