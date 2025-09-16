@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM ===================================
REM   🚀 会議室予約システム 簡単導入 🚀
REM ===================================

echo.
echo ╔══════════════════════════════════════════╗
echo ║        🚀 会議室予約システム 簡単導入        ║
echo ║                                          ║
echo ║  このファイルをダブルクリックするだけで      ║
echo ║  すべての設定が完了します！                  ║
echo ╚══════════════════════════════════════════╝
echo.

REM 管理者権限チェック（オプション）
echo 📋 ステップ1: 環境チェック中...

REM Pythonの確認
echo    ⏳ Python インストール確認中...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ Python がインストールされていません。
    echo.
    echo 📥 Python を自動インストールしますか？
    echo    [1] はい - Python 3.11 を自動インストール
    echo    [2] いいえ - 手動でインストールする
    echo    [3] 終了
    echo.
    choice /c 123 /n /m "数字を選択してください (1,2,3): "

    if !errorlevel!==1 (
        echo.
        echo 🔽 Python 3.11 をダウンロードしています...
        call :download_python
        if errorlevel 1 (
            echo ❌ Python のダウンロードに失敗しました。
            echo 💡 手動で https://python.org からダウンロードしてください。
            pause
            exit /b 1
        )
    ) else if !errorlevel!==2 (
        echo.
        echo 💡 以下の手順で Python をインストールしてください：
        echo    1. https://python.org にアクセス
        echo    2. Python 3.11 以上をダウンロード
        echo    3. インストール時に「Add Python to PATH」をチェック
        echo    4. インストール後、このファイルを再実行
        echo.
        start "" "https://python.org/downloads/"
        pause
        exit /b 1
    ) else (
        echo キャンセルされました。
        pause
        exit /b 0
    )
) else (
    echo    ✅ Python インストール済み
)

REM ライブラリインストール
echo.
echo 📋 ステップ2: 必要なライブラリをインストール中...
echo    ⏳ インストール実行中...

python -m pip install --upgrade pip >nul 2>&1
if exist requirements.txt (
    python -m pip install -r requirements.txt >nul 2>&1
    if !errorlevel!==0 (
        echo    ✅ ライブラリインストール完了
    ) else (
        echo    ⚠️  一部ライブラリのインストールに失敗
        echo       ネットワーク接続を確認してください
    )
) else (
    echo    ⚠️  requirements.txt が見つかりません
)

REM フォルダ作成
echo.
echo 📋 ステップ3: 必要なフォルダを作成中...
if not exist "data" (
    mkdir "data"
    echo    ✅ data フォルダ作成完了
) else (
    echo    ✅ data フォルダ確認済み
)

if not exist "uploads" (
    mkdir "uploads"
    echo    ✅ uploads フォルダ作成完了
) else (
    echo    ✅ uploads フォルダ確認済み
)

if not exist "processed" (
    mkdir "processed"
    echo    ✅ processed フォルダ作成完了
) else (
    echo    ✅ processed フォルダ確認済み
)

REM 設定ファイル確認
echo.
echo 📋 ステップ4: 設定ファイルの確認中...
if not exist "config.json" (
    if exist "config_distribution.json" (
        copy "config_distribution.json" "config.json" >nul
        echo    ✅ 初期設定ファイル作成完了
    ) else (
        echo    ⚠️  設定ファイルが見つかりません
    )
) else (
    echo    ✅ 設定ファイル確認済み
)

REM 初期設定の案内
echo.
echo 📋 ステップ5: 初期設定
echo.
echo 🎯 会議室の設定を行いますか？
echo    [1] はい - 今すぐ設定 (推奨)
echo    [2] あとで - サンプル設定で開始
echo.
choice /c 12 /n /m "数字を選択してください (1,2): "

if !errorlevel!==1 (
    echo.
    echo 🔧 設定エディターを起動します...
    echo    ウィンドウが開いたら会議室名を設定してください
    echo.
    if exist "config_editor.pyw" (
        start "" "python" "config_editor.pyw"
        echo    💡 設定が完了したら、このウィンドウで何かキーを押してください
        pause >nul
    ) else (
        echo    ⚠️  設定エディターが見つかりません
    )
) else (
    echo    ✅ サンプル設定で続行
)

REM サーバー起動確認
echo.
echo 🚀 ステップ6: システムを開始しますか？
echo    [1] はい - 今すぐ開始
echo    [2] いいえ - 後で手動で開始
echo.
choice /c 12 /n /m "数字を選択してください (1,2): "

if !errorlevel!==1 (
    echo.
    echo 🌟 システムを起動しています...
    echo.
    echo ╔══════════════════════════════════════════╗
    echo ║             🎉 導入完了！                 ║
    echo ║                                          ║
    echo ║  ブラウザが自動で開きます                  ║
    echo ║  URL: http://localhost:5000              ║
    echo ║                                          ║
    echo ║  システムを停止する場合:                  ║
    echo ║  このウィンドウで Ctrl+C を押してください  ║
    echo ╚══════════════════════════════════════════╝
    echo.

    REM ブラウザを3秒後に開く
    start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000"

    REM Pythonアプリケーション起動
    python app.py

) else (
    echo.
    echo ╔══════════════════════════════════════════╗
    echo ║             ✅ 導入完了！                 ║
    echo ║                                          ║
    echo ║  システムを開始するには:                  ║
    echo ║  📁 start_server.bat をダブルクリック     ║
    echo ║                                          ║
    echo ║  設定を変更するには:                      ║
    echo ║  📁 run_config_editor.bat をダブルクリック ║
    echo ╚══════════════════════════════════════════╝
    echo.
)

echo システムをお楽しみください！
pause
exit /b 0

REM Python自動ダウンロード機能（簡易版）
:download_python
echo Python の自動インストール機能は準備中です。
echo 手動でインストールしてください。
start "" "https://python.org/downloads/"
exit /b 1