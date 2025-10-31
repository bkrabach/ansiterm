"""Core ANSI art rendering with terminal control.

This module handles:
- CP437 decoding (BBS character set)
- Terminal state management (alt screen, cursor, wrap)
- iCE color mapping
- Safe rendering (filter dangerous sequences)
- Windows compatibility (colorama)
"""

import os
import sys
from pathlib import Path

from .parser import filter_safe, ice_fix
from .sauce import strip_sauce_tail


def decode_text(data: bytes, codec: str = "cp437") -> str:
    """Decode bytes to text using specified codec.

    Args:
        data: Raw bytes
        codec: Character encoding (default: cp437 for BBS art)

    Returns:
        Decoded text string

    Examples:
        >>> decode_text(b"\\xc9\\xcd\\xbb")  # Box drawing chars
        '╔═╗'
    """
    return data.decode(codec, errors="replace")


def _enter_alt_screen(out):
    """Enter alternate screen with proper terminal setup."""
    # Alt screen + disable wrap + hide cursor + clear + home
    out("\x1b[?1049h\x1b[?7l\x1b[?25l\x1b[2J\x1b[H")


def _exit_alt_screen(out):
    """Exit alternate screen and restore terminal state."""
    # Reset colors + show cursor + enable wrap + leave alt screen
    out("\x1b[0m\x1b[?25h\x1b[?7h\x1b[?1049l")


def render_bytes(
    data: bytes,
    *,
    codec: str = "cp437",
    ice_mode: str = "auto",
    use_alt_screen: bool = True,
    disable_wrap: bool = True,
    hide_cursor: bool = True,
    clear_first: bool = True,
    safe_mode: bool = True,
) -> None:
    """Render ANSI art bytes to the active terminal.

    Properly manages terminal state: enters alt screen, sets modes, renders art,
    and restores everything on exit (even on exceptions).

    Args:
        data: Raw ANSI art bytes (possibly with SAUCE)
        codec: Character encoding (default: cp437)
        ice_mode: iCE color handling ("auto" | "on" | "off")
                 "auto" - map if blink detected
                 "on" - always map blink to bright bg
                 "off" - pass through unchanged
        use_alt_screen: Use alternate screen buffer
        disable_wrap: Disable line wrapping
        hide_cursor: Hide cursor during rendering
        clear_first: Clear screen before rendering
        safe_mode: Filter dangerous escape sequences

    Examples:
        >>> data = Path("banner.ans").read_bytes()
        >>> render_bytes(data)  # Renders to terminal with full state management
    """
    # Windows compatibility
    if os.name == "nt":
        try:
            import colorama

            colorama.just_fix_windows_console()
        except Exception:
            pass  # Colorama optional on Windows

    # Prepare text
    raw = strip_sauce_tail(data)
    text = decode_text(raw, codec)

    # Apply iCE color mapping
    if ice_mode in ("auto", "on"):
        text = ice_fix(text)

    # Apply safety filtering
    if safe_mode:
        text = filter_safe(text)

    # Output function
    out = sys.stdout.write

    try:
        # Enter alt screen with setup
        if use_alt_screen:
            _enter_alt_screen(out)
        else:
            # Partial setup without alt screen
            if disable_wrap:
                out("\x1b[?7l")
            if hide_cursor:
                out("\x1b[?25l")
            if clear_first:
                out("\x1b[2J\x1b[H")

        # Render the art
        out(text)
        sys.stdout.flush()

    finally:
        # Always restore terminal state
        if use_alt_screen:
            _exit_alt_screen(out)
        else:
            # Partial restore
            out("\x1b[0m")  # Reset colors
            if hide_cursor:
                out("\x1b[?25h")  # Show cursor
            if disable_wrap:
                out("\x1b[?7h")  # Enable wrap
        sys.stdout.flush()


def render_text_raw(text: str) -> None:
    """Render ANSI text directly with NO terminal control.

    Use this when you're already managing terminal state (alt screen, cursor, etc).
    This function ONLY writes the text - no setup, no cleanup.

    Args:
        text: Pre-processed ANSI text (already decoded, SAUCE stripped, etc.)
    """
    sys.stdout.write(text)
    sys.stdout.flush()


def render_file(path: str | Path, **kwargs) -> None:
    """Render an ANSI art file to the terminal.

    Convenience wrapper around render_bytes() that handles file reading.

    Args:
        path: Path to .ANS file
        **kwargs: Passed to render_bytes()

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file can't be read

    Examples:
        >>> render_file("splash.ans")
        >>> render_file("banner.ans", ice_mode="on", safe_mode=False)
    """
    path = Path(path)
    data = path.read_bytes()
    render_bytes(data, **kwargs)
