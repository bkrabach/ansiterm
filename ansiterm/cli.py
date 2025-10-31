"""CLI tools for viewing and generating ANSI art.

Provides two commands:
- ansi-view: View .ANS files in the terminal
- ansify: Generate simple ANSI art from text
"""

import argparse
import sys
from pathlib import Path

from .analyze import analyze_file
from .builder import AnsiBuilder
from .render import render_file


def view_main():
    """Entry point for ansi-view command."""
    parser = argparse.ArgumentParser(
        description="View BBS-style ANSI (.ANS) art files in the terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ansi-view banner.ans
  ansi-view --no-ice artpack/*.ans
  ansi-view --info banner.ans
        """,
    )

    parser.add_argument(
        "files",
        nargs="+",
        type=str,
        help="ANSI art files to view",
    )

    parser.add_argument(
        "--no-ice",
        action="store_true",
        help="Disable iCE color mapping",
    )

    parser.add_argument(
        "--no-alt-screen",
        action="store_true",
        help="Don't use alternate screen (render to main terminal, art scrolls)",
    )

    parser.add_argument(
        "--no-safe",
        action="store_true",
        help="Disable safety filtering (allow all sequences)",
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show file analysis instead of rendering",
    )

    args = parser.parse_args()

    # Process each file
    for file_path in args.files:
        path = Path(file_path)

        if not path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            continue

        if not path.is_file():
            print(f"Error: Not a file: {file_path}", file=sys.stderr)
            continue

        try:
            if args.info:
                # Show analysis
                analysis = analyze_file(path)
                print(f"\nFile: {path}")
                print(f"  SAUCE: {'Yes' if analysis.has_sauce else 'No'}")
                print(f"  iCE colors: {'Yes' if analysis.uses_ice else 'No'}")
                print(f"  Cursor positioning: {'Yes' if analysis.has_cup else 'No'}")
                print(f"  Estimated size: {analysis.est_cols}x{analysis.est_rows}")
                print(f"  Suggested size: {analysis.suggested_width}x{analysis.suggested_height}")
            else:
                # Render with proper BBS art handling
                ice_mode = "off" if args.no_ice else "auto"
                use_alt = not args.no_alt_screen  # Default: True (BBS art needs controlled buffer!)
                safe = not args.no_safe

                # For alt screen mode, we need custom handling to keep art visible
                if use_alt:
                    # Manual alt screen control to wait before exit
                    from ansiterm import decode_text
                    from ansiterm.parser import filter_safe, ice_fix
                    from ansiterm.render import _enter_alt_screen, _exit_alt_screen, render_text_raw
                    from ansiterm.sauce import strip_sauce_tail

                    data = path.read_bytes()

                    try:
                        # Enter alt screen with full setup
                        _enter_alt_screen(sys.stdout.write)
                        sys.stdout.flush()

                        # Prepare text (do all processing manually)
                        clean = strip_sauce_tail(data)
                        text = decode_text(clean, "cp437")

                        if ice_mode in ("auto", "on"):
                            text = ice_fix(text)

                        if safe:
                            text = filter_safe(text)

                        # Render with NO additional terminal control
                        render_text_raw(text)

                        # ALWAYS wait before exiting alt screen (so art stays visible!)
                        if len(args.files) > 1:
                            sys.stdout.write("\n\nPress Enter for next file (Ctrl+C to quit)...")
                        else:
                            sys.stdout.write("\n\nPress Enter to exit...")

                        sys.stdout.flush()

                        # Use raw terminal input (works better in alt screen)
                        import termios
                        import tty

                        try:
                            fd = sys.stdin.fileno()
                            old_settings = termios.tcgetattr(fd)
                            try:
                                tty.setraw(fd)
                                # Read single char (Enter = \r or \n)
                                while True:
                                    ch = sys.stdin.read(1)
                                    if ch in ("\r", "\n", "\x03"):  # Enter or Ctrl+C
                                        if ch == "\x03":
                                            raise KeyboardInterrupt
                                        break
                            finally:
                                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        except (termios.error, AttributeError):
                            # Fallback to regular input if termios not available
                            input()
                    finally:
                        _exit_alt_screen(sys.stdout.write)
                        sys.stdout.flush()

                    if args.files.index(file_path) < len(args.files) - 1:
                        # Not last file, continue to next
                        continue
                    else:
                        # Last file, we're done
                        break

                else:
                    # Main screen mode (no alt screen)
                    render_file(
                        path,
                        ice_mode=ice_mode,
                        use_alt_screen=False,
                        safe_mode=safe,
                        clear_first=False,
                    )

                    if len(args.files) > 1:
                        print("\nPress Enter for next file (Ctrl+C to quit)...")
                        try:
                            input()
                            print("\n" * 2)  # Spacing
                        except KeyboardInterrupt:
                            print()
                            break

        except Exception as e:
            print(f"Error rendering {file_path}: {e}", file=sys.stderr)
            continue


def ansify_main():
    """Entry point for ansify command."""
    parser = argparse.ArgumentParser(
        description="Generate simple ANSI art banners",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ansify --text "MY BBS" --fg 15 --bg 4 -o banner.ans
  ansify --text "WELCOME" --fg 10 --center -o welcome.ans
        """,
    )

    parser.add_argument(
        "--text",
        type=str,
        required=True,
        help="Text to render",
    )

    parser.add_argument(
        "--fg",
        type=int,
        default=7,
        help="Foreground color (0-15, default: 7=white)",
    )

    parser.add_argument(
        "--bg",
        type=int,
        default=-1,
        help="Background color (0-15, default: none)",
    )

    parser.add_argument(
        "--bright-fg",
        action="store_true",
        help="Use bright foreground",
    )

    parser.add_argument(
        "--bright-bg",
        action="store_true",
        help="Use bright background",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=80,
        help="Width in columns (default: 80)",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=25,
        help="Height in rows (default: 25)",
    )

    parser.add_argument(
        "--center",
        action="store_true",
        help="Center text horizontally",
    )

    parser.add_argument(
        "--sauce-title",
        type=str,
        help="SAUCE title metadata",
    )

    parser.add_argument(
        "--sauce-author",
        type=str,
        help="SAUCE author metadata",
    )

    parser.add_argument(
        "--sauce-group",
        type=str,
        help="SAUCE group metadata",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Output .ANS file",
    )

    args = parser.parse_args()

    # Build ANSI art
    b = AnsiBuilder(args.width, args.height)
    b.clear().home()

    # Set colors
    b.sgr(0)  # Reset first

    fg_code = args.fg % 8
    if args.bright_fg or args.fg >= 8:
        b.fg(fg_code, bright=True)
    else:
        b.fg(fg_code)

    if args.bg >= 0:
        bg_code = args.bg % 8
        if args.bright_bg or args.bg >= 8:
            b.bg(bg_code, bright=True)
        else:
            b.bg(bg_code)

    # Create simple box around text
    text_len = len(args.text)
    box_width = text_len + 4
    box_height = 5

    # Calculate position
    if args.center:
        start_col = (args.width - box_width) // 2
    else:
        start_col = 2

    start_row = (args.height - box_height) // 2

    # Draw box
    b.move(start_row, start_col)
    b.text("╔" + "═" * (box_width - 2) + "╗")

    b.move(start_row + 1, start_col)
    b.text("║" + " " * (box_width - 2) + "║")

    b.move(start_row + 2, start_col)
    b.text("║ " + args.text + " ║")

    b.move(start_row + 3, start_col)
    b.text("║" + " " * (box_width - 2) + "║")

    b.move(start_row + 4, start_col)
    b.text("╚" + "═" * (box_width - 2) + "╝")

    b.reset()

    # Export with optional SAUCE
    sauce_kwargs = {}
    if args.sauce_title:
        sauce_kwargs["title"] = args.sauce_title
    if args.sauce_author:
        sauce_kwargs["author"] = args.sauce_author
    if args.sauce_group:
        sauce_kwargs["group"] = args.sauce_group

    add_sauce = bool(sauce_kwargs)
    data = b.to_bytes(add_sauce=add_sauce, **sauce_kwargs)

    # Write output
    output_path = Path(args.output)
    output_path.write_bytes(data)

    print(f"Generated: {output_path}")
    print(f"Size: {len(data)} bytes")
    if add_sauce:
        print("SAUCE metadata: Yes")
