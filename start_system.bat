@echo off
chcp 65001 >nul 2>&1

REM ===================================
REM   会議室予約システム ワンクリック起動
REM ===================================

echo.
echo ==========================================
echo        会議室予約システム開始
echo.
echo  ブラウザが自動で開きます
echo  http://localhost:5000
echo.
echo  停止するには: Ctrl+C を押してください
echo ==========================================
echo.

REM 初回かどうかチェック
if not exist "config.json" (
    echo 初回起動を検出しました。
    echo 初期設定を開始します...
    echo.

    REM 初期設定ツール起動
    if exist "first_time_setup.py" (
        echo 設定ツールを起動中...
        python first_time_setup.py
        echo.
        echo 初期設定が完了しました。
        echo システムを開始します...
        echo.
    ) else (
        echo 初期設定ツールが見つかりません。
        echo easy_setup.bat を実行してください。
        pause
        exit /b 1
    )
)

REM 必要なフォルダ作成
if not exist "data" mkdir data
if not exist "uploads" mkdir uploads
if not exist "processed" mkdir processed

REM Pythonの確認
python --version >nul 2>&1
if errorlevel 1 (
    echo Python がインストールされていません。
    echo easy_setup.bat を実行してインストールしてください。
    pause
    exit /b 1
)

REM 必要なライブラリの確認
echo ライブラリをチェック中...
python -c "import flask, pandas, watchdog" >nul 2>&1
if errorlevel 1 (
    echo 必要なライブラリが不足しています。
    echo easy_setup.bat を実行してライブラリをインストールしてください。
    pause
    exit /b 1
)

echo システムを起動しています...
echo.

REM ブラウザを3秒後に開く
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

echo 3秒後にブラウザが開きます...
echo ブラウザが開かない場合は手動で http://localhost:5000 にアクセスしてください
echo.

REM Pythonアプリケーション起動
python app.py

echo.
echo システムが停止しました。
echo 再開するには、このファイルをもう一度ダブルクリックしてください。
pause