"""Make MyST/markdown-it emphasis parsing CJK-friendly.

CommonMark's emphasis "flanking" rules were designed for scripts that use
spaces and ASCII punctuation to separate words. They fail for full-width CJK
text in two common ways:

1. ``_斜体_`` directly between CJK characters is left as literal text, because
   ``_`` may not open/close emphasis intra-word and CJK has no spaces.
2. ``**粗体**`` adjacent to CJK punctuation (e.g. ``要诀是：**``) is left as
   literal text, because the full-width punctuation blocks the delimiter run
   from being recognised as right-/left-flanking.

This extension monkeypatches :meth:`markdown_it.rules_inline.state_inline.
StateInline.scanDelims` so that, *only* when a CJK character is adjacent to the
delimiter run, the flanking rules are relaxed:

* CJK punctuation is treated as an ordinary word character (not punctuation),
  which restores ``**...：**`` style emphasis; and
* ``_`` is allowed to split "words" when next to CJK characters, which restores
  ``中文_斜体_中文`` style emphasis.

Latin text is untouched: the relaxations only kick in when a CJK character sits
directly beside the markers, so ``snake_case`` and ordinary English emphasis
behave exactly as before. The fix happens at parse time, so it applies equally
to the English source, the translated (``.po``) content, and every output
format (HTML, LaTeX/PDF).
"""

from __future__ import annotations

from markdown_it.common.utils import isMdAsciiPunct, isPunctChar, isWhiteSpace
from markdown_it.rules_inline.state_inline import Scanned, StateInline

# Unicode ranges that we consider "CJK" for emphasis purposes: ideographs,
# kana, hangul, and the CJK / full-width punctuation that surrounds them.
_CJK_RANGES = (
    (0x1100, 0x11FF),    # Hangul Jamo
    (0x2E80, 0x2EFF),    # CJK Radicals Supplement
    (0x3000, 0x303F),    # CJK Symbols and Punctuation (。、「」（）…)
    (0x3040, 0x30FF),    # Hiragana + Katakana
    (0x3130, 0x318F),    # Hangul Compatibility Jamo
    (0x3400, 0x4DBF),    # CJK Unified Ideographs Extension A
    (0x4E00, 0x9FFF),    # CJK Unified Ideographs
    (0xAC00, 0xD7AF),    # Hangul Syllables
    (0xF900, 0xFAFF),    # CJK Compatibility Ideographs
    (0xFF00, 0xFFEF),    # Halfwidth and Fullwidth Forms (：！？（）)
    (0x20000, 0x2FA1F),  # CJK Unified Ideographs Extensions B–F + supplement
)


def _is_cjk(char: str) -> bool:
    if not char:
        return False
    code = ord(char)
    for start, end in _CJK_RANGES:
        if start <= code <= end:
            return True
    return False


def _scan_delims_cjk(self: StateInline, start: int, canSplitWord: bool) -> Scanned:
    pos = start
    maximum = self.posMax
    marker = self.src[start]

    # treat beginning of the line as a whitespace
    lastChar = self.src[start - 1] if start > 0 else " "

    while pos < maximum and self.src[pos] == marker:
        pos += 1

    count = pos - start

    # treat end of the line as a whitespace
    nextChar = self.src[pos] if pos < maximum else " "

    last_is_cjk = _is_cjk(lastChar)
    next_is_cjk = _is_cjk(nextChar)

    # CJK punctuation is treated as an ordinary word character so that
    # ``**...：**`` style runs flank correctly.
    isLastPunctChar = (
        isMdAsciiPunct(ord(lastChar)) or isPunctChar(lastChar)
    ) and not last_is_cjk
    isNextPunctChar = (
        isMdAsciiPunct(ord(nextChar)) or isPunctChar(nextChar)
    ) and not next_is_cjk

    isLastWhiteSpace = isWhiteSpace(ord(lastChar))
    isNextWhiteSpace = isWhiteSpace(ord(nextChar))

    # Allow ``_`` to split "words" when it sits next to CJK characters, which
    # have no spaces to delimit emphasis.
    if last_is_cjk or next_is_cjk:
        canSplitWord = True

    left_flanking = not (
        isNextWhiteSpace
        or (isNextPunctChar and not (isLastWhiteSpace or isLastPunctChar))
    )
    right_flanking = not (
        isLastWhiteSpace
        or (isLastPunctChar and not (isNextWhiteSpace or isNextPunctChar))
    )

    can_open = left_flanking and (
        canSplitWord or (not right_flanking) or isLastPunctChar
    )
    can_close = right_flanking and (
        canSplitWord or (not left_flanking) or isNextPunctChar
    )

    return Scanned(can_open, can_close, count)


def setup(app):  # noqa: ANN001 - Sphinx extension entry point
    StateInline.scanDelims = _scan_delims_cjk
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
