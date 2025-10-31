"""Programmatic ANSI art generation.

The AnsiBuilder provides a fluent API for creating ANSI art without
manually writing escape sequences.

Examples:
    >>> b = AnsiBuilder(80, 25)
    >>> b.clear().home()
    >>> b.fg(15, bright=True).bg(4)
    >>> b.move(10, 20).text("╔═══ AMPLIFIER ═══╗")
    >>> data = b.to_bytes(add_sauce=True, title="Banner", author="AI")
"""

from .sauce import append_minimal_sauce


class AnsiBuilder:
    """Builder for programmatic ANSI art generation.

    Provides a fluent API for constructing ANSI art with proper escape sequences.
    All methods return self for chaining.

    Attributes:
        width: Target width in columns
        height: Target height in rows
        buf: Internal buffer of text and escape sequences
    """

    def __init__(self, width: int = 80, height: int = 25):
        """Initialize builder.

        Args:
            width: Target width (default: 80)
            height: Target height (default: 25)
        """
        self.width = width
        self.height = height
        self.buf: list[str] = []

    # === Control Sequences ===

    def sgr(self, *params: int) -> "AnsiBuilder":
        """Add SGR (Select Graphic Rendition) sequence.

        Args:
            *params: SGR parameters (e.g., 0=reset, 1=bold, 31=red fg)

        Returns:
            Self for chaining
        """
        self.buf.append(f"\x1b[{';'.join(map(str, params))}m")
        return self

    def move(self, row: int, col: int) -> "AnsiBuilder":
        """Move cursor to position (1-indexed).

        Args:
            row: Row number (1-based)
            col: Column number (1-based)

        Returns:
            Self for chaining
        """
        self.buf.append(f"\x1b[{row};{col}H")
        return self

    def clear(self) -> "AnsiBuilder":
        """Clear entire display.

        Returns:
            Self for chaining
        """
        self.buf.append("\x1b[2J")
        return self

    def home(self) -> "AnsiBuilder":
        """Move cursor to home position (1,1).

        Returns:
            Self for chaining
        """
        self.buf.append("\x1b[H")
        return self

    # === Helper Methods ===

    def fg(self, n: int, bright: bool = False) -> "AnsiBuilder":
        """Set foreground color.

        Args:
            n: Color number (0-7)
            bright: Use bright variant (adds 60)

        Returns:
            Self for chaining

        Examples:
            >>> b.fg(1)       # Red
            >>> b.fg(1, True) # Bright red
        """
        code = 30 + n if not bright else 90 + n
        self.sgr(code)
        return self

    def bg(self, n: int, bright: bool = False) -> "AnsiBuilder":
        """Set background color.

        Args:
            n: Color number (0-7)
            bright: Use bright variant (adds 60)

        Returns:
            Self for chaining

        Examples:
            >>> b.bg(4)       # Blue background
            >>> b.bg(4, True) # Bright blue background
        """
        code = 40 + n if not bright else 100 + n
        self.sgr(code)
        return self

    def reset(self) -> "AnsiBuilder":
        """Reset all attributes (colors, bold, etc).

        Returns:
            Self for chaining
        """
        self.sgr(0)
        return self

    def bold(self) -> "AnsiBuilder":
        """Enable bold.

        Returns:
            Self for chaining
        """
        self.sgr(1)
        return self

    def dim(self) -> "AnsiBuilder":
        """Enable dim.

        Returns:
            Self for chaining
        """
        self.sgr(2)
        return self

    # === Content ===

    def text(self, s: str) -> "AnsiBuilder":
        """Append text (Unicode).

        Args:
            s: Text to append

        Returns:
            Self for chaining
        """
        self.buf.append(s)
        return self

    def cp437(self, b: bytes) -> "AnsiBuilder":
        """Append CP437-encoded bytes.

        Args:
            b: CP437 bytes

        Returns:
            Self for chaining
        """
        self.buf.append(b.decode("cp437", errors="replace"))
        return self

    def newline(self) -> "AnsiBuilder":
        """Append newline.

        Returns:
            Self for chaining
        """
        self.buf.append("\n")
        return self

    # === Export ===

    def to_text(self) -> str:
        """Export as text string.

        Returns:
            Complete ANSI art as Unicode string
        """
        return "".join(self.buf)

    def to_bytes(
        self,
        codec: str = "cp437",
        add_sauce: bool = False,
        **sauce_kwargs,
    ) -> bytes:
        """Export as CP437 bytes, optionally with SAUCE.

        Args:
            codec: Encoding (default: cp437)
            add_sauce: Add SAUCE metadata block
            **sauce_kwargs: Arguments for append_minimal_sauce()
                          (title, author, group, etc.)

        Returns:
            Complete ANSI art as bytes

        Examples:
            >>> b = AnsiBuilder()
            >>> b.text("Hello")
            >>> data = b.to_bytes(add_sauce=True, title="Hello", author="AI")
        """
        text = self.to_text()
        data = text.encode(codec, errors="replace")

        if add_sauce:
            # Add width/height if not provided
            if "tinfo1" not in sauce_kwargs:
                sauce_kwargs["tinfo1"] = self.width
            if "tinfo2" not in sauce_kwargs:
                sauce_kwargs["tinfo2"] = self.height

            data = append_minimal_sauce(data, **sauce_kwargs)

        return data
