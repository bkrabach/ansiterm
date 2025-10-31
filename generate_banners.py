"""Generate 5 BBS-style ANSI art banners for Amplifier.

Each banner has its own aesthetic:
- classic: Clean, professional
- cyber: Neon futuristic with rainbow gradients
- underground: Street art chaos
- matrix: Green-on-black code rain
- retro: Full 90s BBS with gradient borders
"""

from pathlib import Path

from ansiterm import AnsiBuilder


def generate_classic(version: str) -> bytes:
    """Classic: Clean cyan professional banner."""
    b = AnsiBuilder(80, 25)
    b.clear().home()

    # Title
    b.move(8, 15)
    b.fg(6, bright=True)  # Bright cyan
    b.text("▄▀█ █▀▄▀█ █▀█ █░░ █ █▀▀ █ █▀▀ █▀█")

    b.move(9, 15)
    b.text("█▀█ █░▀░█ █▀▀ █▄▄ █ █▀░ █ ██▄ █▀▄")

    # Separator
    b.move(11, 10)
    b.fg(6)  # Cyan
    b.text("─" * 60)

    # Status line
    b.move(13, 10)
    b.fg(7)  # White
    b.text("● SYSTEM READY     ● AI CORE ACTIVE     ● v" + version)

    # Description
    b.move(15, 10)
    b.sgr(2)  # Dim
    b.text("Interactive AI Development Environment")

    # Commands
    b.move(17, 10)
    b.sgr(2)
    b.text("Commands: /help │ /think │ /do │ Ctrl-J │ Ctrl-D")

    b.reset()

    return b.to_bytes(
        add_sauce=True,
        title="Amplifier Classic",
        author="Amplifier Team",
        group="Microsoft",
    )


def generate_cyber(version: str) -> bytes:
    """Cyber: Rainbow gradient blocks and neon colors."""
    b = AnsiBuilder(80, 25)
    b.clear().home()

    # Top rainbow gradient
    b.move(4, 2)
    colors = [3, 6, 5, 2, 1] * 15  # Yellow, cyan, magenta, green, red
    for color in colors[:75]:
        b.fg(color % 8, bright=True)
        b.text("▓")

    # Title box
    b.move(8, 20)
    b.fg(6, bright=True)  # Bright cyan
    b.text("╔══════════════════════════════════════╗")

    b.move(9, 20)
    b.text("║                                      ║")

    b.move(10, 20)
    b.fg(3, bright=True)  # Bright yellow
    b.text("║         A M P L I F I E R           ║")

    b.move(11, 20)
    b.fg(6, bright=True)
    b.text("║                                      ║")

    b.move(12, 20)
    b.text("╚══════════════════════════════════════╝")

    # Status indicators
    b.move(15, 10)
    b.fg(2, bright=True)  # Bright green
    b.text("◉")
    b.fg(7)  # White
    b.text(" ONLINE  ")

    b.fg(6, bright=True)  # Bright cyan
    b.text("◉")
    b.fg(7)
    b.text(" ACTIVE  ")

    b.fg(5, bright=True)  # Bright magenta
    b.text("◉")
    b.fg(7)
    b.text(" FLOWING  ")

    b.sgr(2)  # Dim
    b.text(f" v{version}")

    # Commands
    b.move(18, 10)
    b.sgr(2)
    b.text("CMD: /help │ /think │ /do │ Ctrl-J │ Ctrl-D")

    # Ready indicator
    b.move(20, 35)
    b.fg(5, bright=True)
    b.bg(5)  # Magenta on magenta background
    b.text(" READY ")

    b.reset()

    return b.to_bytes(
        add_sauce=True,
        title="Amplifier Cyber",
        author="Amplifier Team",
        group="Microsoft",
    )


