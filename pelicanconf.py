from datetime import datetime

AUTHOR = "Stanislav Golev"
SITENAME = "Stanislav Golev"
SITEURL = ""  # empty for local dev; publishconf.py overrides for production

PATH = "content"
ARTICLE_PATHS = ["articles"]
TIMEZONE = "Europe/Moscow"

DEFAULT_LANG = "en"

THEME = "theme/mytheme"

# ---------------------------------------------------------------------------
# URLs and slugs
# ---------------------------------------------------------------------------
# Slug comes from the *filename*; the URL prepends the publication date:
# content/articles/my-article-title.md + Date: 2026-07-16
#   -> /blog/2026-07-16-my-article-title/
SLUGIFY_SOURCE = "basename"

ARTICLE_URL = "blog/{date:%Y}-{date:%m}-{date:%d}-{slug}/"
ARTICLE_SAVE_AS = "blog/{date:%Y}-{date:%m}-{date:%d}-{slug}/index.html"
PAGE_URL = "{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"

# Generated article listing at /blog/, landing page at the root
DIRECT_TEMPLATES = ["index", "landing"]
INDEX_URL = "blog/"
INDEX_SAVE_AS = "blog/index.html"
LANDING_URL = ""
LANDING_SAVE_AS = "index.html"

# favicon.ico, robots.txt, CNAME etc. go here (copied verbatim)
STATIC_PATHS = ["images"]

# Keep the theme minimal: no per-author/category/tag pages, no direct archives
# Tags are clickable: each gets a listing page under /blog/tag/<slug>/
TAG_URL = "blog/tag/{slug}/"
TAG_SAVE_AS = "blog/tag/{slug}/index.html"
TAGS_SAVE_AS = ""
AUTHOR_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
ARCHIVES_SAVE_AS = ""

DEFAULT_PAGINATION = 20

# ---------------------------------------------------------------------------
# Jinja: enable the 'do' statement used by the publications macro.
# NB: overriding JINJA_ENVIRONMENT replaces Pelican's default wholesale
# (same gotcha as MARKDOWN), so trim/lstrip are restated explicitly.
# ---------------------------------------------------------------------------
JINJA_ENVIRONMENT = {
    "trim_blocks": True,
    "lstrip_blocks": True,
    "extensions": ["jinja2.ext.do"],
}

# ---------------------------------------------------------------------------
# Markdown / syntax highlighting (Pygments via pymdownx)
# ---------------------------------------------------------------------------
MARKDOWN = {
    "extension_configs": {
        "pymdownx.highlight": {
            "css_class": "highlight",
            "guess_lang": False,
        },
        "pymdownx.superfences": {},
        "markdown.extensions.abbr": {},
        "markdown.extensions.attr_list": {},
        "markdown.extensions.def_list": {},
        "markdown.extensions.footnotes": {},
        "markdown.extensions.md_in_html": {},
        "markdown.extensions.tables": {},
        # "markdown.extensions.codehilite": {
        #     "css_class": "highlight",
        #     "linenums": False,
        #     "guess_lang": False,  # always tag your fences: ```python
        # },
        # "markdown.extensions.extra": {},
        "markdown.extensions.toc": {"permalink": ""},
        "markdown.extensions.meta": {},
    },
    "output_format": "html5",
}

# No feeds during local dev
FEED_ALL_RSS = None
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None

# ---------------------------------------------------------------------------
# Social / SEO metadata (rendered by partials/meta.html)
# ---------------------------------------------------------------------------
# Fallback description for the landing page, /blog/ and tag listings.
SITEDESCRIPTION = "My blog"

# Site-wide preview image, overridable per article/page with an `Image:` line
# in the front matter. Site-relative paths get SITEURL prepended; use the size
# below to match the actual file (1200x630 is the safe default for OG).
OG_IMAGE = ""  # e.g. "images/og-default.png"
OG_IMAGE_SIZE = (1200, 630)

# article.lang / DEFAULT_LANG -> og:locale
OG_LOCALES = {"en": "en_US", "ru": "ru_RU"}

# ---------------------------------------------------------------------------
# Publications on other websites, merged into the landing and /blog/ lists.
# Use datetime(...) so entries sort together with local articles.
# ---------------------------------------------------------------------------
EXTERNAL_ARTICLES = [
    {
        "title": "SQL syntax highlighting within Python code",
        "url": "https://telegra.ph/SQL-syntax-highlighting-within-Python-code-11-17",
        "date": datetime(2025, 11, 18),
        "source": "telegra.ph",
        "lang": "en",
    },
    {
        "title": "Синхронизация файлов через почтовый клиент",
        "url": "https://telegra.ph/Sinhronizaciya-fajlov-cherez-pochtovyj-klient-08-13",
        "date": datetime(2024, 8, 14),
        "source": "telegra.ph",
        "lang": "ru",
    },
    {
        "title": "Программное решение задания №2 в ЕГЭ по информатике",
        "url": "https://telegra.ph/Programmnoe-reshenie-zadaniya-2-v-EGEH-po-informatike-06-09",
        "date": datetime(2024, 6, 9),
        "source": "telegra.ph",
        "lang": "ru",
    },
]

# Reading speed used for the "N min" estimate on article pages
READING_WPM = 200

# ---------------------------------------------------------------------------
# giscus (used by article.html)
# ---------------------------------------------------------------------------
# Fill these in from https://giscus.app after enabling Discussions on the repo
GISCUS = {
    "repo": "sgolev/sgolev.github.io",
    "repo_id": "R_kgDOO8MARw",
    "category": "Announcements",
    "category_id": "DIC_kwDOO8MAR84DBwkW",
    "lang": "en",
    "loading": "lazy",
}
