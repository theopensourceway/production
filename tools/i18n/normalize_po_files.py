from __future__ import annotations

import argparse
from pathlib import Path


def normalize(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    normalized = original.rstrip() + "\n"
    if original == normalized:
        return False
    path.write_text(normalized, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize PO files (trailing newlines).")
    parser.add_argument(
        "--locale-dir",
        default="locales",
        help="Path to the locales root directory (default: locales).",
    )
    args = parser.parse_args()

    locale_dir = Path(args.locale_dir)
    changed = 0
    for path in sorted(locale_dir.rglob("*.po")):
        if normalize(path):
            changed += 1
            print(f"normalized,{path}")
    print(f"summary,normalized-files,{changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
