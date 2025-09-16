#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
システム起動診断ツール (Windows対応版)
"""

import os
import sys
import json

def main():
    print("=" * 50)
    print("システム診断ツール")
    print("=" * 50)

    # Python確認
    print("Python環境チェック:")
    print(f"   バージョン: {sys.version.split()[0]}")
    print(f"   実行ファイル: {sys.executable}")

    # 必要なライブラリ確認
    print("\n必要なライブラリチェック:")
    required_modules = ['flask', 'pandas', 'watchdog']
    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"   OK {module}: インストール済み")
        except ImportError:
            print(f"   NG {module}: 未インストール")
            missing_modules.append(module)

    # 必要なファイル確認
    print("\n必要なファイルチェック:")
    required_files = ['app.py', 'config.json', 'index.html']
    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            print(f"   OK {file}: 存在")
        else:
            print(f"   NG {file}: 見つかりません")
            missing_files.append(file)

    # 設定ファイル確認
    print("\n設定ファイルチェック:")
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            rooms = config.get('rooms', [])
            print(f"   OK config.json: 正常 (会議室数: {len(rooms)})")
            config_ok = True
    except Exception as e:
        print(f"   NG config.json: エラー - {e}")
        config_ok = False

    # フォルダ確認・作成
    print("\n必要なフォルダチェック:")
    folders = ['data', 'uploads', 'processed']
    for folder in folders:
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                print(f"   OK {folder}: 作成しました")
            except Exception as e:
                print(f"   NG {folder}: 作成失敗 - {e}")
        else:
            print(f"   OK {folder}: 存在")

    # ポート確認
    print("\nポート5000確認:")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()

        if result == 0:
            print("   WARN ポート5000は既に使用中")
            port_ok = False
        else:
            print("   OK ポート5000は利用可能")
            port_ok = True
    except Exception as e:
        print(f"   NG ポートチェックエラー: {e}")
        port_ok = False

    # 結果判定
    print("\n" + "=" * 50)
    print("診断結果")
    print("=" * 50)

    all_issues = missing_modules + missing_files
    if not config_ok:
        all_issues.append("config.json")

    if len(all_issues) == 0:
        print("OK システムは正常に動作できます！")
        print("\nシステムを開始するには:")
        print("   python app.py")
        print("   ブラウザで http://localhost:5000 にアクセス")

        if not port_ok:
            print("\n注意: ポート5000が使用中のため")
            print("      別のポートで起動する可能性があります")

        return True
    else:
        print("NG 以下の問題があります:")
        for issue in all_issues:
            print(f"   - {issue}")

        print("\n解決方法:")
        if missing_modules:
            print("   1. pip install -r requirements.txt")
        if missing_files:
            print("   2. 配布ファイルを再確認してください")
        if not config_ok:
            print("   3. first_time_setup.py を実行してください")

        return False

if __name__ == "__main__":
    try:
        result = main()
        if not result:
            input("\nEnterキーを押して終了...")
    except Exception as e:
        print(f"診断エラー: {e}")
        input("Enterキーを押して終了...")