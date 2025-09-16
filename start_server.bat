@echo off
echo ===================================
echo   会議室予約システム 起動中...
echo ===================================
echo.

REM Pythonの確認
python --version >nul 2>&1
if errorlevel 1 (
    echo [エラー] Python がインストールされていません。
    echo Python 3.7以上をインストールしてから再実行してください。
    echo.
    echo 公式サイト: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 必要なライブラリの確認
echo 必要なライブラリの確認中...
python -c "import flask, pandas, watchdog" >nul 2>&1
if errorlevel 1 (
    echo [警告] 必要なライブラリが不足している可能性があります。
    echo setup.bat を実行してライブラリをインストールしてください。
    echo.
    choice /c YN /m "続行しますか？ (Y/N)"
    if errorlevel 2 exit /b 1
)

REM dataフォルダの作成
if not exist "data" mkdir data
if not exist "processed" mkdir processed
if not exist "uploads" mkdir uploads

REM サーバー起動
echo.
echo サーバーを起動しています...
echo ブラウザが自動で開きます: http://localhost:5000
echo.
echo [終了方法] Ctrl+C でサーバーを停止できます
echo.

REM ブラウザを3秒後に開く
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

REM Pythonアプリケーション起動
python app.py

echo.
echo サーバーが停止しました。
pause