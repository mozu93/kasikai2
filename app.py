import pandas as pd
from flask import Flask, jsonify, send_from_directory, request, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import socket
import time
import json
import logging
import datetime

# Configure logging
logging.basicConfig(filename='app_debug.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("DEBUG: app.py is being executed!")

CONFIG_FILE = 'config.json'

app = Flask(__name__)
app.secret_key = 'kasikai_upload_secret_key_2025'  # セッション用
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
CORS(app)

# --- 設定項目 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, '申し込みデータ')
BOOKINGS_CSV = os.path.join(DATA_DIR, 'processed_bookings.csv')

# アップロード設定
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# --- グローバル変数 ---
last_fetch_time = 0
cached_bookings = []
CACHE_DURATION = 5 # キャッシュの有効期間（秒）

def allowed_file(filename):
    """許可されたファイル拡張子かチェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    """アップロードディレクトリが存在することを確認"""
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        logging.info(f"Created upload directory: {UPLOAD_DIR}")

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

@app.route('/upload', methods=['POST'])
def upload_file():
    """CSVファイルのアップロード処理"""
    try:
        ensure_upload_dir()
        
        # ファイルが送信されているかチェック
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "ファイルが選択されていません。"}), 400
        
        file = request.files['file']
        
        # ファイル名が空でないかチェック
        if file.filename == '':
            return jsonify({"success": False, "error": "ファイルが選択されていません。"}), 400
        
        # ファイル拡張子をチェック
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "CSVファイルのみアップロード可能です。"}), 400
        
        # ファイル名を安全にする
        filename = secure_filename(file.filename)
        
        # タイムスタンプを追加してファイル名の重複を防ぐ
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        # ファイルを保存
        filepath = os.path.join(UPLOAD_DIR, unique_filename)
        file.save(filepath)
        
        logging.info(f"File uploaded successfully: {unique_filename}")
        
        return jsonify({
            "success": True, 
            "message": f"ファイル '{filename}' がアップロードされました。約1分後にデータが反映されます。",
            "filename": unique_filename
        })
        
    except Exception as e:
        logging.error(f"Upload failed: {e}")
        return jsonify({"success": False, "error": f"アップロードに失敗しました: {str(e)}"}), 500

@app.route('/upload-status')
def upload_status():
    """アップロード可能な状態かチェック"""
    try:
        ensure_upload_dir()
        return jsonify({
            "success": True,
            "upload_dir": UPLOAD_DIR,
            "allowed_extensions": list(ALLOWED_EXTENSIONS),
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024)
        })
    except Exception as e:
        logging.error(f"Upload status check failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


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