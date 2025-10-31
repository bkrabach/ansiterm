# ansiterm

**Python library for rendering and authoring authentic 90s-style ANSI (.ANS) art in terminals.**

Brings the underground BBS aesthetic back to life with proper CP437 encoding, ANSI escape sequences, SAUCE metadata, and iCE color support.

## Features

✨ **Authentic BBS Art Rendering**
- CP437 encoding (IBM PC character set with box drawing: ╔═╗ █▓▒░)
- ANSI escape sequences for colors and cursor positioning
- Terminal safety (filter dangerous sequences)
- Cross-platform (Linux, macOS, Windows)

🎨 **SAUCE Metadata Support**
- Detect and strip SAUCE blocks
- Append minimal SAUCE v00 metadata
- Preserve title, author, group, dimensions

🌈 **iCE Color Handling**
- Automatic bright background mapping
- Historical blink bit -> modern color codes
- Configurable (auto, on, off)

🛠️ **Builder API**
- Programmatic .ANS generation
- Fluent API (method chaining)
- No manual escape code writing

🖥️ **CLI Tools**
- `ansi-view` - View .ANS files
- `ansify` - Generate simple banners

## Quick Start

### Installation

```bash
pip install ansiterm
```

### View Existing .ANS Files

```python
from ansiterm import render_file

# Render an .ANS file
render_file("banner.ans")
```

### Create New ANSI Art

```python
from ansiterm import AnsiBuilder
from pathlib import Path

# Build programmatically
b = AnsiBuilder(80, 25)
b.clear().home()
b.fg(15, bright=True).bg(4)  # Bright white on blue
b.move(10, 20).text("╔═══ MY BBS ═══╗")
b.move(11, 20).text("║  Welcome!   ║")
b.move(12, 20).text("╚══════════════╝")
b.reset()

# Export with SAUCE metadata
data = b.to_bytes(
    add_sauce=True,
    title="My Banner",
    author="Your Name",
    group="Your Group",
)

Path("mybanner.ans").write_bytes(data)
```

## API Reference

### Rendering

```python
from ansiterm import render_file, render_bytes, decode_text

# Render a file
render_file("banner.ans")

# Render bytes
data = Path("banner.ans").read_bytes()
render_bytes(data)

# Decode CP437 to text
text = decode_text(data, codec="cp437")
```

**Parameters:**
- `ice_mode: str` - iCE color handling ("auto", "on", "off")
- `use_alt_screen: bool` - Use alternate screen buffer (default: True)
- `safe_mode: bool` - Filter dangerous sequences (default: True)
- `codec: str` - Character encoding (default: "cp437")

### SAUCE Metadata

```python
from ansiterm import has_sauce, strip_sauce_tail, append_minimal_sauce

# Check for SAUCE
if has_sauce(data):
    print("Has SAUCE metadata")

# Remove SAUCE
clean_data = strip_sauce_tail(data)

# Add SAUCE
with_sauce = append_minimal_sauce(
    data,
    title="My Art",
    author="Artist Name",
    group="Art Group",
    tinfo1=80,   # Width
    tinfo2=25,   # Height
)
```

### Analysis

```python
from ansiterm import analyze_file, analyze_bytes

# Analyze a file
analysis = analyze_file("banner.ans")

print(f"SAUCE: {analysis.has_sauce}")
print(f"iCE colors: {analysis.uses_ice}")
print(f"Cursor positioning: {analysis.has_cup}")
print(f"Size: {analysis.est_cols}x{analysis.est_rows}")
print(f"Suggested: {analysis.suggested_width}x{analysis.suggested_height}")
```

### Builder API

```python
from ansiterm import AnsiBuilder

b = AnsiBuilder(width=80, height=25)

# Control sequences
b.clear()              # Clear screen
b.home()               # Move to 1,1
b.move(row, col)       # Position cursor
b.sgr(*params)         # SGR sequence

# Colors
b.fg(n, bright=False)  # Foreground (0-7)
b.bg(n, bright=False)  # Background (0-7)
b.reset()              # Reset all
b.bold()               # Bold
b.dim()                # Dim

# Content
b.text("Hello")        # Append text
b.newline()            # Add \n
b.cp437(bytes)         # Append CP437 bytes

# Export
text = b.to_text()     # As string
data = b.to_bytes(     # As bytes
    codec="cp437",
    add_sauce=True,
    title="...",
    author="...",
)
```

**Method chaining:**
```python
b.clear().home().fg(15, bright=True).bg(4).text("Hello").reset()
```

## CLI Tools

### ansi-view

View .ANS files in the terminal:

```bash
# View a file
ansi-view banner.ans

# View multiple files
ansi-view artpack/*.ans

# Show file info
ansi-view --info banner.ans

# Disable iCE color mapping
ansi-view --no-ice banner.ans

# Don't use alternate screen
ansi-view --no-alt banner.ans
```

### ansify

Generate simple ANSI art banners:

```bash
# Basic banner
ansify --text "MY BBS" --fg 15 --bg 4 -o banner.ans

# Centered with bright colors
ansify --text "WELCOME" --fg 10 --center --bright-fg -o welcome.ans

# With SAUCE metadata
ansify --text "TEST" \
  --sauce-title "Test Banner" \
  --sauce-author "AI" \
  -o test.ans
```

## Examples

### Example 1: Simple Splash Screen

