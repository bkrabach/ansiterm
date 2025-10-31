"""Tests for SAUCE metadata handling."""

from ansiterm.sauce import append_minimal_sauce, has_sauce, strip_sauce_tail


def test_has_sauce():
    """Test SAUCE detection."""
    # No SAUCE
    assert not has_sauce(b"Just some content")

    # With SAUCE (128 bytes, starts with "SAUCE")
    sauce_block = b"SAUCE00" + b"\x00" * 121
    data_with_sauce = b"Content" + sauce_block
    assert has_sauce(data_with_sauce)

    # Too short
    assert not has_sauce(b"SAU")


def test_strip_sauce_tail():
    """Test SAUCE removal."""
    # No SAUCE - unchanged
    original = b"Just some content"
    assert strip_sauce_tail(original) == original

    # With SAUCE - removed
    sauce_block = b"SAUCE00" + b"\x00" * 121
    data_with_sauce = b"Content" + sauce_block
    assert strip_sauce_tail(data_with_sauce) == b"Content"


def test_append_minimal_sauce():
    """Test SAUCE creation."""
    content = b"ANSI art content"

    result = append_minimal_sauce(
        content,
        title="Test Art",
        author="Test Author",
        group="Test Group",
        tinfo1=80,
        tinfo2=25,
    )

    # Result is original + 128 bytes
    assert len(result) == len(content) + 128

    # Result has SAUCE
    assert has_sauce(result)

    # Stripping gives back original
    assert strip_sauce_tail(result) == content


def test_sauce_round_trip():
    """Test SAUCE add/strip round-trip."""
    original = b"Some ANSI art"

    with_sauce = append_minimal_sauce(original, title="Test", author="AI")
    stripped = strip_sauce_tail(with_sauce)

    assert stripped == original
