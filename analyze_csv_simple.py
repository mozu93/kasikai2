#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV分析ツール - 初回セットアップ用（シンプル版）
CSVファイルを分析して、自動的に設定ファイルを生成します
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path

def analyze_csv_file(csv_path):
    """CSVファイルを分析してヘッダーと会議室名を抽出"""
    print(f"[CSV分析] ファイル: {csv_path}")
    
    # 複数のエンコードを試行
    encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis', 'iso-2022-jp']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding, engine='python')
            print(f"[成功] エンコード: {encoding}")
            break
        except Exception as e:
            print(f"[失敗] エンコード ({encoding}): {str(e)[:50]}...")
            continue
    
    if df is None:
        print("[エラー] CSVファイルの読み込みに失敗しました")
        return None, None, None
    
    print(f"[データ] 行数: {len(df)}行")
    print(f"[データ] 列数: {len(df.columns)}列")
    
    # ヘッダー情報を取得
    headers = list(df.columns)
    print(f"\\n[ヘッダー] 検出された項目 ({len(headers)}個):")
    for i, header in enumerate(headers, 1):
        print(f"  {i:2d}. {header}")
    
    # 会議室名を抽出（会議室列を探す）
    room_columns = [col for col in headers if '会議室' in col or 'ルーム' in col or 'room' in col.lower()]
    
    if not room_columns:
        print("\\n[警告] 会議室列が見つかりません。手動で指定してください。")
        return headers, [], df
    
    room_column = room_columns[0]  # 最初に見つかった会議室列を使用
    print(f"\\n[会議室] 検出列: {room_column}")
    
    # ユニークな会議室名を抽出
    unique_rooms = df[room_column].dropna().unique()
    unique_rooms = [str(room).strip() for room in unique_rooms if str(room).strip()]
    unique_rooms = sorted(list(set(unique_rooms)))  # 重複削除とソート
    
    print(f"\\n[会議室] 検出された会議室 ({len(unique_rooms)}個):")
    for i, room in enumerate(unique_rooms, 1):
        print(f"  {i:2d}. {room}")
    
    return headers, unique_rooms, df

def generate_room_id(room_name):
    """会議室名から英語IDを生成"""
    if 'ホール' in room_name:
        if 'Ⅰ' in room_name or '１' in room_name or '1' in room_name:
            return "hall-1"
        elif 'Ⅱ' in room_name or '２' in room_name or '2' in room_name:
            return "hall-2"
        elif '全' in room_name:
            return "hall-combined"
        else:
            return "hall-main"
    elif '大会議室' in room_name:
        return "large-room"
    elif '中会議室' in room_name:
        return "medium-room"
    elif '小会議室' in room_name:
        return "small-room"
    elif '研修' in room_name:
        return "training-room"
    elif '役員' in room_name:
        return "executive-room"
    else:
        # その他の場合は連番
        safe_name = room_name.replace(' ', '-').replace('　', '-')
        return f"room-{hash(safe_name) % 1000}"

