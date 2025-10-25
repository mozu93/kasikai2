#!/usr/bin/env python3
"""
会議室予約システム - 簡単テストスクリプト
基本機能の動作確認を行います
"""

import os
import json
import sys
import pandas as pd
from datetime import datetime

def test_config_loading():
    """設定ファイルの読み込みテスト"""
    print(">> 設定ファイル読み込みテスト...")

    config_file = 'config.json'
    if not os.path.exists(config_file):
        print("ERROR: config.jsonが見つかりません")
        return False

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 必要なキーが存在するかチェック
        required_keys = ['rooms', 'modal_fields', 'csv_column_mapping']
        for key in required_keys:
            if key not in config:
                print(f"ERROR: 必要なキー '{key}' が設定ファイルにありません")
                return False

        print(f"OK: 設定ファイル読み込み成功 - 会議室数: {len(config['rooms'])}")
        return True

    except json.JSONDecodeError as e:
        print(f"ERROR: 設定ファイルのJSON形式が無効です: {e}")
        return False
    except Exception as e:
        print(f"ERROR: 設定ファイル読み込みエラー: {e}")
        return False

def test_csv_processing():
    """CSVファイル処理テスト"""
    print(">> CSVファイル処理テスト...")

    csv_file = os.path.join('data', 'processed_bookings.csv')
    if not os.path.exists(csv_file):
        print("ERROR: processed_bookings.csvが見つかりません")
        return False

    try:
        # 複数エンコーディングでの読み込みテスト
        encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis']
        df = None

        for encoding in encodings:
            try:
                df = pd.read_csv(csv_file, encoding=encoding)
                print(f"OK: CSV読み込み成功 ({encoding}) - 行数: {len(df)}, 列数: {len(df.columns)}")
                break
            except Exception:
                continue

        if df is None:
            print("ERROR: CSVファイルの読み込みに失敗しました")
            return False

        # データの基本検証
        if len(df) == 0:
            print("WARNING: CSVファイルにデータが含まれていません")
            return True

        # 列名の確認
        print(f"INFO: CSV列名: {list(df.columns)[:5]}...") if len(df.columns) > 5 else print(f"INFO: CSV列名: {list(df.columns)}")
        return True

    except Exception as e:
        print(f"ERROR: CSV処理エラー: {e}")
        return False

def test_dependencies():
    """依存関係テスト"""
    print(">> 依存パッケージテスト...")

    required_packages = [
        ('flask', 'Flask'),
        ('pandas', 'pandas'),
        ('watchdog', 'watchdog'),
        ('pystray', 'pystray'),
        ('PIL', 'Pillow')
    ]

    missing_packages = []

    for package, display_name in required_packages:
        try:
            __import__(package)
            print(f"OK: パッケージ確認: {display_name}")
        except ImportError:
            print(f"ERROR: パッケージ不足: {display_name}")
            missing_packages.append(display_name)

    if missing_packages:
        print(f"WARNING: 不足パッケージをインストールしてください:")
        print(f"pip install {' '.join(missing_packages).lower()}")
        return False

    return True

def run_all_tests():
    """全テストを実行"""
    print("*** 会議室予約システム - テスト開始 ***")
    print("=" * 50)

    tests = [
        ("依存関係", test_dependencies),
        ("設定ファイル", test_config_loading),
        ("CSV処理", test_csv_processing)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n>> {test_name}テスト実行中...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR: {test_name}テストでエラー: {e}")
            results.append((test_name, False))

    # 結果サマリー
    print("\n" + "=" * 50)
    print("*** テスト結果サマリー ***")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\n成功: {passed}/{total}")

    if passed == total:
        print("*** 全テストが成功しました！システムは正常に動作する準備ができています。")
    else:
        print("WARNING: いくつかのテストが失敗しました。上記のエラーを修正してください。")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)