def generate_underground(version: str) -> bytes:
    """Underground: Street art chaos with rainbow colors."""
    b = AnsiBuilder(80, 25)
    b.clear().home()

    # Chaotic title - each letter different color
    title_colors = [1, 3, 2, 6, 4, 5, 1, 3, 2]  # Red, yellow, green, cyan, blue, magenta
    title = "AMPLIFIER"

    b.move(6, 25)
    for i, char in enumerate(title):
        b.fg(title_colors[i % len(title_colors)], bright=True)
        b.text(char + " ")

    # Underground node banner
    b.move(9, 20)
    b.sgr(2).fg(1)  # Dim red
    b.text("UNDERGROUND NODE")

    b.fg(1, bright=True)
    b.text("  ✗")
    b.bg(1).fg(7, bright=True)  # White on red
    b.text(" NO RULES ")
    b.reset().fg(1, bright=True)
    b.text("✗")

    b.sgr(2).fg(1)
    b.text(f"  v{version}")

    # System checklist
    b.move(12, 18)
    b.sgr(2).fg(7)
    b.text("├── ")
    b.fg(2, bright=True)
    b.text("✓")
    b.fg(7)
    b.text(" SYSTEM ARMED")

    b.move(13, 18)
    b.sgr(2).fg(7)
    b.text("├── ")
    b.fg(2, bright=True)
    b.text("✓")
    b.fg(7)
    b.text(" AI CORE LOADED")

    b.move(14, 18)
    b.sgr(2).fg(7)
    b.text("├── ")
    b.fg(2, bright=True)
    b.text("✓")
    b.fg(7)
    b.text(" SECURITY BYPASSED")

    b.move(15, 18)
    b.sgr(2).fg(7)
    b.text("└── ")
    b.fg(2, bright=True)
    b.text("✓")
    b.fg(7)
    b.text(" ALL SYSTEMS GO")

    # Commands with slashes
    b.move(18, 18)
    b.fg(1, bright=True)
    b.text("/")
    b.fg(3, bright=True)
    b.text("/")
    b.fg(2, bright=True)
    b.text("/")
    b.bg(1).fg(7, bright=True)
    b.text(" COMMANDS ")
    b.reset()
    b.sgr(2)
    b.text(" │ /help │ /think │ /do │ Ctrl-J │ Ctrl-D")

    # Ready
    b.move(20, 18)
    b.fg(3, bright=True)
    b.text("▓")
    b.fg(1, bright=True)
    b.text("░")
    b.fg(2, bright=True)
    b.text("▒")
    b.fg(6, bright=True)
    b.text("▓")
    b.bg(1).fg(7, bright=True)
    b.text(" READY TO HACK ")

    b.reset()

    return b.to_bytes(
        add_sauce=True,
        title="Amplifier Underground",
        author="Amplifier Team",
        group="Microsoft",
    )


def generate_matrix(version: str) -> bytes:
    """Matrix: Green-on-black code rain aesthetic."""
    b = AnsiBuilder(80, 25)
    b.clear().home()

    # All on black background
    b.bg(0)

    # Title
    b.move(6, 15)
    b.fg(2, bright=True).bold()  # Bright bold green
    b.text("╔════════════════════════════════════════════╗")

    b.move(7, 15)
    b.text("║                                            ║")

    b.move(8, 15)
    b.text("║         A M P L I F I E R                 ║")

    b.move(9, 15)
    b.text("║                                            ║")

    b.move(10, 15)
    b.text("╚════════════════════════════════════════════╝")

    # Block separator
    b.move(12, 2)
    b.fg(2).sgr(2)  # Dim green
    b.text("▓" * 76)

    # Init sequence
    b.move(14, 10)
    b.fg(2).sgr(2)
    b.text("> SYSTEM INITIALIZATION...")

    b.move(15, 10)
    b.text("> LOADING NEURAL PATHWAYS...")

    b.move(16, 10)
    b.text("> ESTABLISHING QUANTUM LINK...")

    b.move(17, 10)
    b.fg(2, bright=True).bold()
    b.text("> READY")

    # Version
    b.move(19, 10)
    b.bg(2).fg(0, bright=True).bold()  # Black on bright green
    b.text(f" MATRIX PROTOCOL v{version} ")

    # Commands
    b.move(21, 10)
    b.reset().bg(0).fg(2).sgr(2)
    b.text("CMD: /help │ /think │ /do │ Ctrl-J │ Ctrl-D")

    # Connected
    b.move(22, 32)
    b.bg(2).fg(7, bright=True).bold()
    b.text(" ● CONNECTED ● ")

    b.reset()

    return b.to_bytes(
        add_sauce=True,
        title="Amplifier Matrix",
        author="Amplifier Team",
        group="Microsoft",
    )


