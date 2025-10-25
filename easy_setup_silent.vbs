Option Explicit

Dim objShell, objFSO, currentPath
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
currentPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

Dim result
result = MsgBox("��c���\��V�X�e�� �Z�b�g�A�b�v" & vbCrLf & vbCrLf & "�t�H���_: " & currentPath & vbCrLf & vbCrLf & "�Z�b�g�A�b�v�𑱂��܂����H", vbYesNo + vbQuestion, "�Z�b�g�A�b�v")

If result = vbNo Then
    WScript.Quit
End If

If Not CheckPython() Then
    result = MsgBox("���̃V�X�e����Python���C���X�g�[������Ă��܂���B" & vbCrLf & vbCrLf & "Python�_�E�����[�h�y�[�W���J���܂����H", vbYesNo + vbExclamation, "Python���K�v�ł�")
    If result = vbYes Then
        objShell.Run "https://www.python.org/downloads/", 1, False
    End If
    MsgBox "Python���C���X�g�[�����Ă���A���̃Z�b�g�A�b�v���ēx���s���Ă��������B", vbInformation, "�C���X�g�[���K�{"
    WScript.Quit
End If

If CheckLibrariesImport() Then
    MsgBox "�K�v�ȃ��C�u�����͂��ׂăC���X�g�[���ς݂ŁA����ɓ��삵�Ă��܂��I" & vbCrLf & vbCrLf & "�C���X�g�[���͕s�v�ł��B", vbInformation, "���C�u����OK"
Else
    MsgBox "�K�v�ȃ��C�u�������C���X�g�[�����ł�..." & vbCrLf & vbCrLf & "���b������ꍇ������܂��B", vbInformation, "���C�u�������C���X�g�[����"
    If Not InstallLibraries() Then
        MsgBox "�����C���X�g�[���Ɏ��s���܂����B" & vbCrLf & vbCrLf & "���̃R�}���h���蓮�Ŏ��s���Ă�������:" & vbCrLf & "pip install flask pandas watchdog pystray Pillow", vbExclamation, "�蓮�C���X�g�[�����K�v�ł�"
        WScript.Quit
    End If
    MsgBox "���C�u�����̃C���X�g�[�����������܂����I", vbInformation, "�C���X�g�[������"
End If

CreateFolders
SetupConfig
CreateSampleDataEnglish

result = MsgBox("�Z�b�g�A�b�v������Ɋ������܂����I" & vbCrLf & vbCrLf & "��c���\��V�X�e�����������N�����܂����H", vbYesNo + vbQuestion, "�J�n��������")

If result = vbYes Then
    StartServer
Else
    MsgBox "�Z�b�g�A�b�v���������܂����B" & vbCrLf & vbCrLf & "�蓮�ŋN������ɂ�:" & vbCrLf & "  python server_fixed.py" & vbCrLf & vbCrLf & "���̌�A�u���E�U�ŊJ���Ă�������: http://localhost:5000", vbInformation, "�蓮�N��"
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

    MsgBox "�T�[�o�[���N�����ł�..." & vbCrLf & vbCrLf & "3�b��Ƀu���E�U�������ŊJ���܂��B" & vbCrLf & "�T�[�o�[�̓V�X�e���g���C�ɍŏ�������܂��B", vbInformation, "�T�[�o�[�N����"

    browserCmd = "cmd /c ""timeout /t 3 /nobreak > nul && start http://localhost:5000"""
    objShell.Run browserCmd, 0, False

    startCmd = "cmd /c ""cd /d """ & currentPath & """ && python server_fixed.py"""
    objShell.Run startCmd, 0, False
End Sub