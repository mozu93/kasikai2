Option Explicit

Dim objShell, objFSO, currentPath
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
currentPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

Dim result
result = MsgBox("Meeting Room Booking System Setup" & vbCrLf & vbCrLf & "Current folder: " & currentPath & vbCrLf & vbCrLf & "Continue setup?", vbYesNo + vbQuestion, "Setup")

If result = vbNo Then
    WScript.Quit
End If

If Not CheckPython() Then
    result = MsgBox("Python not found on this system." & vbCrLf & vbCrLf & "Open Python download page?", vbYesNo + vbExclamation, "Python Required")
    If result = vbYes Then
        objShell.Run "https://www.python.org/downloads/", 1, False
    End If
    MsgBox "Please install Python and run this setup again.", vbInformation, "Installation Required"
    WScript.Quit
End If

If CheckLibrariesImport() Then
    MsgBox "All required libraries are already installed and working!" & vbCrLf & vbCrLf & "No installation needed.", vbInformation, "Libraries OK"
Else
    MsgBox "Installing required libraries..." & vbCrLf & vbCrLf & "This may take a few moments.", vbInformation, "Installing Libraries"
    If Not InstallLibraries() Then
        MsgBox "Automatic installation failed." & vbCrLf & vbCrLf & "Please run this command manually:" & vbCrLf & "pip install flask pandas watchdog pystray Pillow", vbExclamation, "Manual Installation Required"
        WScript.Quit
    End If
    MsgBox "Libraries installed successfully!", vbInformation, "Installation Complete"
End If

CreateFolders
SetupConfig
CreateSampleDataEnglish

result = MsgBox("Setup completed successfully!" & vbCrLf & vbCrLf & "Start the Meeting Room System now?", vbYesNo + vbQuestion, "Ready to Start")

If result = vbYes Then
    StartServer
Else
    MsgBox "Setup complete." & vbCrLf & vbCrLf & "To start manually:" & vbCrLf & "  python server_fixed.py" & vbCrLf & vbCrLf & "Then open: http://localhost:5003", vbInformation, "Manual Start"
End If

Function CheckPython()
    On Error Resume Next
    Dim cmd, exitCode
    cmd = "cmd /c ""cd /d """ & currentPath & """ && python --version > nul 2>&1"""
    exitCode = objShell.Run(cmd, 0, True)
    CheckPython = (exitCode = 0)
    On Error GoTo 0
End Function

Function CheckLibrariesImport()
    On Error Resume Next
    Dim cmd, exitCode
    cmd = "cmd /c ""cd /d """ & currentPath & """ && python -c ""import flask, pandas, watchdog, pystray, PIL"" > nul 2>&1"""
    exitCode = objShell.Run(cmd, 0, True)
    CheckLibrariesImport = (exitCode = 0)
    On Error GoTo 0
End Function

Function InstallLibraries()
    On Error Resume Next
    Dim installCmd, exitCode

    installCmd = "cmd /c ""cd /d """ & currentPath & """ && python -m pip install --quiet flask pandas watchdog pystray Pillow > nul 2>&1"""
    exitCode = objShell.Run(installCmd, 0, True)

    If exitCode = 0 Then
        InstallLibraries = CheckLibrariesImport()
    Else
        InstallLibraries = False
    End If
    On Error GoTo 0
End Function

Sub CreateFolders()
    Dim folders, i
    folders = Array("data", "uploads", "processed", "logs")

    For i = 0 To UBound(folders)
        Dim folderPath
        folderPath = currentPath & "\" & folders(i)
        If Not objFSO.FolderExists(folderPath) Then
            objFSO.CreateFolder(folderPath)
        End If
    Next
End Sub

Sub SetupConfig()
    Dim configFile, configDist
    configFile = currentPath & "\config.json"
    configDist = currentPath & "\config_distribution.json"

    If Not objFSO.FileExists(configFile) Then
        If objFSO.FileExists(configDist) Then
            objFSO.CopyFile configDist, configFile
        End If
    End If
End Sub

Sub CreateSampleDataEnglish()
    Dim sampleFile
    sampleFile = currentPath & "\data\processed_bookings.csv"

    If Not objFSO.FileExists(sampleFile) Then
        Dim content
        content = "Application_No,Application_Date,Usage_DateTime,Room_Name,Display_Name,Company,Contact_Person,Total_Amount,Equipment" & vbCrLf
        content = content & "SAMPLE001,2024/09/20,2024/09/21 Morning,Hall-1,Sample Meeting,Sample Corp,Taro Tanaka,5000,Projector" & vbCrLf
        content = content & "SAMPLE002,2024/09/20,2024/09/21 Afternoon,Meeting Room,Regular Meeting,Test Company,Hanako Yamada,3000," & vbCrLf
        content = content & "SAMPLE003,2024/09/20,2024/09/22 Morning,Small Room,Discussion,Demo Inc,Ichiro Suzuki,2000,Whiteboard"

        Dim file
        Set file = objFSO.CreateTextFile(sampleFile, True)
        file.Write content
        file.Close
    End If
End Sub

Sub StartServer()
    Dim startCmd, browserCmd

    MsgBox "Starting server..." & vbCrLf & vbCrLf & "Browser will open automatically in 3 seconds." & vbCrLf & "Server window will be minimized to system tray.", vbInformation, "Starting Server"

    browserCmd = "cmd /c ""timeout /t 3 /nobreak > nul && start http://localhost:5003"""
    objShell.Run browserCmd, 0, False

    startCmd = "cmd /c ""cd /d """ & currentPath & """ && python server_fixed.py"""
    objShell.Run startCmd, 0, False
End Sub