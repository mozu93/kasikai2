#!/usr/bin/env python3
"""
会議室予約システム - コード品質チェック
プロダクション対応のための品質確認スクリプト
"""

import os
import sys
import ast
import re
from pathlib import Path
import json

def check_file_encoding(file_path):
    """ファイルエンコーディング確認"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return True, "UTF-8 OK"
    except UnicodeDecodeError:
        return False, "UTF-8読み込みエラー"
    except Exception as e:
        return False, f"エラー: {e}"

def check_python_syntax(file_path):
    """Python構文チェック"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, "構文OK"
    except SyntaxError as e:
        return False, f"構文エラー: {e}"
    except Exception as e:
        return False, f"エラー: {e}"

def check_imports(file_path):
    """import文の確認"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return True, f"imports: {len(imports)}個"
    except Exception as e:
        return False, f"import解析エラー: {e}"

def check_functions(file_path):
    """関数定義の確認"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source)
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return True, f"関数: {len(functions)}個"
    except Exception as e:
        return False, f"関数解析エラー: {e}"

def check_error_handling(file_path):
    """エラーハンドリング確認"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        try_count = source.count('try:')
        except_count = source.count('except')
        logging_count = source.count('logging.') + source.count('logger.')

        score = min(try_count, except_count) + (logging_count > 0)
        return True, f"try/except: {try_count}/{except_count}, log: {logging_count > 0}"
    except Exception as e:
        return False, f"エラー: {e}"

def check_documentation(file_path):
    """ドキュメンテーション確認"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        docstring_count = source.count('"""') // 2
        comment_count = len([line for line in source.split('\n') if line.strip().startswith('#')])

        return True, f"docstring: {docstring_count}, comments: {comment_count}"
    except Exception as e:
        return False, f"エラー: {e}"

def check_config_file():
    """設定ファイル確認"""
    config_file = 'config.json'
    if not os.path.exists(config_file):
        return False, "config.json not found"

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        required_keys = ['rooms', 'modal_fields', 'csv_column_mapping']
        missing_keys = [key for key in required_keys if key not in config]

        if missing_keys:
            return False, f"Missing keys: {missing_keys}"

        return True, f"keys: {len(config.keys())}, rooms: {len(config['rooms'])}"
    except Exception as e:
        return False, f"JSON error: {e}"

def run_quality_check():
    """品質チェック実行"""
    print("=== 会議室予約システム - コード品質チェック ===")
    print()

    # Pythonファイルのチェック
    python_files = [
        'server_fixed.py',
        'config_editor.pyw',
        'test_system_simple.py',
        'create_distribution.py'
    ]

    checks = [
        ('エンコーディング', check_file_encoding),
        ('Python構文', check_python_syntax),
        ('import文', check_imports),
        ('関数定義', check_functions),
        ('エラーハンドリング', check_error_handling),
        ('ドキュメント', check_documentation)
    ]

    results = {}

    for file_path in python_files:
        if not os.path.exists(file_path):
            print(f"SKIP: {file_path} (ファイルが見つかりません)")
            continue

        print(f"\n--- {file_path} ---")
        file_results = {}

        for check_name, check_func in checks:
            success, message = check_func(file_path)
            status = "OK" if success else "NG"
            print(f"  {check_name}: {status} - {message}")
            file_results[check_name] = (success, message)

        results[file_path] = file_results

    # 設定ファイルチェック
    print(f"\n--- config.json ---")
    success, message = check_config_file()
    status = "OK" if success else "NG"
    print(f"  設定ファイル: {status} - {message}")

    # 必要なディレクトリチェック
    print(f"\n--- ディレクトリ構造 ---")
    required_dirs = ['data', 'uploads', 'processed', 'logs']
    for dir_name in required_dirs:
        exists = os.path.exists(dir_name)
        status = "OK" if exists else "NG"
        print(f"  {dir_name}/: {status}")

    # サマリー
    print(f"\n=== 品質チェック完了 ===")

    total_checks = 0
    passed_checks = 0

    for file_path, file_results in results.items():
        for check_name, (success, _) in file_results.items():
            total_checks += 1
            if success:
                passed_checks += 1

    print(f"チェック結果: {passed_checks}/{total_checks} passed")
    print(f"品質スコア: {(passed_checks/total_checks)*100:.1f}%")

    if passed_checks == total_checks:
        print(">>> 品質チェック: すべてのテストが合格しました！")
        return True
    else:
        print(f">>> 品質チェック: {total_checks - passed_checks}個の問題があります。")
        return False

if __name__ == "__main__":
    success = run_quality_check()
    sys.exit(0 if success else 1)