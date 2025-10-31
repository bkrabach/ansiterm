"""Tests for ANSI parser and iCE color mapping."""

from ansiterm.parser import filter_safe, ice_fix, tokenize_ansi


def test_ice_fix():
    """Test iCE color mapping: blink + bg -> bright bg."""
    # Blink (5) + blue background (44) -> bright blue bg (104)
    input_text = "\x1b[5;44mTEXT\x1b[0m"
    expected = "\x1b[104mTEXT\x1b[0m"  # Blink dropped, bg 44->104
    assert ice_fix(input_text) == expected

    # No blink - unchanged
    input_text = "\x1b[44mTEXT\x1b[0m"
    assert ice_fix(input_text) == input_text

    # Blink without background - unchanged
    input_text = "\x1b[5;31mTEXT\x1b[0m"  # Blink + red foreground
    # Just drop blink, keep fg
    expected = "\x1b[31mTEXT\x1b[0m"
    assert ice_fix(input_text) == expected


def test_tokenize_ansi():
    """Test ANSI tokenization."""
    text = "Hello \x1b[31mWorld\x1b[0m"
    tokens = list(tokenize_ansi(text))

    assert tokens[0] == ("text", "Hello ")
    assert tokens[1] == ("sgr", "\x1b[31m")
    assert tokens[2] == ("text", "World")
    assert tokens[3] == ("sgr", "\x1b[0m")


def test_tokenize_ansi_cursor():
    """Test cursor positioning tokenization."""
    text = "\x1b[10;20HText"
    tokens = list(tokenize_ansi(text))

    assert tokens[0] == ("cup", "\x1b[10;20H")
    assert tokens[1] == ("text", "Text")


def test_filter_safe():
    """Test safety filtering."""
    # Safe sequences pass through
    safe = "\x1b[31mRed\x1b[0m"
    assert filter_safe(safe) == safe

    # OSC (title setting) dropped
    dangerous = "\x1b[31mRed\x1b]0;Title\x07"
    filtered = filter_safe(dangerous)
    assert filtered == "\x1b[31mRed"
    assert "Title" not in filtered


def test_tokenize_ansi_safe_mode():
    """Test that safe_mode identifies dangerous sequences."""
    # OSC sequence
    text = "\x1b]0;Title\x07"
    tokens = list(tokenize_ansi(text, safe_mode=True))

    # Should be marked as "drop"
    assert tokens[0][0] == "drop"
