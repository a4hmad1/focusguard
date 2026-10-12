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

def main():
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
            print(f"Failed to start GUI: {e}. Falling back to CLI.")
            from focusguard.cli import main as cli_main
            sys.exit(cli_main(["status"]))
    else:
        # Headless environment
        from focusguard.cli import main as cli_main
        sys.exit(cli_main(["status"]))

if __name__ == "__main__":
    main()
