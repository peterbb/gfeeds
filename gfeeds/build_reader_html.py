import readability
from gfeeds.reader_mode_style import css, dark_mode_css
from lxml.html import html5parser, tostring as html_tostring
from gettext import gettext as _


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


# fp_item should be a FeedItem.fp_item
def build_reader_html_old(og_html, dark_mode=False, fp_item=None):
    assert og_html is not None
    root = html5parser.fromstring(
        og_html if type(og_html) == str else og_html.decode()
    )

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
