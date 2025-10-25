@echo off
chcp 65001 >nul 2>&1

REM ===================================
REM   🔧 トラブルシューティング自動診断
REM ===================================

echo.
echo ╔══════════════════════════════════════════╗
echo ║        🔧 システム診断ツール              ║
echo ║                                          ║
echo ║  問題を自動で診断・解決します              ║
echo ╚══════════════════════════════════════════╝
echo.

set issue_count=0

echo 📋 システムの状態をチェックしています...
echo.

REM Python確認
echo [1/6] 🐍 Python インストール確認...
python --version >nul 2>&1
if errorlevel 1 (
    echo    ❌ Python がインストールされていません
    set /a issue_count+=1
    set python_missing=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
    echo    ✅ Python !python_version! インストール済み
    set python_missing=0
)

REM 必要なライブラリ確認
echo [2/6] 📚 必要なライブラリ確認...
if !python_missing!==0 (
    python -c "import flask, pandas, watchdog" >nul 2>&1
    if errorlevel 1 (
        echo    ❌ 必要なライブラリが不足しています
        set /a issue_count+=1
        set libs_missing=1
    ) else (
        echo    ✅ ライブラリインストール済み
        set libs_missing=0
    )
) else (
    echo    ⚠️  Python未インストールのためスキップ
    set libs_missing=0
)

REM 設定ファイル確認
echo [3/6] ⚙️  設定ファイル確認...
if exist "config.json" (
    echo    ✅ config.json 存在確認済み
    set config_missing=0
) else (
    echo    ❌ config.json がありません
    set /a issue_count+=1
    set config_missing=1
)

REM 必要なフォルダ確認
echo [4/6] 📁 必要なフォルダ確認...
set folder_issues=0
if not exist "data" (
    echo    ⚠️  data フォルダがありません
    mkdir "data" >nul 2>&1
    if exist "data" (
        echo    ✅ data フォルダを作成しました
    ) else (
        echo    ❌ data フォルダの作成に失敗
        set /a folder_issues+=1
    )
) else (
    echo    ✅ data フォルダ確認済み
)

if not exist "uploads" (
    echo    ⚠️  uploads フォルダがありません
    mkdir "uploads" >nul 2>&1
    if exist "uploads" (
        echo    ✅ uploads フォルダを作成しました
    ) else (
        echo    ❌ uploads フォルダの作成に失敗
        set /a folder_issues+=1
    )
) else (
    echo    ✅ uploads フォルダ確認済み
)

if not exist "processed" (
    echo    ⚠️  processed フォルダがありません
    mkdir "processed" >nul 2>&1
    if exist "processed" (
        echo    ✅ processed フォルダを作成しました
    ) else (
        echo    ❌ processed フォルダの作成に失敗
        set /a folder_issues+=1
    )
) else (
    echo    ✅ processed フォルダ確認済み
)

if !folder_issues! GTR 0 (
    set /a issue_count+=1
)

REM メインファイル確認
echo [5/6] 📄 メインファイル確認...
set file_issues=0
set required_files=app.py config_editor.pyw upload_script.py index.html requirements.txt

for %%f in (!required_files!) do (
    if exist "%%f" (
        echo    ✅ %%f 確認済み
    ) else (
        echo    ❌ %%f がありません
        set /a file_issues+=1
    )
)

if !file_issues! GTR 0 (
    set /a issue_count+=1
    set files_missing=1
) else (
    set files_missing=0
)

REM ポート使用状況確認
echo [6/6] 🌐 ポート 5000 確認...
netstat -an | findstr ":5000 " >nul 2>&1
if not errorlevel 1 (
    echo    ⚠️  ポート 5000 が既に使用されています
    set port_in_use=1
    set /a issue_count+=1
) else (
    echo    ✅ ポート 5000 利用可能
    set port_in_use=0
)

echo.
echo ════════════════════════════════════════
echo 📊 診断結果
echo ════════════════════════════════════════

if !issue_count!==0 (
    echo.
    echo ✅ 問題は見つかりませんでした！
    echo 🚀 システムは正常に動作できる状態です。
    echo.
    echo 💡 システムを開始するには:
    echo    📁 「🚀 システム開始.bat」をダブルクリック
    echo.
) else (
    echo.
    echo ⚠️  !issue_count! 個の問題が見つかりました:
    echo.

    REM 修復案内
    if !python_missing!==1 (
        echo 🔧 Python インストール不足
        echo    解決方法: 📁 easy_setup.bat を実行
        echo.
    )

    if !libs_missing!==1 (
        echo 🔧 ライブラリ不足
        echo    解決方法: 📁 easy_setup.bat を実行
        echo.
    )

    if !config_missing!==1 (
        echo 🔧 設定ファイル不足
        echo    解決方法: 📁 first_time_setup.bat を実行
        echo.
    )

    if !files_missing!==1 (
        echo 🔧 システムファイル不足
        echo    解決方法: 配布ファイルを再展開してください
        echo.
    )

    if !port_in_use!==1 (
        echo 🔧 ポート競合
        echo    解決方法: 他のアプリを終了するか、PCを再起動
        echo.
    )

    echo 🚀 自動修復を試行しますか？
    echo    [1] はい - 可能な問題を自動修復
    echo    [2] いいえ - 手動で解決
    echo.
    choice /c 12 /n /m "数字を選択してください (1,2): "

    if !errorlevel!==1 (
        echo.
        echo 🔧 自動修復を実行中...
        call :auto_fix
    ) else (
        echo.
        echo 💡 上記の解決方法を参考に手動で修復してください。
    )
)

echo.
pause
exit /b 0

:auto_fix
REM 自動修復処理
echo.
echo ⚡ 自動修復処理開始...

if !config_missing!==1 (
    if exist "config_distribution.json" (
        copy "config_distribution.json" "config.json" >nul 2>&1
        echo ✅ 設定ファイルを復元しました
    )
)

if !libs_missing!==1 (
    echo 📚 ライブラリをインストール中...
    python -m pip install --upgrade pip >nul 2>&1
    if exist "requirements.txt" (
        python -m pip install -r requirements.txt >nul 2>&1
        echo ✅ ライブラリインストール完了
    )
)

echo ✅ 自動修復完了
echo 💡 修復後もエラーが続く場合は、easy_setup.bat を実行してください。
echo.
goto :eof