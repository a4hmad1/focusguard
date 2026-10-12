#!/usr/bin/env bash
set -e

# FocusGuard Ubuntu .deb Package Builder
APP_NAME="focusguard"
VERSION="1.0.0"
ARCH="amd64"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST_DIR="${SRC_DIR}/dist"
STAGE_DIR="${SRC_DIR}/build/deb_pkg"

echo "=== Building Ubuntu .deb Package for ${APP_NAME} v${VERSION} (${ARCH}) ==="

# 1. Clean previous build staging
rm -rf "${STAGE_DIR}"
mkdir -p "${DIST_DIR}"
mkdir -p "${STAGE_DIR}/DEBIAN"
mkdir -p "${STAGE_DIR}/usr/bin"
mkdir -p "${STAGE_DIR}/usr/lib/focusguard"
mkdir -p "${STAGE_DIR}/usr/share/applications"
mkdir -p "${STAGE_DIR}/usr/share/icons/hicolor/scalable/apps"
mkdir -p "${STAGE_DIR}/lib/systemd/system"

# 2. Copy application source
cp -r "${SRC_DIR}/focusguard" "${STAGE_DIR}/usr/lib/focusguard/"

# 3. Create /usr/bin/focusguard executable wrapper
cat << 'EOF' > "${STAGE_DIR}/usr/bin/focusguard"
#!/usr/bin/env bash
export PYTHONPATH="/usr/lib/focusguard:${PYTHONPATH}"
exec /usr/bin/python3 -m focusguard.main "$@"
EOF
chmod 755 "${STAGE_DIR}/usr/bin/focusguard"

# 4. Copy desktop integration assets
cp "${SRC_DIR}/packaging/deb/focusguard.desktop" "${STAGE_DIR}/usr/share/applications/"
cp "${SRC_DIR}/focusguard/resources/icons/focusguard.svg" "${STAGE_DIR}/usr/share/icons/hicolor/scalable/apps/"
cp "${SRC_DIR}/packaging/deb/focusguard.service" "${STAGE_DIR}/lib/systemd/system/"

# 5. Create Debian package control file
cat << EOF > "${STAGE_DIR}/DEBIAN/control"
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.8), python3-pyside6.qtwidgets, python3-pyside6.qtsvg, python3-psutil
Maintainer: FocusGuard Project <support@focusguard.dev>
Description: Cross-Platform Website and Application Blocking Desktop Software
 FocusGuard is a desktop productivity application that empowers students
 to block distracting websites and desktop applications, manage website whitelists,
 schedule study sessions, and maintain a distraction-free learning environment.
EOF

# 6. Create post-installation script
cat << 'EOF' > "${STAGE_DIR}/DEBIAN/postinst"
#!/bin/sh
set -e

if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q /usr/share/applications || true
fi

if [ -x /usr/bin/gtk-update-icon-cache ]; then
    /usr/bin/gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

exit 0
EOF
chmod 755 "${STAGE_DIR}/DEBIAN/postinst"

# 7. Create pre-removal script (clean up hosts restrictions before uninstall)
cat << 'EOF' > "${STAGE_DIR}/DEBIAN/prerm"
#!/bin/sh
set -e

# Lift any active restrictions before removal
if [ -x /usr/bin/focusguard ]; then
    /usr/bin/focusguard emergency-unblock >/dev/null 2>&1 || true
fi

exit 0
EOF
chmod 755 "${STAGE_DIR}/DEBIAN/prerm"

# 8. Build Debian Package
DEB_FILE="${DIST_DIR}/${APP_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "${STAGE_DIR}" "${DEB_FILE}"

echo "=========================================================="
echo "Package built successfully:"
echo "  Location: ${DEB_FILE}"
echo "=========================================================="
dpkg-deb --info "${DEB_FILE}"