def generate_retro(version: str) -> bytes:
    """Retro: Full 90s BBS with gradient borders."""
    b = AnsiBuilder(80, 25)
    b.clear().home()

    # All on blue background
    b.bg(4)

    # Top gradient borders
    b.move(2, 1)
    b.fg(7, bright=True)
    b.text("░" * 78)

    b.move(3, 1)
    b.fg(3, bright=True)
    b.text("▒" * 78)

    b.move(4, 1)
    b.fg(6, bright=True)
    b.text("▓" * 78)

    # Title
    b.move(7, 10)
    b.fg(3, bright=True).bold()
    b.text("╔══════════════════════════════════════════════════════╗")

    b.move(8, 10)
    b.text("║                                                      ║")

    b.move(9, 10)
    b.text("║              A M P L I F I E R                      ║")

    b.move(10, 10)
    b.text("║                                                      ║")

    b.move(11, 10)
    b.text("╚══════════════════════════════════════════════════════╝")

    # BBS Header
    b.move(13, 10)
    b.fg(6, bright=True).bold()
    b.text("░▒▓█  AI DEVELOPMENT BBS  █▓▒░  EST. 2024")

    # Separator
    b.move(15, 1)
    b.fg(3, bright=True)
    b.text("▓" * 78)

    # Status board
    b.move(17, 10)
    b.fg(7, bright=True)
    b.text(f"● NODE #42       ● SYSOP Claude v4.0       ● v{version}")

    b.move(18, 10)
    b.text("● LOCATION      ● UPTIME Just now")

    # Commands
    b.move(20, 10)
    b.sgr(2)
    b.text("COMMANDS: /help │ /think │ /do │ Ctrl-J │ Ctrl-D")

    # Ready
    b.move(21, 28)
    b.bg(2).fg(7, bright=True).bold()  # White on green
    b.text(" READY FOR INPUT ")

    # Bottom gradient borders
    b.reset().bg(4)

    b.move(23, 1)
    b.fg(6, bright=True)
    b.text("▓" * 78)

    b.move(24, 1)
    b.fg(3, bright=True)
    b.text("▒" * 78)

    b.move(25, 1)
    b.fg(7, bright=True)
    b.text("░" * 78)

    b.reset()

    return b.to_bytes(
        add_sauce=True,
        title="Amplifier Retro",
        author="Amplifier Team",
        group="Microsoft",
    )


def main():
    """Generate all 5 banners."""
    output_dir = Path("banners")
    output_dir.mkdir(exist_ok=True)

    version = "0.1.0"

    banners = {
        "classic": generate_classic,
        "cyber": generate_cyber,
        "underground": generate_underground,
        "matrix": generate_matrix,
        "retro": generate_retro,
    }

    for name, generator in banners.items():
        print(f"Generating {name}...")
        data = generator(version)
        output_path = output_dir / f"{name}.ans"
        output_path.write_bytes(data)
        print(f"  → {output_path} ({len(data)} bytes)")

    print(f"\n✅ Generated {len(banners)} banners in {output_dir}/")
    print("\nView with: ansi-view banners/*.ans")


if __name__ == "__main__":
    main()
