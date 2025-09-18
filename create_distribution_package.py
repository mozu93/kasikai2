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

def create_distribution():
    """配布用パッケージを作成"""

    # 配布フォルダ名
    dist_folder = "会議室予約システム"

    # 既存の配布フォルダを削除
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)

    # 配布フォルダ作成
    os.makedirs(dist_folder)

    # 必須ファイル
    required_files = [
        "app.py",
        "config_editor.pyw",
        "upload_script.py",
        "host_app.py",
        "index.html",
        "requirements.txt",
        "setup.bat",
        "start_server.bat",
        "run_config_editor.bat",
        "DISTRIBUTION_README.md",
        "QUICK_START.md",
        "SETUP_MANUAL.md",
        "USER_MANUAL.md"
    ]

    # ファイルをコピー
    for file in required_files:
        if os.path.exists(file):
            shutil.copy2(file, dist_folder)
            print(f"✅ コピー完了: {file}")
        else:
            print(f"⚠️  見つからない: {file}")

    # config.json を配布用に変更
    if os.path.exists("config_distribution.json"):
        shutil.copy2("config_distribution.json", os.path.join(dist_folder, "config.json"))
        print("✅ 配布用config.json作成完了")
    else:
        print("❌ config_distribution.json が見つかりません")

    # フォルダをコピー
    folders_to_copy = [
        "config_templates",
        "sample_csv"
    ]

    for folder in folders_to_copy:
        if os.path.exists(folder):
            shutil.copytree(folder, os.path.join(dist_folder, folder))
            print(f"✅ フォルダコピー完了: {folder}")
        else:
            print(f"⚠️  フォルダが見つからない: {folder}")

    # 空のdataフォルダを作成
    os.makedirs(os.path.join(dist_folder, "data"), exist_ok=True)
    print("✅ dataフォルダ作成完了")

    # READMEをメインにリネーム
    dist_readme = os.path.join(dist_folder, "DISTRIBUTION_README.md")
    main_readme = os.path.join(dist_folder, "README.md")
    if os.path.exists(dist_readme):
        os.rename(dist_readme, main_readme)
        print("✅ README.md作成完了")

    print(f"\n📦 配布パッケージ作成完了: {dist_folder}/")

    # ZIP作成の確認
    create_zip = input("\nZIPファイルを作成しますか？ (y/N): ").lower().strip()
    if create_zip == 'y':
        create_zip_file(dist_folder)

def create_zip_file(folder_name):
    """ZIPファイルを作成"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"{folder_name}_{timestamp}.zip"

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, os.path.dirname(folder_name))
                zipf.write(file_path, arc_path)

    print(f"📦 ZIPファイル作成完了: {zip_name}")
    print(f"ファイルサイズ: {os.path.getsize(zip_name) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    print("🚀 会議室予約システム配布パッケージ作成")
    print("=" * 50)
    create_distribution()