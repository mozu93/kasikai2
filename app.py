import pandas as pd
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import socket
import gspread
from google.oauth2.service_account import Credentials
import time

app = Flask(__name__)
CORS(app)

# --- 設定項目 ---
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_NAME = 'kasikai予約台帳'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# --- グローバル変数 ---
last_fetch_time = 0
cached_bookings = []
CACHE_DURATION = 60 # キャッシュの有効期間（秒）

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

def fetch_from_spreadsheet():
    """スプレッドシートからデータを取得する関数"""
    global last_fetch_time, cached_bookings
    current_time = time.time()

    # キャッシュが有効な場合はキャッシュを返す
    if current_time - last_fetch_time < CACHE_DURATION and cached_bookings:
        print("Returning cached data.")
        return cached_bookings

    print("Fetching new data from spreadsheet...")
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.sheet1
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        df = df.astype(object).fillna('')
        
        bookings = parse_booking_data(df)
        
        # データをキャッシュ
        cached_bookings = bookings
        last_fetch_time = current_time
        
        return bookings
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"エラー: スプレッドシート '{SPREADSHEET_NAME}' が見つかりません。")
        return []
    except Exception as e:
        print(f"スプレッドシートからのデータ取得中にエラーが発生しました: {e}")
        return []

def parse_booking_data(df):
    """DataFrameを解析して予約リストを返す関数"""
    if df.empty:
        return []

    bookings = []
    room_mapping = {
        'ホールⅠ': 'hall-1', 'ホールⅡ': 'hall-2', 'ホール全': 'hall-combined',
        '中会議室': 'medium-room', '研修室': 'training-room', '小会議室': 'small-room',
        '大会議室': 'large-room', '役員会議室': 'executive-room'
    }
    slot_mapping = {'午前': 'morning', '午後': 'afternoon', '夜間': 'night'}

    all_bookings_data = df.to_dict('records')

    for row_data in all_bookings_data:
        date_time_str = row_data.get('利用日時(予約内容)')
        if not date_time_str:
            continue
        room_str = row_data.get('会議室(予約内容)')
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
                # 「合計金額(予約内容)」が0の場合に特別なフラグを立てる
                is_special = False
                total_amount_str = str(row_data.get('合計金額(予約内容)', '')).replace(',', '')
                try:
                    if total_amount_str.strip() != '' and float(total_amount_str) == 0:
                        is_special = True
                except (ValueError, TypeError):
                    pass # 数値に変換できない場合はFalseのまま

                # 「ホール全」の場合は「ホールⅠ」と「ホールⅡ」の両方に予約を作成
                if room_id == 'hall-combined':
                    # ホールⅠの予約を作成
                    booking_entry_1 = row_data.copy()
                    booking_entry_1['id'] = f"{formatted_date}-hall-1-{slot_id}"
                    booking_entry_1['roomId'] = 'hall-1'
                    booking_entry_1['date'] = formatted_date
                    booking_entry_1['slot'] = slot_id
                    booking_entry_1['isSpecial'] = is_special
                    bookings.append(booking_entry_1)
                    
                    # ホールⅡの予約を作成
                    booking_entry_2 = row_data.copy()
                    booking_entry_2['id'] = f"{formatted_date}-hall-2-{slot_id}"
                    booking_entry_2['roomId'] = 'hall-2'
                    booking_entry_2['date'] = formatted_date
                    booking_entry_2['slot'] = slot_id
                    booking_entry_2['isSpecial'] = is_special
                    bookings.append(booking_entry_2)
                else:
                    # 通常の予約を作成
                    booking_entry = row_data.copy()
                    booking_entry['id'] = f"{formatted_date}-{room_id}-{slot_id}"
                    booking_entry['roomId'] = room_id
                    booking_entry['date'] = formatted_date
                    booking_entry['slot'] = slot_id
                    booking_entry['isSpecial'] = is_special
                    bookings.append(booking_entry)
    return bookings

@app.route('/api/bookings')
def get_bookings():
    bookings = fetch_from_spreadsheet()
    return jsonify(bookings)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_web_server():
    host_ip = get_local_ip()
    port = 5000
    print("--- Starting Web Server ---")
    print(f"Access the application from other devices on the same network using the following URL:")
    print(f"http://{host_ip}:{port}")
    print("-------------------------------------------------")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    run_web_server()

