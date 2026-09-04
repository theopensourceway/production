import os
import re
import sys

sys.path.insert(0, os.path.abspath("tools/sphinx_ext"))

project = "The Open Source Way"
author = "The Open Source Way contributors"
guidebook_version = os.environ.get("GUIDEBOOK_VERSION", "dev")
version = guidebook_version.removeprefix("v")

extensions = ["myst_parser", "cjk_emphasis"]
templates_path = [os.path.abspath("_templates")]
html_static_path = [os.path.abspath("_static")]
html_css_files = ["custom.css"]

source_suffix = {
    ".md": "markdown",
}
root_doc = "index"
exclude_patterns = [
    ".git",
    ".venv",
    "_build",
    "_staging",
    "l10n/**",
    "SUMMARY.md",
]

# Translation catalogs live in the editorial repo (the guidebook submodule),
# so they sit next to the English source they translate. The production build
# consumes them from there; there is no separate copy in this repository.
locale_dirs = [os.path.abspath("guidebook/locales")]
gettext_compact = False

myst_enable_extensions = ["colon_fence", "tasklist"]
myst_heading_anchors = 3

# Sites that reject the linkcheck bot with HTTP 403 (and similar) in CI even
# though the URLs resolve fine in a browser. linkcheck is advisory, but these
# patterns keep the report focused on genuinely broken links. Genuine 404s and
# anchor problems are intentionally NOT listed here so they stay visible.
linkcheck_ignore = [
    r"https://www\.bls\.gov/",
    r"https://www\.nytimes\.com/",
    r"https://www\.unwomen\.org/",
    r"https://www\.weforum\.org/",
    r"https://academic\.oup\.com/",
    r"https://.*\.wiley\.com/",
    r"https://www\.huffpost\.com/",
    r"https://www\.managers\.org\.uk/",
    r"https://www\.mayoclinic\.org/",
    r"https://www\.teamblind\.com/",
    r"https://www\.theburnoutproject\.com\.au/",
    r"https://www\.opavote\.com/",
]

language = "en"
guidebook_languages = [
    {"code": "en", "build_dir": "en", "label": "English", "aliases": []},
    {"code": "zh_CN", "build_dir": "zh_CN", "label": "简体中文", "aliases": ["zh"]},
]

# EPUB metadata shared by every language build. Language-specific values and a
# stable package identifier are filled in after command-line configuration
# overrides (for example, ``-D language=zh_CN``) have been applied.
epub_title = project
epub_author = author
epub_contributor = "The Open Source Way community"
epub_description = (
    "A guidebook for open source community management and participation."
)
epub_publisher = "The Open Source Way"
epub_copyright = "The Open Source Way contributors; licensed under CC BY-SA 4.0"
epub_scheme = "ID"
epub_show_urls = "footnote"
epub_tocdepth = 3
epub_css_files = ["epub-custom.css"]

html_theme = "sphinx_book_theme"
html_title = project
html_theme_options = {
    # The repository button and edit/issue links point at the guidebook repo,
    # which holds the editorial content most readers will want to report on.
    "repository_url": "https://github.com/theopensourceway/guidebook",
    "repository_branch": "main",
    "path_to_docs": "",
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_repository_button": True,
    "use_download_button": False,
    # A secondary icon link points at the production repo for build toolchain,
    # CI, and theme issues.
    "icon_links": [
        {
            "name": "Build toolchain (production)",
            "url": "https://github.com/theopensourceway/production",
            "icon": "fa-solid fa-screwdriver-wrench",
            "type": "fontawesome",
        },
    ],
    "home_page_in_toc": True,
    "show_navbar_depth": 1,
    "max_navbar_depth": 3,
    "show_toc_level": 2,
    "toc_title": "On this page",
}
latex_engine = "xelatex"
latex_documents = [
    (root_doc, "the-open-source-way.tex", project, author, "manual"),
]
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": r"""
\usepackage{xeCJK}
\setCJKmainfont{Noto Serif CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}
""",
}
html_sidebars = {
    "**": [
        "navbar-logo.html",
        "icon-links.html",
        "search-button-field.html",
        "language_switcher.html",
        "sbt-sidebar-nav.html",
    ]
}


def setup(app):
    def configure_epub_metadata(app, config):
        language_tag = "zh-CN" if config.language == "zh_CN" else config.language
        release_value = guidebook_version or "dev"
        release_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", release_value).strip("-")
        release_slug = release_slug or "dev"
        identifier_token = re.sub(r"[^A-Za-z0-9_]", "_", release_slug)
        language_token = re.sub(r"[^A-Za-z0-9_]", "_", language_tag)
        identifier = (
            f"theOpenSourceWayGuidebook_{identifier_token}_{language_token}"
        )

        config.epub_language = language_tag
        config.epub_basename = (
            f"the-open-source-way-{release_slug}-{language_tag}"
        )
        # Sphinx writes epub_identifier to the OPF package and epub_uid to the
        # legacy NCX. EPUBCheck requires the two identifiers to match.
        config.epub_identifier = identifier
        config.epub_uid = identifier

        if config.language == "zh_CN":
            config.epub_title = "The Open Source Way（简体中文）"
            config.epub_description = "开源社区管理与参与指南。"

    def localize_theme_options(app, config):
        if config.language == "zh_CN":
            config.html_theme_options["toc_title"] = "本页内容"

    def add_language_context(app, pagename, templatename, context, doctree):
        context["guidebook_current_language"] = app.config.language
        context["guidebook_languages"] = guidebook_languages

    def make_epub_inputs_xhtml_safe(
        app, pagename, templatename, context, doctree
    ):
        if app.builder.name == "epub" and "body" in context:
            # MyST task lists emit HTML-style void elements. EPUB XHTML
            # requires them to be explicitly self-closing.
            context["body"] = re.sub(
                r"(<input\b[^>]*?)(?<!/)>\s*", r"\1 />", context["body"]
            )

    app.connect("config-inited", configure_epub_metadata)
    app.connect("config-inited", localize_theme_options)
    app.connect("html-page-context", add_language_context)
    app.connect("html-page-context", make_epub_inputs_xhtml_safe)
