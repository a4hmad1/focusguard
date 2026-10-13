"""FocusGuard Main Application Entry Point.

Seamlessly launches either the Graphical User Interface (GUI)
or routes to the Command-Line Interface (CLI) based on user arguments
and environment availability.
"""

import sys
import os

def is_display_available() -> bool:
    """Check if graphical display is available."""
    if sys.platform == "win32":
        return True
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))

def show_fatal_error(title: str, msg: str):
    """Display an alert dialog on Windows or print to stderr."""
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, msg, title, 0x10)  # MB_ICONERROR
    except Exception:
        pass
    print(f"[{title}] {msg}", file=sys.stderr)

def main():
    try:
        args = sys.argv[1:]
        
        # If explicit CLI command is provided (not --gui)
        if args and args[0] != "--gui":
            from focusguard.cli import main as cli_main
            sys.exit(cli_main(args))

        # Otherwise launch GUI if display is available
        if is_display_available():
            try:
                from focusguard.gui.app import run_gui
                sys.exit(run_gui())
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                try:
                    from focusguard.core.config import get_app_dir
                    log_file = get_app_dir() / "crash.log"
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"\n--- GUI Crash ---\n{tb}\n")
                except Exception:
                    pass
                show_fatal_error("FocusGuard Launch Error", f"Failed to start GUI:\n{e}\n\nCheck crash.log for details.")
                from focusguard.cli import main as cli_main
                sys.exit(cli_main(["status"]))
        else:
            # Headless environment
            from focusguard.cli import main as cli_main
            sys.exit(cli_main(["status"]))
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        show_fatal_error("FocusGuard Fatal Error", f"FocusGuard encountered an unexpected error:\n\n{e}\n\n{tb}")
        sys.exit(1)

if __name__ == "__main__":
    main()
