Option Explicit

Dim objShell, objFSO, currentPath
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
currentPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

Dim result

result = MsgBox("Meeting Room System Setup" & vbCrLf & vbCrLf & "Continue?", vbYesNo + vbQuestion, "Setup")
If result = vbNo Then
    WScript.Quit
End If

Dim pythonInstalled
pythonInstalled = CheckPython()

If Not pythonInstalled Then
    result = MsgBox("Python not found." & vbCrLf & "Open download page?", vbYesNo + vbExclamation, "Python Missing")
    If result = vbYes Then
        objShell.Run "https://www.python.org/downloads/", 1, False
        MsgBox "Install Python and run this again.", vbInformation, "Please Install"
    End If
    WScript.Quit
End If

MsgBox "Python found. Installing libraries...", vbInformation, "Python OK"

If InstallLibraries() Then
    MsgBox "Libraries installed successfully", vbInformation, "Install Complete"
Else
    MsgBox "Library installation failed", vbExclamation, "Error"
    WScript.Quit
End If

CreateFolders
CheckConfigFile

result = MsgBox("Basic setup complete. Configure rooms?", vbYesNo + vbQuestion, "Room Config")
If result = vbYes Then
    If objFSO.FileExists(currentPath & "\config_editor.pyw") Then
        objShell.Run "python """ & currentPath & "\config_editor.pyw""", 1, True
        MsgBox "Configuration saved", vbInformation, "Complete"
    Else
        MsgBox "Config editor not found", vbExclamation, "Error"
    End If
End If

result = MsgBox("Setup complete! Start system now?", vbYesNo + vbQuestion, "Start System")
If result = vbYes Then
    MsgBox "Starting system... Browser will open", vbInformation, "Starting"
    objShell.Run "cmd /c ""timeout /t 3 /nobreak >nul && start http://localhost:5003""", 0, False
    objShell.Run "python """ & currentPath & "\server_fixed.py""", 0, False
Else
    MsgBox "Start manually when ready", vbInformation, "Complete"
End If

Function CheckPython()
    On Error Resume Next
    Dim checkResult
    checkResult = objShell.Run("python --version", 0, True)
    CheckPython = (checkResult = 0)
    On Error GoTo 0
End Function

Function InstallLibraries()
    On Error Resume Next
    Dim pipResult, libResult

    pipResult = objShell.Run("python -m pip install --upgrade pip", 0, True)

    If objFSO.FileExists(currentPath & "\requirements.txt") Then
        libResult = objShell.Run("python -m pip install -r """ & currentPath & "\requirements.txt""", 0, True)
    Else
        libResult = objShell.Run("python -m pip install flask flask_cors pandas watchdog pystray Pillow", 0, True)
    End If

    InstallLibraries = (libResult = 0)
    On Error GoTo 0
End Function

Sub CreateFolders()
    Dim folders, i
    folders = Array("data", "uploads", "processed")

    For i = 0 To UBound(folders)
        If Not objFSO.FolderExists(currentPath & "\" & folders(i)) Then
            objFSO.CreateFolder(currentPath & "\" & folders(i))
        End If
    Next
End Sub

Sub CheckConfigFile()
    If Not objFSO.FileExists(currentPath & "\config.json") Then
        If objFSO.FileExists(currentPath & "\config_distribution.json") Then
            objFSO.CopyFile currentPath & "\config_distribution.json", currentPath & "\config.json"
        End If
    End If
End Sub