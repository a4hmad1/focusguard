#include <windows.h>
#include <stdio.h>
#include <string.h>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    char exePath[MAX_PATH];
    char localPython[MAX_PATH];
    char cmdArgs[4096];
    char fallbackArgs[4096];
    char *lastSlash;
    DWORD attrib;
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    GetModuleFileNameA(NULL, exePath, MAX_PATH);
    lastSlash = strrchr(exePath, '\\');
    if (lastSlash) {
        *lastSlash = '\0';
    }

    snprintf(localPython, sizeof(localPython), "%s\\python\\pythonw.exe", exePath);
    attrib = GetFileAttributesA(localPython);

    if (attrib != INVALID_FILE_ATTRIBUTES && !(attrib & FILE_ATTRIBUTE_DIRECTORY)) {
        snprintf(cmdArgs, sizeof(cmdArgs), "\"%s\" -m focusguard.main %s", localPython, lpCmdLine ? lpCmdLine : "");
    } else {
        snprintf(cmdArgs, sizeof(cmdArgs), "pythonw.exe -m focusguard.main %s", lpCmdLine ? lpCmdLine : "");
    }

    SetEnvironmentVariableA("PYTHONPATH", exePath);

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    if (!CreateProcessA(NULL, cmdArgs, NULL, NULL, FALSE, 0, NULL, exePath, &si, &pi)) {
        snprintf(fallbackArgs, sizeof(fallbackArgs), "python.exe -m focusguard.main %s", lpCmdLine ? lpCmdLine : "");
        if (!CreateProcessA(NULL, fallbackArgs, NULL, NULL, FALSE, 0, NULL, exePath, &si, &pi)) {
            MessageBoxA(NULL, 
                "FocusGuard requires Python 3.8+ on your system.\n\nPlease install Python from python.org or verify your installation.", 
                "FocusGuard Launcher", MB_OK | MB_ICONEXCLAMATION);
            return 1;
        }
    }

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return 0;
}
