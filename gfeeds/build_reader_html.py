import readability
from gfeeds.reader_mode_style import css, dark_mode_css
from lxml.html import html5parser, tostring as html_tostring
from gettext import gettext as _

import pygments
import pygments.lexers
import pygments.formatters

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

    code_nodes = root.xpath('//x:pre/x:code',
        namespaces={'x': 'http://www.w3.org/1999/xhtml'}
    )

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

        formatter = pygments.formatters.HtmlFormatter(style='solarized-dark')

        if not syntax_highlight_css:
            syntax_highlight_css = formatter.get_style_defs()

        newtext = pygments.highlight(code_node.text, lexer, formatter)
        newhtml = html5parser.fromstring(newtext)

        pre_node = code_node.getparent()
        pre_node.getparent().replace(pre_node, newhtml)

    return syntax_highlight_css, root


# fp_item should be a FeedItem.fp_item
def build_reader_html_old(og_html, dark_mode=False, fp_item=None):
    assert og_html is not None
    root = html5parser.fromstring(
        og_html if type(og_html) == str else og_html.decode()
    )

    syntax_highlight_css, root = build_syntax_highlight(root)

    def extract_useful_content():
        try:
            article_els = root.xpath(
                '//x:article',
                namespaces={'x': 'http://www.w3.org/1999/xhtml'}
            )
            if len(article_els) == 0:
                article_els = root.xpath(
                    '//x:body',
                    namespaces={'x': 'http://www.w3.org/1999/xhtml'}
                )
            article_s = html_tostring(
                article_els[0]
            ).decode().replace('<html:', '<').replace('</html:', '</')
        except Exception:
            article_s = (
                '<h1><i>' +
                _('Reader mode unavailable for this site') +
                '</i></h1>'
            )
        return article_s

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

    article_s = extract_useful_content()
    article_s = article_s.replace('<br></br>', '<br>')
    article_s += build_media_block()
    # subsequent alterations to the reader content can be done here

    return f'''<html>
        <head><style>
        {dark_mode_css if dark_mode else ""}
        {css}
        {syntax_highlight_css}
        </style></head>
        <body>
            <article>{article_s}</article>
        </body>
        </html>'''


def build_reader_html(og_html, dark_mode=False, fp_item=None):
    if fp_item is None:
        return build_reader_html_old(og_html, dark_mode, fp_item)
    doc = readability.Document(og_html)
    return f'''<html>
        <head>
            <style>
                {css}
                {dark_mode_css if dark_mode else ""}
            </style>
            <title>{doc.short_title()}</title>
        </head>
        <body>
            <article>
                <h1>{doc.short_title()}</h1>
                {doc.summary(True)}
            </article>
        </body>
    </html>'''
