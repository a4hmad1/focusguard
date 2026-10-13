!define APPNAME "FocusGuard"
!define APPVERSION "1.0.0"
!define COMPANYNAME "FocusGuard Project"
!define DESCRIPTION "Cross-Platform Website and Application Blocking Desktop Software"

Name "${APPNAME} ${APPVERSION}"
OutFile "../../dist/FocusGuard-Setup-1.0.0.exe"
InstallDir "$PROGRAMFILES64\FocusGuard"
InstallDirRegKey HKLM "Software\FocusGuard" "Install_Dir"
RequestExecutionLevel admin

Icon "focusguard.ico"
UninstallIcon "focusguard.ico"

Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

Section "FocusGuard Core"
  SetOutPath "$INSTDIR"
  
  ; Native Windows Launcher Executable
  File "FocusGuard.exe"
  File "focusguard.ico"

  ; Application Source
  File /r "..\..\focusguard"
  File "..\..\pyproject.toml"
  File "..\..\README.md"

  ; Embedded Standalone Python 3.11 Windows Runtime
  SetOutPath "$INSTDIR\python"
  File /r "python_embed\*.*"

  SetOutPath "$INSTDIR"
  ; Command Line Batch Wrapper
  FileOpen $0 "$INSTDIR\focusguard.bat" w
  FileWrite $0 '@echo off$\r$\nset PYTHONPATH=%~dp0;%PYTHONPATH%$\r$\nif exist "%~dp0python\python.exe" ($\r$\n    "%~dp0python\python.exe" -m focusguard.main %*$\r$\n) else ($\r$\n    python -m focusguard.main %*$\r$\n)$\r$\n'
  FileClose $0

  ; Create Start Menu Shortcuts
  CreateDirectory "$SMPROGRAMS\FocusGuard"
  CreateShortcut "$SMPROGRAMS\FocusGuard\FocusGuard.lnk" "$INSTDIR\FocusGuard.exe" "" "$INSTDIR\FocusGuard.exe" 0
  CreateShortcut "$SMPROGRAMS\FocusGuard\FocusGuard CLI.lnk" "$INSTDIR\focusguard.bat" "" "$INSTDIR\FocusGuard.exe" 0
  CreateShortcut "$SMPROGRAMS\FocusGuard\Uninstall.lnk" "$INSTDIR\uninstall.exe" ""

  ; Create Desktop Shortcut
  CreateShortcut "$DESKTOP\FocusGuard.lnk" "$INSTDIR\FocusGuard.exe" "" "$INSTDIR\FocusGuard.exe" 0

  ; Register in Windows Add/Remove Programs
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FocusGuard" "DisplayName" "FocusGuard Study Shield"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FocusGuard" "DisplayVersion" "${APPVERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FocusGuard" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FocusGuard" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FocusGuard" "QuietUninstallString" '"$INSTDIR\uninstall.exe" /S'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FocusGuard" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FocusGuard" "NoRepair" 1
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\FocusGuard.lnk"
  Delete "$SMPROGRAMS\FocusGuard\FocusGuard.lnk"
  Delete "$SMPROGRAMS\FocusGuard\FocusGuard CLI.lnk"
  Delete "$SMPROGRAMS\FocusGuard\Uninstall.lnk"
  RMDir "$SMPROGRAMS\FocusGuard"
  RMDir /r "$INSTDIR\python"
  RMDir /r "$INSTDIR\focusguard"
  Delete "$INSTDIR\FocusGuard.exe"
  Delete "$INSTDIR\focusguard.bat"
  Delete "$INSTDIR\pyproject.toml"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\FocusGuard"
  DeleteRegKey HKLM "Software\FocusGuard"
SectionEnd
