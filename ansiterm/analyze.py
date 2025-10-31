"""ANSI art analysis and heuristics.

Provides heuristics for:
- Width/height estimation
- iCE color detection
- Cursor addressing detection
- SAUCE presence
"""

import re
from dataclasses import dataclass
from pathlib import Path

from .sauce import has_sauce, strip_sauce_tail


@dataclass
class Analysis:
    """Analysis results for ANSI art file.

    Attributes:
        has_sauce: SAUCE metadata block present
        uses_ice: Uses iCE colors (blink for bright backgrounds)
        est_cols: Estimated width in columns
        est_rows: Estimated height in rows
        has_cup: Uses cursor positioning (ESC[row;colH)
        suggested_width: Recommended terminal width (80 or 132)
        suggested_height: Recommended terminal height (usually 25)
    """

    has_sauce: bool
    uses_ice: bool
    est_cols: int
    est_rows: int
    has_cup: bool
    suggested_width: int
    suggested_height: int


def analyze_bytes(data: bytes) -> Analysis:
    """Analyze ANSI art data and provide heuristics.

    Args:
        data: Raw ANSI art bytes (possibly with SAUCE)

    Returns:
        Analysis results with heuristics

    Examples:
        >>> data = Path("banner.ans").read_bytes()
        >>> analysis = analyze_bytes(data)
        >>> print(f"Suggested size: {analysis.suggested_width}x{analysis.suggested_height}")
        Suggested size: 80x25
    """
    # Check SAUCE
    sauce_present = has_sauce(data)
    clean = strip_sauce_tail(data)

    # Decode as CP437
    try:
        text = clean.decode("cp437", errors="replace")
    except Exception:
        text = str(clean)

    # Check for iCE colors (blink + background)
    uses_ice = bool(re.search(r"\x1b\[[^m]*5[^m]*[4][0-7]m", text))

    # Check for cursor positioning
    has_cup = bool(re.search(r"\x1b\[\d+;\d+[Hf]", text))

    # Estimate dimensions by analyzing visible content
    lines = []
    current_col = 0
    max_col = 0

    i = 0
    while i < len(text):
        if text[i] == "\n":
            lines.append(max_col)
            max_col = max(max_col, current_col)
            current_col = 0
            i += 1
        elif text[i] == "\r":
            current_col = 0
            i += 1
        elif text[i] == "\x1b":
            # Skip escape sequence
            j = i + 1
            if j < len(text) and text[j] == "[":
                j += 1
                while j < len(text) and text[j] in "0123456789;?":
                    j += 1
                if j < len(text):
                    j += 1  # Final byte
            i = j
        else:
            current_col += 1
            i += 1

    lines.append(max_col)
    est_rows = len(lines)
    est_cols = max(lines) if lines else 0

    # Suggest dimensions
    # 132 if any line > 100 or est_cols > 100
    if est_cols > 100:
        suggested_width = 132
    else:
        suggested_width = 80

    # Most BBS art is 25 rows
    if est_rows > 25 and est_rows <= 50:
        suggested_height = 50
    elif est_rows > 50:
        suggested_height = max(25, est_rows)
    else:
        suggested_height = 25

    return Analysis(
        has_sauce=sauce_present,
        uses_ice=uses_ice,
        est_cols=est_cols,
        est_rows=est_rows,
        has_cup=has_cup,
        suggested_width=suggested_width,
        suggested_height=suggested_height,
    )


def analyze_file(path: str | Path) -> Analysis:
    """Analyze an ANSI art file.

    Convenience wrapper around analyze_bytes() that handles file reading.

    Args:
        path: Path to .ANS file

    Returns:
        Analysis results

    Examples:
        >>> analysis = analyze_file("banner.ans")
        >>> if analysis.uses_ice:
        ...     print("This art uses iCE colors")
    """
    path = Path(path)
    data = path.read_bytes()
    return analyze_bytes(data)
