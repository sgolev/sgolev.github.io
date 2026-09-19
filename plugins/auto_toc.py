"""Auto-generate a table of contents for articles.

The `markdown.extensions.toc` extension already gives every heading an `id`;
this plugin reads those headings back out of the rendered HTML and exposes a
nested `<ul>` as `article.toc`, which templates/article.html renders.

Doing it here rather than with a `[TOC]` marker keeps the Markdown sources free
of layout directives, and rather than in JS keeps the TOC in the served HTML.

Settings (all optional):
  TOC_MIN_HEADINGS  Articles with fewer headings get no TOC at all (default 3).
  TOC_MAX_DEPTH     Levels to include, counted from the shallowest heading in
                    the article (default 3), so `#`- and `##`-rooted articles
                    behave the same.
"""

import re
from html import escape
from html.parser import HTMLParser

from pelican import signals

# Headings as python-markdown emits them: one tag, id attribute always present
# unless the author disabled it with {: .no-toc } / an explicit attr_list.
_HEADING_RE = re.compile(r"<h([1-6])([^>]*)>(.*?)</h\1>", re.DOTALL | re.IGNORECASE)
_ID_RE = re.compile(r"""\bid=["']([^"']+)["']""", re.IGNORECASE)

# Inline markup worth keeping in an entry (e.g. `# \`await\`-ing a task`).
# Everything else is unwrapped to its text, so no nested <a> can appear.
_KEEP_TAGS = {"code", "em", "strong", "b", "i", "sub", "sup", "kbd", "abbr", "span"}


class _EntryText(HTMLParser):
    """Reduce a heading's inner HTML to text plus a few safe inline tags."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag in _KEEP_TAGS:
            self._parts.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag in _KEEP_TAGS:
            self._parts.append(f"</{tag}>")

    def handle_data(self, data):
        self._parts.append(escape(data, quote=False))

    @property
    def text(self):
        return "".join(self._parts).strip()


def _entry_text(inner_html):
    parser = _EntryText()
    parser.feed(inner_html)
    parser.close()
    return parser.text


def _collect(content_html, max_depth):
    """Return [(level, anchor, text)] for the headings that belong in the TOC."""
    headings = []
    for match in _HEADING_RE.finditer(content_html):
        anchor = _ID_RE.search(match.group(2))
        if not anchor:
            continue
        text = _entry_text(match.group(3))
        if text:
            headings.append([int(match.group(1)), anchor.group(1), text])

    if not headings:
        return []

    # Normalise: the shallowest heading in the article becomes level 1.
    top = min(level for level, _, _ in headings)
    return [(lvl - top + 1, a, t) for lvl, a, t in headings if lvl - top < max_depth]


def _render(headings):
    """Turn the flat heading list into nested <ul>s, closing tags in order."""
    parts = []
    open_levels = []
    for level, anchor, text in headings:
        while open_levels and level < open_levels[-1]:
            parts.append("</li></ul>")
            open_levels.pop()
        if open_levels and level == open_levels[-1]:
            parts.append("</li>")
        else:
            parts.append("<ul>")
            open_levels.append(level)
        parts.append(f'<li><a href="#{anchor}">{text}</a>')
    parts.extend("</li></ul>" for _ in open_levels)
    return "".join(parts)


def add_toc(content):
    html = getattr(content, "_content", None)
    if not html:
        return

    settings = content.settings
    headings = _collect(html, settings.get("TOC_MAX_DEPTH", 3))
    if len(headings) < settings.get("TOC_MIN_HEADINGS", 3):
        return

    content.toc = _render(headings)


def register():
    signals.content_object_init.connect(add_toc)
