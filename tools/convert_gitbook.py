#!/usr/bin/env python3
"""Convert GitBook-specific Markdown syntax to MyST equivalents.

The guidebook source (a git submodule) still uses GitBook's
``{% hint style="..." %}...{% endhint %}`` callout syntax, which MyST/Sphinx
does not understand and renders as literal text. This script rewrites those
blocks into MyST admonition directives in the staging tree, leaving the
submodule untouched.

Run it over the staging directory after the source has been copied in (see
``tools/prepare-source.sh``).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# GitBook hint style -> MyST admonition directive name. Sphinx ships localized
# titles for these directives, so translations keep working automatically.
_STYLE_TO_DIRECTIVE = {
    "success": "tip",
    "info": "note",
    "warning": "warning",
    "danger": "danger",
}

_HINT_RE = re.compile(
    r'{%\s*hint\s+style="(?P<style>[^"]+)"\s*%}'
    r"(?P<body>.*?)"
    r"{%\s*endhint\s*%}",
    re.DOTALL,
)


def _convert_hint(match: re.Match[str]) -> str:
    style = match.group("style").strip().lower()
    directive = _STYLE_TO_DIRECTIVE.get(style, "note")
    body = match.group("body").strip("\n")
    # Use a colon fence so the body may contain its own Markdown markup.
    return f":::{{{directive}}}\n{body}\n:::"


def convert_text(text: str) -> str:
    return _HINT_RE.sub(_convert_hint, text)


def convert_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    converted = convert_text(original)
    if converted != original:
        path.write_text(converted, encoding="utf-8")
        return True
    return False


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <staging-dir>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    changed = 0
    for md_path in sorted(root.rglob("*.md")):
        if convert_file(md_path):
            changed += 1
            print(f"converted GitBook syntax in {md_path}")
    print(f"GitBook conversion complete ({changed} file(s) changed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
