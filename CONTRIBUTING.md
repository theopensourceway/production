# Contributing to The Open Source Way Production

This repository manages the build and translation toolchain for The Open Source Way guidebook. For editorial contributions (content, writing, editing), see the [guidebook repository](https://github.com/theopensourceway/guidebook) instead.

## Building docs

Install [uv](https://docs.astral.sh/uv/) and run:

```bash
uv sync
uv run sphinx-build -b html -c . guidebook _build/html/en
```

## Translation workflow

Translation catalogs live in the `guidebook/locales/` directory (part of the guidebook submodule). To refresh catalogs after source changes:

```bash
SOURCE_DATE_EPOCH=0 uv run sphinx-build -b gettext -c . guidebook _build/gettext
uv run sphinx-intl update -p _build/gettext -l zh_CN --locale-dir guidebook/locales
uv run python tools/i18n/normalize_po_files.py --locale-dir guidebook/locales
```

Check catalog status:

```bash
uv run python tools/i18n/catalog_status.py --locale-dir guidebook/locales
```

## Building PDFs

Requires XeLaTeX and `latexmk` locally. CI installs these automatically.

```bash
uv run sphinx-build -M latexpdf -c . guidebook _build/pdf/en
uv run sphinx-build -M latexpdf -c . -D language=zh_CN guidebook _build/pdf/zh_CN
```

## Community

For project-wide contribution guidelines, see the [guidebook CONTRIBUTING.md](https://github.com/theopensourceway/guidebook/blob/main/CONTRIBUTING.md).
