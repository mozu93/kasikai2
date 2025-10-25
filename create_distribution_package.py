#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会議室予約システム配布パッケージ作成スクリプト
"""

import os
import shutil
import zipfile
from pathlib import Path
import datetime
import sys
import io

# 標準出力のエンコーディングをUTF-8に設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_distribution():
    """配布用パッケージを作成"""

    # 配布フォルダ名
    dist_folder = "会議室予約システム_配布版"

    # 既存の配布フォルダを削除
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)

    # 配布フォルダ作成
    os.makedirs(dist_folder)

    # 必須ファイル
    required_files = [
        "server_fixed.py",
        "config_editor.pyw",
        "index.html",
        "requirements.txt",
        "easy_setup_silent.vbs",
        "start_server.bat",
        "trouble_shooter.bat",
        "DISTRIBUTION_README.md",
        "QUICK_START.md",
        "SETUP_MANUAL.md",
        "USER_MANUAL.md",
        "config.json",
        "code_quality_check.py",
        "test_system_simple.py",
        "PRODUCTION_READINESS.md",
        "📋 超簡単！3分で完了ガイド.md",
    ]

    # ファイルをコピー
    for file in required_files:
        try:
            if os.path.exists(file):
                shutil.copy2(file, dist_folder)
                print(f"コピー完了: {file}")
            else:
                print(f"見つからない: {file}")
        except Exception as e:
            print(f"エラー: {file} のコピー中にエラーが発生しました: {e}")

    # フォルダをコピー
    folders_to_copy = [
        "config_templates",
    ]

    for folder in folders_to_copy:
        try:
            if os.path.exists(folder):
                shutil.copytree(folder, os.path.join(dist_folder, folder))
                print(f"フォルダコピー完了: {folder}")
            else:
                print(f"フォルダが見つからない: {folder}")
        except Exception as e:
            print(f"エラー: {folder} のコピー中にエラーが発生しました: {e}")

    # 空のフォルダを作成
    empty_folders = ["data", "uploads", "processed"]
    for folder in empty_folders:
        try:
            os.makedirs(os.path.join(dist_folder, folder), exist_ok=True)
            # .gitkeepファイルを作成して空フォルダをgitの管理対象にする
            with open(os.path.join(dist_folder, folder, ".gitkeep"), "w") as f:
                pass
            print(f"空フォルダ作成完了: {folder}")
        except Exception as e:
            print(f"エラー: {folder} の作成中にエラーが発生しました: {e}")

    # READMEをメインにリネーム
    try:
        dist_readme = os.path.join(dist_folder, "DISTRIBUTION_README.md")
        main_readme = os.path.join(dist_folder, "配布パッケージ_README.md")
        if os.path.exists(dist_readme):
            os.rename(dist_readme, main_readme)
            print("配布パッケージ_README.md作成完了")
    except Exception as e:
        print(f"エラー: README.mdのリネーム中にエラーが発生しました: {e}")

    print(f"\n配布パッケージ作成完了: {dist_folder}/")

    # ZIPファイルを作成
    create_zip_file(dist_folder)

def create_zip_file(folder_name):
    """ZIPファイルを作成"""
    zip_name = f"{folder_name}.zip"
    
    # 既存のZIPファイルを削除
    if os.path.exists(zip_name):
        os.remove(zip_name)

    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_name):
                # .gitフォルダを無視する
                if '.git' in dirs:
                    dirs.remove('.git')
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, os.path.dirname(folder_name))
                    zipf.write(file_path, arc_path)

        print(f"ZIPファイル作成完了: {zip_name}")
        print(f"ファイルサイズ: {os.path.getsize(zip_name) / 1024 / 1024:.1f} MB")
    except Exception as e:
        print(f"エラー: ZIPファイルの作成中にエラーが発生しました: {e}")

if __name__ == "__main__":
    print("会議室予約システム配布パッケージ作成")
    print("=" * 50)
    create_distribution()