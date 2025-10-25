Option Explicit

Dim objShell, objFSO, currentPath
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
currentPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

Dim result
result = MsgBox("会議室予約システム セットアップ" & vbCrLf & vbCrLf & "フォルダ: " & currentPath & vbCrLf & vbCrLf & "セットアップを続けますか？", vbYesNo + vbQuestion, "セットアップ")

If result = vbNo Then
    WScript.Quit
End If

If Not CheckPython() Then
    result = MsgBox("このシステムにPythonがインストールされていません。" & vbCrLf & vbCrLf & "Pythonダウンロードページを開きますか？", vbYesNo + vbExclamation, "Pythonが必要です")
    If result = vbYes Then
        objShell.Run "https://www.python.org/downloads/", 1, False
    End If
    MsgBox "Pythonをインストールしてから、このセットアップを再度実行してください。", vbInformation, "インストール必須"
    WScript.Quit
End If

If CheckLibrariesImport() Then
    MsgBox "必要なライブラリはすべてインストール済みで、正常に動作しています！" & vbCrLf & vbCrLf & "インストールは不要です。", vbInformation, "ライブラリOK"
Else
    MsgBox "必要なライブラリをインストール中です..." & vbCrLf & vbCrLf & "数秒かかる場合があります。", vbInformation, "ライブラリをインストール中"
    If Not InstallLibraries() Then
        MsgBox "自動インストールに失敗しました。" & vbCrLf & vbCrLf & "次のコマンドを手動で実行してください:" & vbCrLf & "pip install flask pandas watchdog pystray Pillow", vbExclamation, "手動インストールが必要です"
        WScript.Quit
    End If
    MsgBox "ライブラリのインストールが完了しました！", vbInformation, "インストール完了"
End If

CreateFolders
SetupConfig
CreateSampleDataEnglish

result = MsgBox("セットアップが正常に完了しました！" & vbCrLf & vbCrLf & "会議室予約システムを今すぐ起動しますか？", vbYesNo + vbQuestion, "開始準備完了")

If result = vbYes Then
    StartServer
Else
    MsgBox "セットアップが完了しました。" & vbCrLf & vbCrLf & "手動で起動するには:" & vbCrLf & "  python server_fixed.py" & vbCrLf & vbCrLf & "その後、ブラウザで開いてください: http://localhost:5000", vbInformation, "手動起動"
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

    MsgBox "サーバーを起動中です..." & vbCrLf & vbCrLf & "3秒後にブラウザが自動で開きます。" & vbCrLf & "サーバーはシステムトレイに最小化されます。", vbInformation, "サーバー起動中"

    browserCmd = "cmd /c ""timeout /t 3 /nobreak > nul && start http://localhost:5000"""
    objShell.Run browserCmd, 0, False

    startCmd = "cmd /c ""cd /d """ & currentPath & """ && python server_fixed.py"""
    objShell.Run startCmd, 0, False
End Sub