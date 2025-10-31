"""SAUCE metadata handling.

SAUCE (Standard Architecture for Universal Comment Extensions) is a 128-byte
metadata block appended to BBS art files. It contains title, author, group,
date, dimensions, and other metadata.

This module provides minimal SAUCE v00 support:
- Detection: has_sauce()
- Removal: strip_sauce_tail()
- Creation: append_minimal_sauce()
"""

from datetime import datetime
from typing import Optional


def has_sauce(data: bytes) -> bool:
    """Check if data contains a SAUCE block.

    SAUCE is exactly 128 bytes at the end, starting with ASCII "SAUCE".

    Args:
        data: Raw file bytes

    Returns:
        True if SAUCE block detected
    """
    if len(data) < 128:
        return False
    return data[-128:-123] == b"SAUCE"


def strip_sauce_tail(data: bytes) -> bytes:
    """Remove SAUCE metadata block if present.

    This is critical before rendering - SAUCE should never be displayed.

    Args:
        data: Raw file bytes (possibly with SAUCE)

    Returns:
        Data with SAUCE removed (or unchanged if no SAUCE)

    Examples:
        >>> data = b"ANSI art content" + sauce_block
        >>> clean = strip_sauce_tail(data)
        >>> clean
        b'ANSI art content'
    """
    if len(data) >= 128 and data[-128:-123] == b"SAUCE":
        return data[:-128]

    # Defensive: Some files have padding before SAUCE
    last = data.rfind(b"SAUCE")
    if last != -1 and len(data) - last <= 512:
        return data[:last]

    return data


def append_minimal_sauce(
    data: bytes,
    *,
    title: str = "",
    author: str = "",
    group: str = "",
    yyyymmdd: Optional[str] = None,
    datatype: int = 1,  # Character art
    filetype: int = 1,  # ANSI
    tinfo1: Optional[int] = None,  # Width hint
    tinfo2: Optional[int] = None,  # Height hint
) -> bytes:
    """Append a minimal SAUCE v00 metadata block.

    This creates a spec-conformant 128-byte SAUCE block with basic metadata.
    Comments and record chaining are not supported (minimal implementation).

    Args:
        data: Content to append SAUCE to
        title: Title (max 35 chars)
        author: Author name (max 20 chars)
        group: Group name (max 20 chars)
        yyyymmdd: Date string (YYYYMMDD format), defaults to today
        datatype: SAUCE data type (1 = Character)
        filetype: SAUCE file type (1 = ANSI)
        tinfo1: Type-specific info 1 (usually width, e.g., 80)
        tinfo2: Type-specific info 2 (usually height, e.g., 25)

    Returns:
        Original data + 128-byte SAUCE block

    Examples:
        >>> data = b"ANSI art content"
        >>> with_sauce = append_minimal_sauce(
        ...     data,
        ...     title="MY BBS",
        ...     author="Artist",
        ...     tinfo1=80,
        ...     tinfo2=25
        ... )
        >>> len(with_sauce) == len(data) + 128
        True
    """
    if yyyymmdd is None:
        yyyymmdd = datetime.now().strftime("%Y%m%d")

    # Build SAUCE block (128 bytes total)
    sauce = bytearray(128)

    # ID (5 bytes): "SAUCE"
    sauce[0:5] = b"SAUCE"

    # Version (2 bytes): "00"
    sauce[5:7] = b"00"

    # Title (35 bytes, padded with spaces)
    sauce[7:42] = title[:35].encode("cp437", errors="replace").ljust(35, b" ")

    # Author (20 bytes)
    sauce[42:62] = author[:20].encode("cp437", errors="replace").ljust(20, b" ")

    # Group (20 bytes)
    sauce[62:82] = group[:20].encode("cp437", errors="replace").ljust(20, b" ")

    # Date (8 bytes): YYYYMMDD
    sauce[82:90] = yyyymmdd[:8].encode("ascii", errors="replace").ljust(8, b" ")

    # FileSize (4 bytes, little-endian) - original file size before SAUCE
    file_size = len(data)
    sauce[90:94] = file_size.to_bytes(4, byteorder="little")

    # DataType (1 byte)
    sauce[94] = datatype

    # FileType (1 byte)
    sauce[95] = filetype

    # TInfo1 (2 bytes, little-endian) - width hint
    if tinfo1 is not None:
        sauce[96:98] = tinfo1.to_bytes(2, byteorder="little")

    # TInfo2 (2 bytes, little-endian) - height hint
    if tinfo2 is not None:
        sauce[98:100] = tinfo2.to_bytes(2, byteorder="little")

    # TInfo3, TInfo4, TFlags (leave as zeros for minimal implementation)
    # sauce[100:106] already zero-filled

    # TInfoS (22 bytes) - optional filler string, leave empty
    # sauce[106:128] already zero-filled

    return data + bytes(sauce)
