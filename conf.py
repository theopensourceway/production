import os
import sys

sys.path.insert(0, os.path.abspath("tools/sphinx_ext"))

project = "The Open Source Way"
author = "The Open Source Way contributors"

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

locale_dirs = [os.path.abspath("locales")]
gettext_compact = False

myst_enable_extensions = ["colon_fence", "tasklist"]
myst_heading_anchors = 3

language = "en"
guidebook_languages = [
    {"code": "en", "build_dir": "en", "label": "English", "aliases": []},
    {"code": "zh_CN", "build_dir": "zh_CN", "label": "简体中文", "aliases": ["zh"]},
]
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
    def localize_theme_options(app, config):
        if config.language == "zh_CN":
            config.html_theme_options["toc_title"] = "本页内容"

    def add_language_context(app, pagename, templatename, context, doctree):
        context["guidebook_current_language"] = app.config.language
        context["guidebook_languages"] = guidebook_languages

    app.connect("config-inited", localize_theme_options)
    app.connect("html-page-context", add_language_context)
