"""Automated Windows Executable and Installer Builder.

Compiles FocusGuard into a standalone Windows executable directory via PyInstaller
and packages it into an official FocusGuard-Setup-1.0.0.exe installer via Inno Setup.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build():
    root = Path(__file__).parent.parent.parent
    spec_file = root / "packaging" / "windows" / "focusguard.spec"
    dist_dir = root / "dist"
    iss_file = root / "packaging" / "windows" / "installer.iss"

    print("=== Step 1: Building Standalone Windows Executable via PyInstaller ===")
    cmd_pyinstaller = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]
    subprocess.check_call(cmd_pyinstaller, cwd=str(root))
    print(f"PyInstaller build complete: {dist_dir / 'FocusGuard'}")

    print("\n=== Step 2: Compiling Setup Installer via Inno Setup (if available) ===")
    # Look for ISCC.exe in common locations
    iscc_candidates = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        shutil.which("ISCC.exe")
    ]
    iscc_path = next((c for c in iscc_candidates if c and os.path.exists(c)), None)

    if iscc_path:
        subprocess.check_call([iscc_path, str(iss_file)])
        print(f"Setup Installer compiled: {dist_dir / 'FocusGuard-Setup-1.0.0.exe'}")
    else:
        print("Inno Setup compiler (ISCC.exe) not found on path.")
        print(f"The portable standalone application directory is ready at: {dist_dir / 'FocusGuard'}")
        print("To create the installer .exe, install Inno Setup 6 and compile installer.iss.")

if __name__ == "__main__":
    build()
