"""System and Application Icon Resolution Utilities."""

import os
from typing import Optional
from PySide6.QtGui import QIcon

def init_icon_subsystem():
    """Ensure standard icon search paths and theme fallbacks are configured."""
    search_paths = list(QIcon.themeSearchPaths())
    candidates = [
        "/usr/share/icons",
        "/usr/local/share/icons",
        "/usr/share/pixmaps",
        os.path.expanduser("~/.local/share/icons"),
        os.path.expanduser("~/.icons"),
    ]
    for p in candidates:
        if os.path.exists(p) and p not in search_paths:
            search_paths.append(p)
    QIcon.setThemeSearchPaths(search_paths)

    if not QIcon.themeName():
        for theme_name in ["Yaru", "Adwaita", "breeze", "elementary", "hicolor"]:
            if any(os.path.exists(os.path.join(p, theme_name)) for p in search_paths):
                QIcon.setThemeName(theme_name)
                break

try:
    init_icon_subsystem()
except Exception:
    pass

from PySide6.QtWidgets import QApplication, QStyle

def _get_style_icon(standard_pixmap) -> QIcon:
    app = QApplication.instance()
    if app:
        return app.style().standardIcon(standard_pixmap)
    return QIcon()

def get_app_icon(icon_name_or_path: Optional[str], exec_name: Optional[str] = None) -> QIcon:
    """Resolve native desktop application icon with comprehensive multi-tier fallback."""
    # 1. File path lookup (sanitize Windows quotes, comma indices like 'app.exe,0')
    if icon_name_or_path:
        clean_path = icon_name_or_path.strip('"\'').split(",")[0].strip()
        if os.path.isabs(clean_path) and os.path.exists(clean_path):
            ic = QIcon(clean_path)
            if not ic.isNull():
                return ic

    # 2. Freedesktop theme lookup by icon name
    if icon_name_or_path:
        ic = QIcon.fromTheme(icon_name_or_path)
        if not ic.isNull():
            return ic

    # 3. Freedesktop theme lookup by clean executable name
    if exec_name:
        clean = os.path.splitext(os.path.basename(exec_name))[0].lower()
        ic = QIcon.fromTheme(clean)
        if not ic.isNull():
            return ic

    # 4. Standard Linux /usr/share/pixmaps & hicolor search
    search_keys = []
    if icon_name_or_path:
        search_keys.append(icon_name_or_path)
    if exec_name:
        search_keys.append(os.path.splitext(os.path.basename(exec_name))[0].lower())

    for key in search_keys:
        for ext in [".png", ".svg", ".xpm"]:
            p = f"/usr/share/pixmaps/{key}{ext}"
            if os.path.exists(p):
                ic = QIcon(p)
                if not ic.isNull():
                    return ic

    # 5. Fallback generic executable icon
    fallback = QIcon.fromTheme("application-x-executable")
    if not fallback.isNull():
        return fallback
    fallback = QIcon.fromTheme("system-run")
    if not fallback.isNull():
        return fallback
    return _get_style_icon(QStyle.SP_FileIcon)

def get_shield_icon() -> QIcon:
    """Return FocusGuard shield vector icon."""
    res_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icons", "focusguard.svg")
    if os.path.exists(res_dir):
        return QIcon(res_dir)
    ic = QIcon.fromTheme("system-lock-screen")
    if not ic.isNull():
        return ic
    return _get_style_icon(QStyle.SP_VistaShield)

def get_web_icon() -> QIcon:
    """Return web browser / globe icon."""
    ic = QIcon.fromTheme("applications-internet")
    if not ic.isNull():
        return ic
    ic = QIcon.fromTheme("web-browser")
    if not ic.isNull():
        return ic
    return _get_style_icon(QStyle.SP_DriveNetIcon)

def get_apps_icon() -> QIcon:
    """Return desktop application icon."""
    ic = QIcon.fromTheme("application-x-executable")
    if not ic.isNull():
        return ic
    ic = QIcon.fromTheme("system-run")
    if not ic.isNull():
        return ic
    return _get_style_icon(QStyle.SP_DesktopIcon)

def get_calendar_icon() -> QIcon:
    """Return calendar / appointment icon."""
    ic = QIcon.fromTheme("appointment-new")
    if not ic.isNull():
        return ic
    ic = QIcon.fromTheme("appointment-soon")
    if not ic.isNull():
        return ic
    return _get_style_icon(QStyle.SP_FileDialogListView)

def get_settings_icon() -> QIcon:
    """Return preferences / gear icon."""
    ic = QIcon.fromTheme("preferences-system")
    if not ic.isNull():
        return ic
    ic = QIcon.fromTheme("emblem-system")
    if not ic.isNull():
        return ic
    return _get_style_icon(QStyle.SP_FileDialogDetailedView)
