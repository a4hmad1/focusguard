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
    BOOL launched = FALSE;

    GetModuleFileNameA(NULL, exePath, MAX_PATH);
    lastSlash = strrchr(exePath, '\\');
    if (lastSlash) {
        *lastSlash = '\0';
    }

    SetCurrentDirectoryA(exePath);
    SetEnvironmentVariableA("PYTHONPATH", exePath);

    // Check local embedded python locations
    const char *subdirs[] = {"python", "python_embed"};
    const char *binaries[] = {"pythonw.exe", "python.exe"};
    localPython[0] = '\0';

    for (size_t s = 0; s < 2; s++) {
        for (size_t b = 0; b < 2; b++) {
            char candidate[MAX_PATH];
            snprintf(candidate, sizeof(candidate), "%s\\%s\\%s", exePath, subdirs[s], binaries[b]);
            attrib = GetFileAttributesA(candidate);
            if (attrib != INVALID_FILE_ATTRIBUTES && !(attrib & FILE_ATTRIBUTE_DIRECTORY)) {
                strncpy(localPython, candidate, sizeof(localPython) - 1);
                localPython[sizeof(localPython) - 1] = '\0';
                break;
            }
        }
        if (localPython[0] != '\0') break;
    }

    // Prepend Python paths to PATH
    char envPath[8192];
    char oldPath[4096] = "";
    GetEnvironmentVariableA("PATH", oldPath, sizeof(oldPath));
    snprintf(envPath, sizeof(envPath), "%s\\python;%s\\python_embed;%s", exePath, exePath, oldPath);
    SetEnvironmentVariableA("PATH", envPath);

    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));

    if (localPython[0] != '\0') {
        snprintf(cmdArgs, sizeof(cmdArgs), "\"%s\" -m focusguard.main %s", localPython, lpCmdLine ? lpCmdLine : "");
        launched = CreateProcessA(NULL, cmdArgs, NULL, NULL, FALSE, 0, NULL, exePath, &si, &pi);
    }

    if (!launched) {
        snprintf(cmdArgs, sizeof(cmdArgs), "pythonw.exe -m focusguard.main %s", lpCmdLine ? lpCmdLine : "");
        launched = CreateProcessA(NULL, cmdArgs, NULL, NULL, FALSE, 0, NULL, exePath, &si, &pi);
    }

    if (!launched) {
        snprintf(fallbackArgs, sizeof(fallbackArgs), "python.exe -m focusguard.main %s", lpCmdLine ? lpCmdLine : "");
        launched = CreateProcessA(NULL, fallbackArgs, NULL, NULL, FALSE, 0, NULL, exePath, &si, &pi);
    }

    if (!launched) {
        MessageBoxA(NULL, 
            "FocusGuard could not find a Python runtime.\n\n"
            "Please ensure the application was installed correctly, or install Python 3.8+ from python.org.", 
            "FocusGuard Launcher Error", MB_OK | MB_ICONERROR);
        return 1;
    }

    // Wait briefly to catch immediate startup crashes
    DWORD waitRes = WaitForSingleObject(pi.hProcess, 1500);
    if (waitRes == WAIT_OBJECT_0) {
        DWORD exitCode = 0;
        GetExitCodeProcess(pi.hProcess, &exitCode);
        if (exitCode != 0) {
            char errMsg[1024];
            snprintf(errMsg, sizeof(errMsg),
                "FocusGuard failed to start (Exit code: %lu).\n\n"
                "Please run 'focusguard.bat' in the application directory to inspect error logs.",
                exitCode);
            MessageBoxA(NULL, errMsg, "FocusGuard Error", MB_OK | MB_ICONERROR);
            CloseHandle(pi.hProcess);
            CloseHandle(pi.hThread);
            return (int)exitCode;
        }
    }

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    return 0;
}
