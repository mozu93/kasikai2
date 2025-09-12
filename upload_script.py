import time
import os
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import json # Added import json

# --- 設定項目 ---
CONFIG_FILE = 'config.json'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, '申し込みデータ')
PROCESSED_DIR = os.path.join(BASE_DIR, '処理済み')
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_CSV = os.path.join(DATA_DIR, 'processed_bookings.csv')

# --- グローバル変数 ---
upload_timer = None
UPLOAD_DELAY = 5  # 5秒に変更

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config.json: {e}. Using default settings.")
        return {
            "rooms": [
                {"csv_name": "ホールⅠ", "id": "hall-1", "display_name": "ホールⅠ"},
                {"csv_name": "ホールⅡ", "id": "hall-2", "display_name": "ホールⅡ"},
                {"csv_name": "ホール全", "id": "hall-combined", "display_name": "ホール全"},
                {"csv_name": "中会議室", "id": "medium-room", "display_name": "中会議室"},
                {"csv_name": "研修室", "id": "training-room", "display_name": "研修室"},
                {"csv_name": "小会議室", "id": "small-room", "display_name": "小会議室"},
                {"csv_name": "大会議室", "id": "large-room", "display_name": "大会議室"},
                {"csv_name": "役員会議室", "id": "executive-room", "display_name": "役員会議室"}
            ],
            "internal_room_ids": ["large-room", "executive-room"],
            "csv_column_mapping": {
                "booking_datetime": "利用日時(予約内容)",
                "room_name": "会議室(予約内容)",
                "total_amount": "合計金額(予約内容)",
                "cancellation_date": "取消日(予約内容)",
                "display_name": "案内表示名(予約内容)",
                "company_name": "事業所名",
                "extension": "延長(予約内容)",
                "equipment": "備品(予約内容)",
                "notes": "備考（ご要望や持込機材などございましたらご入力ください。）",
                "memo": "メモ",
                "purpose": "利用目的(予約内容)",
                "member_type": "会員種別(予約内容)",
                "department_name": "部署名",
                "contact_person": "担当者名",
                "zip_code": "郵便番号",
                "prefecture": "都道府県",
                "city": "市区町村",
                "address_rest": "以降の住所",
                "phone_number": "電話番号"
            },
            "modal_fields": {
                "利用日時": "booking_datetime",
                "会議室": "room_name",
                "案内表示名": "display_name",
                "事業所名": "company_name",
                "担当者名": "contact_person",
                "延長": "extension",
                "備品": "equipment"
            }
        }

def get_room_mapping():
    config = load_config()
    return {room['csv_name']: room['id'] for room in config['rooms']}

def get_csv_column_mapping():
    config = load_config()
    return config.get('csv_column_mapping', {})

def parse_booking_data(df):
    """DataFrameを解析して予約リストを返す関数"""
    if df.empty:
        return []

    room_mapping = get_room_mapping()
    # CSVのヘッダーはそのまま保持（英語に変換しない）

    bookings = []
    slot_mapping = {'午前': 'morning', '午後': 'afternoon', '夜間': 'night'}

    # '利用日時(予約内容)' 列が存在するか確認
    datetime_column = '利用日時(予約内容)'
    room_column = '会議室(予約内容)'
    
    if datetime_column not in df.columns:
        print(f"エラー: '{datetime_column}' 列が見つかりません。")
        return []

    all_bookings_data = df.to_dict('records')

    for row_data in all_bookings_data:
        date_time_str = row_data.get(datetime_column)
        if not date_time_str or pd.isna(date_time_str):
            continue
        room_str = row_data.get(room_column)
        try:
            parts = str(date_time_str).rsplit(' ', 1)
            date_part = parts[0]
            time_part = parts[1]
        except (IndexError, AttributeError):
            continue
        try:
            date_obj = pd.to_datetime(date_part, format='%Y年%m月%d日')
            formatted_date = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue
        room_id = room_mapping.get(room_str)
        if not room_id:
            continue
        time_slots = []
        if '・' in time_part:
            time_slots.extend(time_part.split('・'))
        elif time_part == '一日':
            time_slots.extend(['午前', '午後', '夜間'])
        else:
            time_slots.append(time_part)
        for slot in time_slots:
            slot_id = slot_mapping.get(slot)
            if slot_id:
                is_special = False
                total_amount_str = str(row_data.get('合計金額(予約内容)', '')).replace(',', '')
                try:
                    if total_amount_str.strip() != '' and float(total_amount_str) == 0:
                        is_special = True
                except (ValueError, TypeError):
                    pass

                booking_base = row_data.copy()
                booking_base['date'] = formatted_date
                booking_base['slot'] = slot_id
                booking_base['isSpecial'] = is_special

                if room_id == 'hall-combined':
                    for hall_id in ['hall-1', 'hall-2']:
                        entry = booking_base.copy()
                        entry['id'] = f"{formatted_date}-{hall_id}-{slot_id}"
                        entry['roomId'] = hall_id
                        bookings.append(entry)
                else:
                    entry = booking_base.copy()
                    entry['id'] = f"{formatted_date}-{room_id}-{slot_id}"
                    entry['roomId'] = room_id
                    bookings.append(entry)
    return bookings

