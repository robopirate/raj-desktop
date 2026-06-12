; ============================================================================
; Raj Hotkey Launcher — AutoHotkey Script
; ============================================================================
; Ctrl + Space  →  Toggle Raj on/off
;   - If Raj is NOT running → starts it
;   - If Raj IS running → closes it
;
; SETUP:
; 1. Install AutoHotkey v2 from https://www.autohotkey.com/
; 2. Double-click this file to run it (add to Windows startup for always-on)
; 3. Press Ctrl+Space anytime to toggle Raj
; ============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

; Path to the Raj folder (same folder as this script)
RAJ_PATH := A_ScriptDir
START_BAT := RAJ_PATH "\START.bat"
RAJ_EXE := "python.exe"
RAJ_WINDOW := "Raj — RoboPirate Command Center"

^Space:: {
    ; Check if Raj is already running by looking for the window title
    if WinExist(RAJ_WINDOW) {
        ; Raj is running → close it gracefully
        WinClose(RAJ_WINDOW)
        TrayTip "Raj", "Raj closed", 10
    } else {
        ; Check if python.exe is running with main.py (fallback check)
        pythonRunning := false
        try {
            wmi := ComObject("WbemScripting.SWbemLocator")
            svc := wmi.ConnectServer(".", "root\cimv2")
            processes := svc.ExecQuery("SELECT * FROM Win32_Process WHERE Name='python.exe'")
            for proc in processes {
                cmdLine := proc.CommandLine
                if InStr(cmdLine, "main.py") {
                    pythonRunning := true
                    break
                }
            }
        }

        if pythonRunning {
            ; Process exists but no window → kill it and restart
            RunWait 'taskkill /f /im python.exe 2>nul', , "Hide"
            Sleep 500
        }

        ; Start Raj
        Run START_BAT, RAJ_PATH
        TrayTip "Raj", "Raj starting...", 10
    }
}

; Right-click tray icon → Exit
#MenuTrayClick := 2  ; 2 = right-click
TrayMenu := A_TrayMenu
TrayMenu.Delete()
TrayMenu.Add("Raj Hotkey — Ctrl+Space", (*) => return)
TrayMenu.Disable("1&")
TrayMenu.Add()
TrayMenu.Add("Exit", (*) => ExitApp())
