@echo off
REM ========================================================
REM FocusGuard Windows Installer Builder
REM ========================================================

echo [1/3] Installing Windows build dependencies...
pip install pyinstaller psutil PySide6

echo [2/3] Compiling FocusGuard Windows binary with PyInstaller...
pyinstaller --clean --noconfirm packaging\windows\focusguard.spec

echo [3/3] Building Inno Setup Windows installer...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" packaging\windows\installer.iss
    echo Setup installer generated in dist\FocusGuard-Setup-1.0.0.exe
) else (
    echo [INFO] Inno Setup not found. Standalone executable folder generated in dist\FocusGuard\
)

pause
