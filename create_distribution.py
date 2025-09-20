#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会議室予約システム配布パッケージ作成スクリプト
現在の最新ファイル構成に対応
"""

import os
import shutil
import zipfile
from pathlib import Path
import datetime
import json

def create_distribution():
    """配布用パッケージを作成"""

    print(">> 会議室予約システム配布パッケージ作成")
    print("=" * 50)

    # 配布フォルダ名
    dist_folder = "会議室予約システム_配布版"

    # 既存の配布フォルダを削除
    if os.path.exists(dist_folder):
        shutil.rmtree(dist_folder)
        print(f"[削除] 既存フォルダを削除: {dist_folder}")

    # 配布フォルダ作成
    os.makedirs(dist_folder)
    print(f"[作成] 配布フォルダ作成: {dist_folder}")

    # 必須ファイル（現在の構成に基づく）
    required_files = [
        # メインアプリケーション
        "server_fixed.py",
        "config_editor.pyw",
        "index.html",
        "requirements.txt",
        "config.json",

        # セットアップ用ファイル
        "easy_setup_gui.vbs",
        "easy_setup.bat",

        # ドキュメント
        "README.md",
        "USER_MANUAL.md",
        "QUICK_START.md",
        "📋 超簡単！3分で完了ガイド.md"
    ]

    # ファイルをコピー
    print("\n[ファイル] ファイルコピー:")
    for file in required_files:
        if os.path.exists(file):
            shutil.copy2(file, dist_folder)
            try:
                print(f"  [OK] {file}")
            except UnicodeEncodeError:
                print(f"  [OK] {file.encode('ascii', 'replace').decode('ascii')}")
        else:
            print(f"  [!] 見つからない: {file}")

    # フォルダをコピー
    folders_to_copy = [
        "config_templates"
    ]

    print("\n[フォルダ] フォルダコピー:")
    for folder in folders_to_copy:
        if os.path.exists(folder):
            shutil.copytree(folder, os.path.join(dist_folder, folder))
            print(f"  [OK] {folder}/")
        else:
            print(f"  [!] フォルダが見つからない: {folder}")

    # 必要な空フォルダを作成
    empty_folders = [
        "data",
        "uploads",
        "processed"
    ]

    print("\n[作成] 必要フォルダ作成:")
    for folder in empty_folders:
        folder_path = os.path.join(dist_folder, folder)
        os.makedirs(folder_path, exist_ok=True)

        # .gitkeepファイルを作成（フォルダ構造を保持）
        gitkeep_path = os.path.join(folder_path, ".gitkeep")
        with open(gitkeep_path, 'w', encoding='utf-8') as f:
            f.write("# このファイルはフォルダ構造を保持するためのものです\n")

        print(f"  [OK] {folder}/")

    # サンプルCSVファイルを作成
    create_sample_csv(dist_folder)

    print(f"\n[完了] 配布パッケージ作成完了: {dist_folder}/")

    # パッケージ内容を確認
    show_package_info(dist_folder)

    # ZIP作成の確認
    create_zip = input("\nZIPファイルを作成しますか？ (y/N): ").lower().strip()
    if create_zip == 'y':
        create_zip_file(dist_folder)

def create_sample_csv(dist_folder):
    """サンプルCSVファイルを作成"""
    uploads_folder = os.path.join(dist_folder, "uploads")

    # サンプルCSVファイルの内容
    sample_content = """利用日時(予約内容),会議室(予約内容),案内表示名(予約内容),事業所名,担当者名,合計金額(予約内容)
2025年01月20日 午前,ホールⅠ,新年度企画会議,テスト株式会社,田中太郎,50000
2025年01月20日 午後,ホールⅡ,研修会,サンプル企業,佐藤花子,30000
2025年01月21日 一日,ホール全,年次総会,大手株式会社,山田次郎,150000
2025年01月22日 夜間,ホールⅠ,特別料金イベント,NPO法人,鈴木一郎,0"""

    sample_csv_path = os.path.join(uploads_folder, "sample_bookings.csv")
    with open(sample_csv_path, 'w', encoding='utf-8-sig') as f:
        f.write(sample_content)

    print(f"  [OK] サンプルCSV作成: uploads/sample_bookings.csv")

def create_zip_file(folder_name):
    """ZIPファイルを作成"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"会議室予約システム_{timestamp}.zip"

    print(f"\n[ZIP] ZIPファイル作成中...")

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                # ZIP内でのパス（最上位フォルダ名を含む）
                arc_path = os.path.relpath(file_path, '.')
                zipf.write(file_path, arc_path)

    file_size_mb = os.path.getsize(zip_name) / 1024 / 1024
    print(f"[完了] ZIPファイル作成完了: {zip_name}")
    print(f"[情報] ファイルサイズ: {file_size_mb:.1f} MB")

def show_package_info(dist_folder):
    """パッケージ内容を表示"""
    print(f"\n[内容] パッケージ内容確認:")

    total_files = 0
    total_size = 0

    for root, dirs, files in os.walk(dist_folder):
        level = root.replace(dist_folder, '').count(os.sep)
        indent = '  ' * level
        folder_name = os.path.basename(root)
        if folder_name:
            print(f'{indent}[DIR] {folder_name}/')

        sub_indent = '  ' * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            file_size_kb = file_size / 1024

            if file_size_kb < 1:
                size_str = f"{file_size}B"
            elif file_size_kb < 1024:
                size_str = f"{file_size_kb:.1f}KB"
            else:
                size_str = f"{file_size_kb/1024:.1f}MB"

            print(f'{sub_indent}[FILE] {file} ({size_str})')
            total_files += 1
            total_size += file_size

    total_size_mb = total_size / 1024 / 1024
    print(f"\n[合計] {total_files}ファイル, {total_size_mb:.1f}MB")

if __name__ == "__main__":
    create_distribution()