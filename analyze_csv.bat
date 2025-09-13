@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    CSV分析ツール - 初回セットアップ用
echo ========================================
echo.
echo このツールは、CSVファイルを分析して
echo 自動的に初期設定を生成します。
echo.
echo 【使用方法】
echo 1. 自組織のCSVファイルを用意してください
echo 2. ファイルパスを入力してください
echo 3. 生成された設定を確認・保存してください
echo.
pause
echo.

python analyze_csv.py

echo.
echo ========================================
echo CSV分析完了
echo ========================================
echo.
echo 次のステップ:
echo 1. run_config_editor.bat で詳細設定を調整
echo 2. start_server.bat でシステムを起動
echo.
pause