"""BBS-style ANSI art rendering and authoring library.

This library provides correct, authentic 90s-style ANSI (.ANS) art rendering
with proper CP437 encoding, SAUCE metadata support, iCE color handling, and
terminal state management.

Philosophy:
- Correctness: Authentic BBS art rendering with CP437 and ANSI escape sequences
- Safety: Filter dangerous sequences by default, never trash the terminal
- Portability: Works on Linux, macOS, Windows with minimal dependencies
- Simplicity: Clean API, minimal configuration
"""

__version__ = "1.0.0"

from .analyze import Analysis, analyze_bytes, analyze_file
from .builder import AnsiBuilder
from .render import decode_text, render_bytes, render_file, render_text_raw
from .sauce import append_minimal_sauce, has_sauce, strip_sauce_tail

__all__ = [
    # Rendering
    "render_bytes",
    "render_file",
    "render_text_raw",
    "decode_text",
    # SAUCE
    "strip_sauce_tail",
    "has_sauce",
    "append_minimal_sauce",
    # Analysis
    "analyze_bytes",
    "analyze_file",
    "Analysis",
    # Builder
    "AnsiBuilder",
]
