# The Open Source Way — Production

This repository contains the production toolchain for building and translating [The Open Source Way](https://github.com/theopensourceway/guidebook) guidebook.

The editorial source lives in the `guidebook/` submodule. This repo provides Sphinx/MyST build configuration, translation tooling, CI workflows, and theme customization.

## Quick start

```bash
# Clone with submodule
git clone --recurse-submodules https://github.com/theopensourceway/production.git
cd production

# Install toolchain
uv sync

# Build English HTML
uv run sphinx-build -b html -c . guidebook _build/html/en

# Build Chinese HTML
uv run sphinx-build -b html -c . -D language=zh_CN guidebook _build/html/zh_CN
```

## Building PDFs

Requires XeLaTeX and `latexmk`:

```bash
uv run sphinx-build -M latexpdf -c . guidebook _build/pdf/en
uv run sphinx-build -M latexpdf -c . -D language=zh_CN guidebook _build/pdf/zh_CN
```

## Translation workflow

```bash
# Extract translatable strings
SOURCE_DATE_EPOCH=0 uv run sphinx-build -b gettext -c . guidebook _build/gettext

# Update zh_CN catalogs
uv run sphinx-intl update -p _build/gettext -l zh_CN --locale-dir guidebook/locales

# Normalize and check status
uv run python tools/i18n/normalize_po_files.py --locale-dir guidebook/locales
uv run python tools/i18n/catalog_status.py --locale-dir guidebook/locales
```

## Repository layout

```
.
├── conf.py              # Sphinx configuration
├── pyproject.toml       # uv-managed dependencies
├── _static/             # Custom CSS
├── _templates/          # Jinja templates (language switcher)
├── tools/i18n/          # Translation utility scripts
├── .github/workflows/   # CI: build, PDF, Pages, linkcheck
└── guidebook/           # Editorial source (git submodule)
    ├── index.md
    ├── locales/zh_CN/   # Translation catalogs
    └── ...
```
