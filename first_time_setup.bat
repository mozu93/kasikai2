@echo off
chcp 65001 >nul 2>&1

REM ===================================
REM   🔧 会議室予約システム 初回設定
REM ===================================

echo.
echo ╔══════════════════════════════════════════╗
echo ║        🔧 会議室予約システム初回設定        ║
echo ║                                          ║
echo ║  簡単なGUI画面で設定できます               ║
echo ╚══════════════════════════════════════════╝
echo.

REM Pythonの確認
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python がインストールされていません。
    echo 📥 まず easy_setup.bat を実行してください。
    pause
    exit /b 1
)

echo 🔧 設定画面を起動中...

REM 設定ツール起動
if exist "first_time_setup.py" (
    python first_time_setup.py
) else (
    echo ❌ 設定ツールが見つかりません。
    echo 📄 ファイルが不足している可能性があります。
    pause
    exit /b 1
)

echo.
echo ✅ 設定が完了しました。
echo 🚀 システムを開始するには「🚀 システム開始.bat」をダブルクリックしてください。
pause