def process_files():
    """CSVファイルを処理して単一のCSVに統合する関数"""
    print(f'{time.ctime()}: 処理を開始します。', flush=True)

    try:
        csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
        if not csv_files:
            print('処理対象のCSVファイルがありません。', flush=True)
            return

        all_data_raw = pd.DataFrame()
        processed_file_paths = []
        for file in csv_files:
            file_path = os.path.join(INPUT_DIR, file)
            
            # Try multiple encodings
            encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis', 'iso-2022-jp']
            df_loaded = False
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, engine='python')
                    all_data_raw = pd.concat([all_data_raw, df], ignore_index=True)
                    processed_file_paths.append(file_path)
                    df_loaded = True
                    print(f'ファイル読み込み成功: {file} (エンコーディング: {encoding})', flush=True)
                    break
                except Exception:
                    continue
            
            if not df_loaded:
                print(f'ファイル読み込みエラー: {file_path} - サポートされているエンコーディングで読み込めませんでした', flush=True)
                continue

        if all_data_raw.empty:
            print('読み込むデータがありませんでした。', flush=True)
            return

        # 3. キャンセル済み予約を除外
        print("キャンセル済み予約を除外しています...", flush=True)
        cancellation_column = '取消日(予約内容)'
        if cancellation_column in all_data_raw.columns:
            valid_data_df = all_data_raw[all_data_raw[cancellation_column].isnull()].copy()
        else:
            valid_data_df = all_data_raw.copy()

        print("予約の重複を排除しています...S", flush=True)
        bookings_with_ids = parse_booking_data(valid_data_df)
        unique_bookings_map = {}
        for booking in bookings_with_ids:
            unique_bookings_map[booking['id']] = booking

        final_bookings = list(unique_bookings_map.values())
        print(f"重複排除後、ユニークな予約が {len(final_bookings)}件見つかりました。", flush=True)

        if not final_bookings:
            print("書き込むデータがありません。", flush=True)
        else:
            final_df = pd.DataFrame(final_bookings)
            # スプレッドシートに不要なヘルパー列を削除 (今回は不要だが、将来的な互換性のため残す)
            columns_to_drop = ['id', 'roomId', 'date', 'slot', 'isSpecial']
            existing_columns_to_drop = [col for col in columns_to_drop if col in final_df.columns]
            final_df = final_df.drop(columns=existing_columns_to_drop, errors='ignore')
            final_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
            print(f'{len(final_df)}行のデータを {OUTPUT_CSV} に書き込みました。', flush=True)

        # 処理済みファイルを移動
        if not os.path.exists(PROCESSED_DIR):
            os.makedirs(PROCESSED_DIR)
        for path in processed_file_paths:
            file_name = os.path.basename(path)
            dst = os.path.join(PROCESSED_DIR, file_name)
            # 移動先にファイルが既に存在する場合は上書きする
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(path, dst)
        print(f'{len(processed_file_paths)}個のCSVファイルを処理済みフォルダに移動しました。', flush=True)

    except Exception as e:
        print(f'エラーが発生しました: {e}', flush=True)
    finally:
        print(f'{time.ctime()}: 処理を終了します。', flush=True)

class DebounceEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory or not event.src_path.endswith('.csv'):
            return

        global upload_timer
        if upload_timer and upload_timer.is_alive():
            upload_timer.cancel()

        print(f"{time.ctime()}: ファイル変更を検知。タイマーをリセットします。", flush=True)
        upload_timer = threading.Timer(UPLOAD_DELAY, process_files)
        upload_timer.start()
        print(f"{time.ctime()}: {UPLOAD_DELAY}秒後に処理をスケジュールしました。", flush=True)

def start_file_watcher():
    for directory in [INPUT_DIR, PROCESSED_DIR, DATA_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f'フォルダを作成しました: {directory}', flush=True)

    print(f'{time.ctime()}: 監視を開始します。監視対象: {INPUT_DIR}', flush=True)
    # 初回起動時に一度処理を実行
    process_files()
    
    event_handler = DebounceEventHandler()
    observer = Observer()
    observer.schedule(event_handler, INPUT_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_file_watcher()