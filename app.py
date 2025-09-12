import pandas as pd
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import socket
import time
import json
import logging

# Configure logging
logging.basicConfig(filename='app_debug.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("DEBUG: app.py is being executed!")

CONFIG_FILE = 'config.json'

app = Flask(__name__)
CORS(app)

# --- 設定項目 ---
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
BOOKINGS_CSV = os.path.join(DATA_DIR, 'processed_bookings.csv')

# --- グローバル変数 ---
last_fetch_time = 0
cached_bookings = []
CACHE_DURATION = 5 # キャッシュの有効期間（秒）

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

def fetch_from_csv():
    """CSVファイルからデータを取得する関数"""
    global last_fetch_time, cached_bookings
    current_time = time.time()

    # CSVファイルが更新されているか、またはキャッシュが古いか確認
    try:
        file_mod_time = os.path.getmtime(BOOKINGS_CSV)
        if file_mod_time < last_fetch_time and current_time - last_fetch_time < CACHE_DURATION:
            logging.info("Returning cached data.")
            return cached_bookings
    except FileNotFoundError:
        logging.warning(f"Warning: {BOOKINGS_CSV} not found. No data to display.")
        return []

    logging.info("Fetching new data from CSV...")
    try:
        df = pd.read_csv(BOOKINGS_CSV, encoding='utf-8-sig')
        # pandasは空の値をNaNとして読み込むため、空の文字列に変換する
        df = df.fillna('')
        bookings = df.to_dict('records')
        
        # データをキャッシュ
        cached_bookings = bookings
        last_fetch_time = time.time()
        
        return bookings
    except Exception as e:
        logging.error(f"CSVからのデータ取得中にエラーが発生しました: {e}")
        return []

@app.route('/api/bookings')
def get_bookings():
    bookings = fetch_from_csv()
    return jsonify(bookings)

@app.route('/api/config')
def get_config():
    logging.info(f"Attempting to load config from: {CONFIG_FILE}")
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info("Config loaded successfully.")
        return jsonify(config)
    except FileNotFoundError:
        logging.error(f"Error: {CONFIG_FILE} not found.")
        return jsonify({"error": "config.json not found"}), 404
    except json.JSONDecodeError as e:
        logging.error(f"Error: Error decoding {CONFIG_FILE}. Exception: {e}")
        return jsonify({"error": f"Error decoding config.json: {e}"}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading config: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


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
    print(f"Access the application from this PC at: http://127.0.0.1:{port}")
    print(f"Access from other devices on the same network using: http://{host_ip}:{port}")
    print("-------------------------------------------------")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    run_web_server()