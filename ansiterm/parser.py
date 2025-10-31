"""ANSI escape sequence parser and iCE color mapper.

This module provides:
- Minimal ANSI tokenization (SGR, CUP, ED, EL)
- iCE color mapping (blink bit -> bright backgrounds)
- Safety filtering (drop dangerous sequences)

We don't need a full DEC VT parser - just enough for BBS art.
"""

import re
from typing import Iterator


def ice_fix(text: str) -> str:
    """Map iCE colors: blink (SGR 5) + background (40-47) -> bright background (100-107).

    Historical BBS boards used the "blink" attribute bit to enable bright backgrounds
    (iCE colors). Modern terminals ignore blink, so we map it explicitly.

    This function rewrites SGR sequences: if both blink (5) and a background color
    (40-47) appear together, we convert the background to bright (100-107) and
    drop the blink.

    Args:
        text: Text with ANSI escape sequences

    Returns:
        Text with iCE colors mapped to bright backgrounds

    Examples:
        >>> ice_fix("\\x1b[5;44mTEXT\\x1b[0m")
        '\\x1b[104mTEXT\\x1b[0m'  # Blink dropped, bg 44 -> 104
    """
    _sgr = re.compile(r"\x1b\[([0-9;]*)m")

    def repl(match):
        raw = match.group(1)
        if not raw:
            return match.group(0)

        try:
            params = [int(p) for p in raw.split(";") if p]
        except ValueError:
            return match.group(0)

        # Check if blink (5) present
        if 5 not in params:
            return match.group(0)

        # Map blink + background (40-47) to bright background (100-107)
        out = []
        for p in params:
            if 40 <= p <= 47:
                out.append(p + 60)  # 40->100, 41->101, ..., 47->107
            elif p != 5:  # Drop blink
                out.append(p)

        return f"\x1b[{';'.join(map(str, out))}m"

    return _sgr.sub(repl, text)


def tokenize_ansi(text: str, safe_mode: bool = True) -> Iterator[tuple[str, str]]:
    """Tokenize ANSI escape sequences.

    Yields tokens as (type, content) pairs:
    - ("text", "...") - Plain text
    - ("sgr", "...") - SGR color/attribute
    - ("cup", "...") - Cursor position
    - ("ed", "...") - Erase display
    - ("el", "...") - Erase line
    - ("dec", "...") - DEC private mode
    - ("other", "...") - Other CSI
    - ("drop", "...") - Dangerous sequence (if safe_mode)

    Args:
        text: Text with ANSI sequences
        safe_mode: If True, identify dangerous sequences as "drop"

    Yields:
        (token_type, content) pairs

    Examples:
        >>> list(tokenize_ansi("Hello \\x1b[31mWorld\\x1b[0m"))
        [('text', 'Hello '), ('sgr', '\\x1b[31m'), ('text', 'World'), ('sgr', '\\x1b[0m')]
    """
    i = 0
    while i < len(text):
        # Check for ESC
        if text[i] == "\x1b" and i + 1 < len(text):
            # CSI sequence: ESC [
            if text[i + 1] == "[":
                # Find final byte
                j = i + 2
                while j < len(text) and text[j] in "0123456789;?":
                    j += 1

                if j < len(text):
                    final = text[j]
                    seq = text[i : j + 1]

                    # Classify by final byte
                    if final == "m":
                        yield ("sgr", seq)
                    elif final in "Hf":
                        yield ("cup", seq)
                    elif final in "ABCD":  # Cursor movement (Up, Down, Right, Left)
                        yield ("cursor_move", seq)
                    elif final == "J":
                        yield ("ed", seq)
                    elif final == "K":
                        yield ("el", seq)
                    elif final in "hl" and "?" in seq:
                        yield ("dec", seq)
                    elif final in "su":  # Save/restore cursor
                        yield ("cursor_save", seq)
                    elif safe_mode:
                        yield ("drop", seq)  # Unknown in safe mode
                    else:
                        yield ("other", seq)

                    i = j + 1
                    continue

            # OSC sequence: ESC ]
            elif text[i + 1] == "]" and safe_mode:
                # OSC is dangerous (can set title, clipboard, etc.)
                # Find terminator (BEL or ESC \)
                j = i + 2
                while j < len(text):
                    if text[j] == "\x07":  # BEL
                        yield ("drop", text[i : j + 1])
                        i = j + 1
                        break
                    elif text[j : j + 2] == "\x1b\\":  # ESC backslash
                        yield ("drop", text[i : j + 2])
                        i = j + 2
                        break
                    j += 1
                else:
                    # No terminator found, consume rest
                    yield ("drop", text[i:])
                    break
                continue

        # Regular text
        next_esc = text.find("\x1b", i)
        if next_esc == -1:
            yield ("text", text[i:])
            break
        else:
            if next_esc > i:
                yield ("text", text[i:next_esc])
            i = next_esc


def filter_safe(text: str) -> str:
    """Filter text, keeping only safe ANSI sequences.

    Drops:
    - OSC (operating system commands)
    - Unknown CSI sequences
    - Anything that could affect terminal outside display area

    Keeps:
    - SGR (colors/attributes)
    - CUP (cursor positioning - absolute)
    - Cursor movement (relative: up, down, left, right)
    - Cursor save/restore
    - ED/EL (erase display/line)
    - DEC private modes we support

    Args:
        text: Text with ANSI sequences

    Returns:
        Text with only safe sequences

    Examples:
        >>> filter_safe("\\x1b[31mRed\\x1b]0;Title\\x07")
        '\\x1b[31mRed'  # OSC dropped
    """
    result = []
    for token_type, content in tokenize_ansi(text, safe_mode=True):
        if token_type != "drop":
            result.append(content)
    return "".join(result)
