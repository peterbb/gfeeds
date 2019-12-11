css = """
/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * Alternatively, the contents of this file may be used under the terms
 * of the GNU General Public License Version 3, as described below:
 *
 * This file is free software: you may copy, redistribute and/or modify
 * it under the terms of the GNU General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * This file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
 * Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see http://www.gnu.org/licenses/.
 *
 * Changes
 * - replace Firefox specific css extensions with WebKit css extensions
 * - append FeedView css selectors
 *
 * - Adjusted for Epiphany (Removing footer)
 *
 * Notes:
 *
 * - WCAG 2.0 level AA recommends at least 4.5 for normal text, 3 for large
 *   text. See: https://marijohannessen.github.io/color-contrast-checker/
 *
 * - The @font-face rules try to use locally installed copies of the fonts,
 *   and fallback to the bundled versions. As per W3C recommendation, the
 *   rules include both full font names and PostScript names to assure
 *   proper matching across platforms and installed font formats. See:
 *   https://www.w3.org/TR/css-fonts-3/#font-face-rule
 */

@font-face {
  font-family: ephy-reader-serif;
  src: local('DejaVu Serif'),
       local('DejaVu Serif Book');
  font-weight: normal;
  font-style: normal;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-serif;
  src: local('DejaVu Serif Italic');
  font-weight: normal;
  font-style: italic;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-serif;
  src: local('DejaVu Serif Bold');
  font-weight: bold;
  font-style: normal;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-serif;
  src: local('DejaVu Serif Bold Italic');
  font-weight: bold;
  font-style: italic;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-sans;
  src: local('Cantarell'),
       local('DejaVu Sans');
  font-weight: normal;
  font-style: normal;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-sans;
  src: local('Cantarell Italic'),
       local('DejaVu Sans Italic');
  font-weight: normal;
  font-style: italic;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-sans;
  src: local('Cantarell Bold'),
       local('DejaVu Sans Bold');
       url('ephy-resource:///org/gnome/epiphany/fonts/MerriweatherSans-Bold.ttf') format('truetype');
  font-weight: bold;
  font-style: normal;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-sans;
  src: local('Cantarell Bold Italic'),
       local('DejaVu Sans Bold Italic');
  font-weight: bold;
  font-style: italic;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-mono;
  src: local('DejaVu Sans Mono'),
       local('DejaVu Sans Mono Book');
  font-weight: normal;
  font-style: normal;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-mono;
  src: local('DejaVu Sans Mono Italic'),
       local('DejaVu Sans Mono Oblique');
  font-weight: normal;
  font-style: italic;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-mono;
  src: local('DejaVu Sans Mono Bold');
  font-weight: bold;
  font-style: normal;
  font-display: block;
}

@font-face {
  font-family: ephy-reader-mono;
  src: local('DejaVu Sans Mono Bold Italic'),
       local('DejaVu Sans Mono Bold Oblique');
  font-weight: bold;
  font-style: italic;
  font-display: block;
}


body.sans {
  font-family: ephy-reader-sans, sans-serif;
}

body.serif {
  font-family: ephy-reader-serif, serif;
}

body {
  line-height: 1.45;
  text-rendering: optimizeLegibility;
}

body.light {
  /* Contrast ratio: 10.49 */
  color: #333333;
  background: #efefee;
}

body.dark {
  color: #efefef;
  background: #181818;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  /* Contrast ratio: 4.77 */
  font-weight: bold;
  color: #555555;
  font-family: ephy-reader-serif, serif;
}

body.serif h1,
body.serif h2,
body.serif h3,
body.serif h4,
body.serif h5,
body.serif h6 {
  font-family: ephy-reader-sans, sans-serif;
}


body.dark h1,
body.dark h2,
body.dark h3,
body.dark h4,
body.dark h5,
body.dark h6 {
  color: #999999;
}


tt,
code,
pre {
  font-family: ephy-reader-mono, monospace;
}

hr {
  border: 1px solid #efefef;
}

picture img {
  border-radius: 3px;
}

img {
    display: inline-block !important;
    position: relative !important;
    background-color: white;
}

h1 {
  font-size: 1.6em;
}

h2 {
  font-size: 1.2em;
}

h3 {
  font-size: 1em;
}

a {
  text-decoration: underline;
  font-weight: normal;
}

a,
a:visited,
a:hover,
a:active {
  color: #0095dd;
}

* {
  max-width: 100%;
  height: auto;
}

p,
code,
pre,
blockquote,
ul,
ol,
li,
figure,
.wp-caption {
  margin: 0 0 30px 0;
}

p > img:only-child,
p > a:only-child > img:only-child,
.wp-caption img,
figure img {
  display: block;
}

.caption,
.wp-caption-text,
figcaption {
  font-size: 0.9em;
  font-style: italic;
}

code,
pre {
  white-space: pre-wrap;
}

blockquote {
  padding: 0;
  -webkit-padding-start: 16px;
}

ul,
ol {
  padding: 0;
}

ul {
  -webkit-padding-start: 30px;
  list-style: disc;
}

ol {
  -webkit-padding-start: 30px;
  list-style: decimal;
}

/* Hide elements with common "hidden" class names */
.visually-hidden,
.visuallyhidden,
.hidden,
.invisible,
.sr-only {
  display: none;
}

article, body {
  /*margin: 20px auto;
  width: 640px;*/
  font-size: 18px;
  word-wrap: break-word;
}

body {
  margin: 24px 24px 24px 24px;
}

article {
  margin: auto;
  max-width: 640px;
}

mark {
  padding: 2px;
  margin: -2px;
  border-radius: 3px;
  background: #d7d7d8;
}

body.dark mark {
  background: #282828;
  color: #efefef;
}
"""

dark_mode_css = """
body, table, tbody, tr, td {
  background-color: #181818;
}

body, article, p, h1, h2, h3, h4, h5, h6, h7, table {
  color: white !important;
}
"""

from lxml.html import html5parser, tostring as html_tostring
from gettext import gettext as _

# Thanks to Eloi Rivard (azmeuk) for the contribution on the media block

_build_media_text = lambda title, content: f'''
    <p>
        <strong>{title}:</strong>
        {content}
    </p>'''

_build_media_link = lambda title, content, link: _build_media_text(
    title, f'<a href="{link}">{content}</a>'
)

# thumbnails aren't supposed to be links, images can be?
# funnily enough, using `#` as a link opens the main content url
# that's because the webkitview sets the base url to the feed item link
_build_media_img = lambda title, imgurl, link='#': _build_media_link(
    title, f'<br /><img src="{imgurl}" />', link
)


# fp_item should be a FeedItem.fp_item
def build_reader_html(og_html, dark_mode=False, fp_item=None):
    assert og_html != None
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
        except:
            article_s = '<h1><i>'+_('Reader mode unavailable for this site')+'</i></h1>'
        return article_s

    def build_media_block():
        if not fp_item: return ''
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
                except:
                    continue
        return media_s if media_s != '<hr />' else ''

    article_s = extract_useful_content()
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
