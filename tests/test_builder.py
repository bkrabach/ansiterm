"""Tests for AnsiBuilder API."""

from ansiterm.builder import AnsiBuilder
from ansiterm.sauce import has_sauce


def test_builder_basic():
    """Test basic builder operations."""
    b = AnsiBuilder()
    b.clear().home()
    b.text("Hello")

    result = b.to_text()
    assert "\x1b[2J" in result  # Clear
    assert "\x1b[H" in result  # Home
    assert "Hello" in result


def test_builder_colors():
    """Test color methods."""
    b = AnsiBuilder()
    b.fg(1).text("Red")  # Red foreground
    b.bg(4).text("Blue")  # Blue background

    result = b.to_text()
    assert "\x1b[31m" in result  # FG red (30 + 1)
    assert "\x1b[44m" in result  # BG blue (40 + 4)


def test_builder_bright_colors():
    """Test bright color variants."""
    b = AnsiBuilder()
    b.fg(1, bright=True).text("Bright Red")

    result = b.to_text()
    assert "\x1b[91m" in result  # Bright red (90 + 1)


def test_builder_move():
    """Test cursor positioning."""
    b = AnsiBuilder()
    b.move(10, 20).text("Positioned")

    result = b.to_text()
    assert "\x1b[10;20H" in result
    assert "Positioned" in result


def test_builder_reset():
    """Test reset method."""
    b = AnsiBuilder()
    b.reset()

    result = b.to_text()
    assert "\x1b[0m" in result


def test_builder_to_bytes():
    """Test CP437 encoding."""
    b = AnsiBuilder()
    b.text("Hello")

    data = b.to_bytes()
    assert isinstance(data, bytes)
    assert b"Hello" in data


def test_builder_with_sauce():
    """Test SAUCE addition."""
    b = AnsiBuilder(80, 25)
    b.text("Test")

    data = b.to_bytes(add_sauce=True, title="Test", author="AI")

    # Has SAUCE
    assert has_sauce(data)

    # Original content is there
    assert b"Test" in data[: len(data) - 128]  # Before SAUCE block


def test_builder_chaining():
    """Test fluent API chaining."""
    b = AnsiBuilder()

    # All methods return self
    result = b.clear().home().fg(7).bg(4).text("Chained").reset()

    assert result is b  # Fluent API
    assert "Chained" in b.to_text()