def generate_config(headers, rooms):
    """分析結果から設定ファイルを生成"""
    print(f"\\n[設定生成] 設定ファイルを生成中...")
    
    # 基本的な会議室設定を生成
    room_configs = []
    for room_name in rooms:
        room_id = generate_room_id(room_name)
        room_configs.append({
            "csv_name": room_name,
            "id": room_id,
            "display_name": room_name
        })
    
    # CSVヘッダーマッピングを生成
    csv_mapping = {}
    
    # 標準的なマッピングパターン
    mapping_patterns = {
        "booking_datetime": ["利用日時", "予約日時", "日時"],
        "room_name": ["会議室", "ルーム", "施設"],
        "display_name": ["案内表示", "表示名", "名称"],
        "company_name": ["事業所", "会社", "団体", "組織"],
        "contact_person": ["担当者", "代表者", "連絡先"],
        "total_amount": ["合計金額", "料金", "金額"],
        "cancellation_date": ["取消日", "キャンセル"],
        "extension": ["延長"],
        "equipment": ["備品", "設備"],
        "purpose": ["利用目的", "目的"],
        "member_type": ["会員種別", "会員"],
        "memo": ["メモ", "備考"],
        "department_name": ["部署", "部門"],
        "zip_code": ["郵便番号"],
        "prefecture": ["都道府県", "県"],
        "city": ["市区町村", "市"],
        "address_rest": ["住所", "以降"],
        "phone_number": ["電話", "TEL"],
        "notes": ["備考", "要望", "持込"]
    }
    
    # ヘッダーをマッピング
    for system_key, patterns in mapping_patterns.items():
        for header in headers:
            for pattern in patterns:
                if pattern in header:
                    csv_mapping[system_key] = header
                    break
            if system_key in csv_mapping:
                break
    
    # モーダル表示項目を生成（重要な項目のみ）
    modal_fields = {}
    important_fields = ["booking_datetime", "room_name", "display_name", "company_name", "contact_person", "extension", "equipment"]
    for field in important_fields:
        if field in csv_mapping:
            modal_fields[csv_mapping[field]] = csv_mapping[field]
    
    # 分割ルールを生成（ホール全がある場合）
    data_split_rules = []
    hall_combined = None
    hall_parts = []
    
    for room in room_configs:
        if '全' in room['csv_name'] and 'ホール' in room['csv_name']:
            hall_combined = room['id']
        elif 'ホール' in room['csv_name'] and ('Ⅰ' in room['csv_name'] or 'Ⅱ' in room['csv_name'] or '１' in room['csv_name'] or '２' in room['csv_name']):
            hall_parts.append(room['id'])
    
    if hall_combined and len(hall_parts) >= 2:
        data_split_rules.append({
            "source_room_id": hall_combined,
            "target_room_ids": hall_parts,
            "enabled": True,
            "description": f"{hall_combined}の予約を{', '.join(hall_parts)}にコピー"
        })
    
    # 内部利用会議室を推定
    internal_room_ids = []
    for room in room_configs:
        if '役員' in room['csv_name'] or '大会議室' in room['csv_name']:
            internal_room_ids.append(room['id'])
    
    # 隠し会議室（分割元）
    hidden_room_ids = []
    if hall_combined:
        hidden_room_ids.append(hall_combined)
    
    # 最終的な設定を生成
    config = {
        "rooms": room_configs,
        "internal_room_ids": internal_room_ids,
        "csv_column_mapping": csv_mapping,
        "modal_fields": modal_fields,
        "data_split_rules": data_split_rules,
        "hidden_room_ids": hidden_room_ids
    }
    
    return config

def save_config(config, output_path="config.json"):
    """設定をファイルに保存"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[保存成功] 設定ファイル: {output_path}")
        return True
    except Exception as e:
        print(f"[保存エラー] {e}")
        return False

def main():
    print("CSV分析ツール - 初回セットアップ用")
    print("=" * 50)
    
    # コマンドライン引数でCSVファイルパスを取得
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # CSVファイルパスを入力
        csv_path = input("分析するCSVファイルのパスを入力してください: ").strip().strip('"')
    
    if not os.path.exists(csv_path):
        print(f"[エラー] ファイルが見つかりません: {csv_path}")
        return
    
    # CSVファイルを分析
    headers, rooms, df = analyze_csv_file(csv_path)
    
    if headers is None:
        print("[エラー] CSV分析に失敗しました")
        return
    
    if not rooms:
        print("[警告] 会議室が検出されませんでした。手動で設定する必要があります。")
        return
    
    # 設定ファイルを生成
    config = generate_config(headers, rooms)
    
    # 設定内容を表示
    print(f"\\n[設定結果]")
    print(f"  会議室数: {len(config['rooms'])}個")
    print(f"  CSVマッピング: {len(config['csv_column_mapping'])}項目")
    print(f"  分割ルール: {len(config['data_split_rules'])}個")
    
    # 保存確認
    save_confirm = input(f"\\nconfig.jsonに保存しますか？ (y/N): ").strip().lower()
    if save_confirm in ['y', 'yes']:
        if save_config(config):
            print(f"\\n[完了] 初期設定が完了しました！")
            print(f"次は run_config_editor.bat で詳細設定を調整してください。")
        else:
            print(f"\\n[エラー] 設定保存に失敗しました")
    else:
        print(f"\\n[キャンセル] 設定は保存されませんでした")

if __name__ == "__main__":
    main()