```python
from ansiterm import AnsiBuilder
from pathlib import Path

b = AnsiBuilder(80, 25)
b.clear().home()

# Blue background panel
b.fg(15, bright=True).bg(4)
b.move(8, 20).text("╔══════════════════════════════════╗")
b.move(9, 20).text("║                                  ║")
b.move(10, 20).text("║         MY  BBS  v1.0           ║")
b.move(11, 20).text("║    Authentic ANSI Vibes          ║")
b.move(12, 20).text("║                                  ║")
b.move(13, 20).text("╚══════════════════════════════════╝")
b.reset()

data = b.to_bytes(add_sauce=True, title="MY BBS", author="AI")
Path("splash.ans").write_bytes(data)
```

### Example 2: Rainbow Gradient

```python
b = AnsiBuilder(80, 25)
b.clear().home()

# Rainbow blocks
b.move(10, 10)
colors = [1, 3, 2, 6, 4, 5]  # Red, yellow, green, cyan, blue, magenta
for color in colors * 8:
    b.fg(color, bright=True).text("▓▓")

b.reset()
data = b.to_bytes()
Path("rainbow.ans").write_bytes(data)
```

### Example 3: Viewing Art Packs

```python
from ansiterm import render_file
from pathlib import Path

# Download art from 16colo.rs
artpack = Path("acdu0595")  # Unzipped art pack

# View all .ANS files
for ans_file in artpack.glob("*.ANS"):
    print(f"\n{'='*80}")
    print(f"Viewing: {ans_file.name}")
    print('='*80 + '\n')

    render_file(ans_file)

    input("Press Enter for next...")
```

## Technical Details

### CP437 Encoding

IBM PC Code Page 437 includes:

**Box Drawing:**
- Single line: `─│┌┐└┘├┤┬┴┼`
- Double line: `═║╔╗╚╝╠╣╦╩╬`
- Mixed: `╒╓╕╖╘╙╛╜╞╟╡╢╤╥╧╨╪╫`

**Blocks:**
- `█` - Full block
- `▓` - Dark shade
- `▒` - Medium shade
- `░` - Light shade
- `▀` - Upper half
- `▄` - Lower half

### ANSI Escape Sequences

**SGR (Select Graphic Rendition):**
- `ESC[0m` - Reset
- `ESC[1m` - Bold
- `ESC[2m` - Dim
- `ESC[30-37m` - Foreground colors
- `ESC[40-47m` - Background colors
- `ESC[90-97m` - Bright foreground
- `ESC[100-107m` - Bright background

**Cursor Positioning:**
- `ESC[H` - Home (1,1)
- `ESC[{row};{col}H` - Move to position
- `ESC[{n}A` - Up n lines
- `ESC[{n}B` - Down n lines

**Display:**
- `ESC[2J` - Clear entire screen
- `ESC[K` - Clear to end of line

### iCE Colors

BBS art from the 90s used the "blink" attribute bit to enable bright backgrounds (iCE colors). Modern terminals ignore blink, so we map it:

- `ESC[5;44m` (blink + blue bg) → `ESC[104m` (bright blue bg)
- Blink bit dropped
- Background color incremented by 60

### SAUCE Format

128-byte block at file end:

```
Offset  Length  Field
0       5       ID ("SAUCE")
5       2       Version ("00")
7       35      Title
42      20      Author
62      20      Group
82      8       Date (YYYYMMDD)
90      4       FileSize (little-endian)
94      1       DataType (1 = Character)
95      1       FileType (1 = ANSI)
96      2       TInfo1 (width)
98      2       TInfo2 (height)
100     2       TInfo3
102     2       TInfo4
104     1       TFlags
105     22      TInfoS
127     1       (padding)
```

## Safety

By default, ansiterm filters dangerous sequences:
- **OSC** (Operating System Commands) - Can set titles, clipboard
- **DCS** (Device Control Strings) - Terminal-specific commands
- **Unknown CSI** - Anything not whitelisted

**Safe sequences:**
- SGR (colors/attributes)
- CUP (cursor positioning)
- ED/EL (erase display/line)
- DEC private modes (for alt screen, wrap, cursor)

Disable with `safe_mode=False` if you trust the source.

## Windows Support

On Windows, ansiterm automatically enables VT processing:

```python
try:
    import colorama
    colorama.just_fix_windows_console()
except Exception:
    pass  # Optional dependency
```

For best results, install colorama:

```bash
pip install ansiterm[windows]
```

## Philosophy

**Mechanism, not policy:**
- ansiterm provides ANSI rendering capabilities
- Applications decide when and how to use them
- No configuration files or defaults

**Ruthless simplicity:**
- Minimal dependencies (optional colorama only)
- Clean, focused API
- No unnecessary features

**Authenticity:**
- Real CP437 encoding
- Proper ANSI escape sequences
- SAUCE metadata support
- iCE color handling

**Safety:**
- Filter dangerous sequences by default
- Never crash the terminal
- Graceful degradation

## Testing

Run the test suite:

```bash
cd ansiterm
pytest tests/ -v
```

All tests should pass on Linux, macOS, and Windows.

## Contributing

This library is part of the [Amplifier](https://github.com/microsoft/amplifier) project.

**Philosophy alignment:**
- @ai_context/IMPLEMENTATION_PHILOSOPHY.md - Ruthless simplicity
- @ai_context/MODULAR_DESIGN_PHILOSOPHY.md - Bricks and studs
- @AGENTS.md - Mechanism, not policy

## License

MIT

## Acknowledgments

- BBS art communities (ACiD, iCE, etc.)
- [16colo.rs](https://16colo.rs/) - Preserving BBS art history
- SAUCE spec creators
- Underground art scene from the 90s

---

**Brings back the 90s, one escape sequence at a time.** 🎨✨
