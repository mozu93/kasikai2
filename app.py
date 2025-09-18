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

# --- 設定項目 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
BOOKINGS_CSV = os.path.join(DATA_DIR, 'processed_bookings.csv')

# アップロード設定
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app = Flask(__name__)
app.secret_key = 'meeting_room_system_secret_key_2025'  # セッション用
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
CORS(app)

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
    try:
        return send_from_directory(BASE_DIR, 'index.html')
    except FileNotFoundError:
        return "index.html not found", 404

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
        # Try multiple encodings for Japanese CSV files
        for encoding in ['utf-8-sig', 'cp932', 'shift_jis', 'utf-8']:
            try:
                df = pd.read_csv(BOOKINGS_CSV, encoding=encoding)
                logging.info(f"Successfully loaded CSV with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise Exception("Could not decode CSV file with any supported encoding")
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
    """CSVファイルのアップロード処理（複数ファイル対応）"""
    try:
        logging.info("Upload request received")
        logging.info(f"Request files keys: {list(request.files.keys())}")
        logging.info(f"Request form keys: {list(request.form.keys())}")
        
        ensure_upload_dir()
        
        # ファイルが送信されているかチェック
        if 'files' not in request.files:
            logging.error("No 'files' key in request.files")
            return jsonify({"success": False, "error": "ファイルが選択されていません。"}), 400
        
        files = request.files.getlist('files')
        logging.info(f"Number of files received: {len(files)}")
        for i, file in enumerate(files):
            logging.info(f"File {i}: filename='{file.filename}', content_type='{file.content_type}'")
        
        if not files or all(f.filename == '' for f in files):
            logging.error("No valid files received")
            return jsonify({"success": False, "error": "ファイルが選択されていません。"}), 400
        
        uploaded_files = []
        
        for file in files:
            # ファイル名が空でないかチェック
            if file.filename == '':
                continue
            
            # ファイル拡張子をチェック
            if not allowed_file(file.filename):
                continue
            
            # ファイル名処理のデバッグログ
            original_filename = file.filename
            logging.info(f"Original filename: '{original_filename}'")
            
            # より安全なファイル名処理
            # まず元のファイル名から拡張子を抽出
            original_name, original_ext = os.path.splitext(original_filename)
            logging.info(f"Original name: '{original_name}', Original ext: '{original_ext}'")

            # secure_filename を全体のファイル名に適用してから拡張子を処理
            safe_filename = secure_filename(original_filename)
            logging.info(f"Secure filename result: '{safe_filename}'")

            # secure_filename の結果を検証・修正
            if safe_filename and safe_filename != original_ext.replace('.', ''):
                # secure_filename が正常に処理された場合（拡張子だけにならなかった場合）
                safe_name, processed_ext = os.path.splitext(safe_filename)
                # 元の拡張子を優先、なければ処理済み拡張子、最後に.csv
                safe_ext = (original_ext or processed_ext or '.csv').lower()
            else:
                # secure_filename が拡張子だけになった場合や空の場合のフォールバック
                safe_name = "uploaded_file"
                safe_ext = original_ext.lower() if original_ext else '.csv'
                logging.info(f"secure_filename failed for '{original_filename}', using fallback")

            logging.info(f"Safe name: '{safe_name}', Safe ext: '{safe_ext}'")

            # ファイル名が空になった場合の対処
            if not safe_name:
                safe_name = "csv_file"
                logging.info(f"Name was empty, using default: '{safe_name}'")
            
            # タイムスタンプを追加してファイル名の重複を防ぐ
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{safe_name}_{timestamp}{safe_ext}"
            logging.info(f"Final unique filename: '{unique_filename}'")
            
            # ファイルを保存
            filepath = os.path.join(UPLOAD_DIR, unique_filename)
            file.save(filepath)
            
            uploaded_files.append(unique_filename)
            logging.info(f"File uploaded successfully: {unique_filename}")
        
        if not uploaded_files:
            return jsonify({"success": False, "error": "有効なCSVファイルがありませんでした。"}), 400
        
        return jsonify({
            "success": True, 
            "message": f"{len(uploaded_files)}個のファイルがアップロードされました。約1分後にデータが反映されます。",
            "uploaded_files": uploaded_files
        })
        
    except Exception as e:
        logging.error(f"Upload failed: {e}")
        logging.error(f"Exception type: {type(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
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
    port = 5001
    print("--- Starting Web Server ---")
    print(f"Access the application from this PC at: http://127.0.0.1:{port}")
    print(f"Access from other devices on the same network using: http://{host_ip}:{port}")
    print("-------------------------------------------------")
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)

if __name__ == '__main__':
    run_web_server()