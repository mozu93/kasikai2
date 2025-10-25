import pandas as pd
from flask import Flask, jsonify, send_from_directory, request
from werkzeug.utils import secure_filename
import os
import json
import logging
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import glob
import webbrowser
import pystray
from PIL import Image, ImageDraw
import sys
import subprocess
from datetime import datetime, timedelta

# Configure logging with rotation
import logging.handlers

# ログディレクトリを作成
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# ログ設定：ファイルローテーション付き
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')

# ファイルハンドラ（最大10MB、5ファイルまで保持）
file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(LOG_DIR, 'meeting_room_system.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

# コンソールハンドラ
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler.setLevel(logging.INFO)

# ロガー設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Flaskのログも同様に設定
flask_logger = logging.getLogger('werkzeug')
flask_logger.addHandler(file_handler)

print("Starting Meeting Room Booking System...")

CONFIG_FILE = 'config.json'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
BOOKINGS_CSV = os.path.join(DATA_DIR, 'processed_bookings.csv')

# セキュリティ設定
ALLOWED_EXTENSIONS = {'csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_FILES_PER_REQUEST = 10

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# セキュリティヘルパー関数
def allowed_file(filename):
    """許可されたファイル拡張子かチェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_csv_content(file_path):
    """CSVファイルの内容を検証"""
    try:
        # ファイルサイズチェック
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File size too large: {file_size} bytes")
            return False, "ファイルサイズが大きすぎます（最大50MB）"

        # CSV形式チェック（複数エンコーディング対応）
        encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis']
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, nrows=1)
                if len(df.columns) == 0:
                    return False, "CSVファイルに列が見つかりません"
                logger.info(f"CSV validation passed with encoding: {encoding}")
                return True, "OK"
            except Exception as e:
                continue

        return False, "CSVファイルの読み込みに失敗しました"
    except Exception as e:
        logger.error(f"CSV validation error: {e}")
        return False, f"ファイル検証エラー: {str(e)}"

def sanitize_filename(filename):
    """ファイル名をサニタイズ"""
    # secure_filenameを使用し、さらに厳格化
    filename = secure_filename(filename)
    # 日本語ファイル名対応
    if not filename or filename == '':
        filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return filename

# Global variables for system tray
observer = None
server_port = 5000  # デフォルトポート

def load_config():
    """設定ファイルを読み込む"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info("Config loaded successfully")
            return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {CONFIG_FILE}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return None

def cleanup_old_processed_files():
    """当日以前の処理済みファイルを削除"""
    try:
        processed_dir = os.path.join(BASE_DIR, 'processed')
        if not os.path.exists(processed_dir):
            return
        
        today = datetime.now().date()
        deleted_count = 0
        
        for filename in os.listdir(processed_dir):
            file_path = os.path.join(processed_dir, filename)
            if os.path.isfile(file_path):
                try:
                    # ファイルの作成日時を取得
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
                    
                    # 当日以前のファイルを削除
                    if file_mtime < today:
                        os.remove(file_path)
                        deleted_count += 1
                        logging.info(f"Deleted old processed file: {filename}")
                        
                except Exception as e:
                    logging.error(f"Error deleting {filename}: {e}")
        
        if deleted_count > 0:
            logging.info(f"Cleanup completed: {deleted_count} old files deleted")
        else:
            logging.info("No old files to cleanup")
            
    except Exception as e:
        logging.error(f"Error in cleanup_old_processed_files: {e}")

def process_csv_files():
    """uploadsフォルダ内のCSVファイルを処理して結合"""
    try:
        # 古い処理済みファイルを削除
        cleanup_old_processed_files()
        
        # Create directories if they don't exist
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(UPLOADS_DIR, exist_ok=True)

        # Find all CSV files in uploads directory
        csv_files = glob.glob(os.path.join(UPLOADS_DIR, '*.csv'))

        if not csv_files:
            logging.info("No CSV files found in uploads directory")
            return False

        logging.info(f"Found {len(csv_files)} CSV files to process")

        combined_data = []
        processed_files = []

        for csv_file in csv_files:
            try:
                # Try multiple encodings for Japanese CSV files
                df = None
                for encoding in ['utf-8-sig', 'cp932', 'shift_jis', 'utf-8', 'iso-2022-jp']:
                    try:
                        df = pd.read_csv(csv_file, encoding=encoding)
                        logging.info(f"Successfully read {os.path.basename(csv_file)} with encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue

                if df is not None:
                    # Add source file information
                    df['source_file'] = os.path.basename(csv_file)
                    combined_data.append(df)
                    processed_files.append(csv_file)
                    logging.info(f"Processed: {os.path.basename(csv_file)} ({len(df)} rows)")
                else:
                    logging.error(f"Could not read {csv_file} with any encoding")

            except Exception as e:
                logging.error(f"Error processing {csv_file}: {e}")

        if combined_data:
            # Combine all dataframes
            combined_df = pd.concat(combined_data, ignore_index=True, sort=False)

            # Fill NaN values with empty strings
            combined_df = combined_df.fillna('')

            # Process "一日" bookings - split into 午前, 午後, 夜間
            processed_rows = []
            config = load_config()
            csv_column_mapping = config.get('csv_column_mapping', {}) if config else {}
            datetime_col = csv_column_mapping.get('booking_datetime', '利用日時(予約内容)')

            for index, row in combined_df.iterrows():
                datetime_value = str(row.get(datetime_col, ''))
                if '一日' in datetime_value:
                    # Split "一日" into three time slots
                    base_datetime = datetime_value.replace('一日', '')
                    for time_slot in ['午前', '午後', '夜間']:
                        new_row = row.copy()
                        new_row[datetime_col] = base_datetime + time_slot
                        processed_rows.append(new_row)
                else:
                    processed_rows.append(row)

            # Create new dataframe with processed rows
            if processed_rows:
                combined_df = pd.DataFrame(processed_rows)

            # Save combined data
            combined_df.to_csv(BOOKINGS_CSV, index=False, encoding='utf-8-sig')
            logging.info(f"Combined CSV saved: {len(combined_df)} total rows")

            # Move processed files to processed folder
            processed_dir = os.path.join(BASE_DIR, 'processed')
            os.makedirs(processed_dir, exist_ok=True)

            for file_path in processed_files:
                try:
                    filename = os.path.basename(file_path)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    new_filename = f"{timestamp}_{filename}"
                    new_path = os.path.join(processed_dir, new_filename)

                    os.rename(file_path, new_path)
                    logging.info(f"Moved {filename} to processed folder as {new_filename}")
                except Exception as e:
                    logging.error(f"Error moving {file_path}: {e}")

            return True
        else:
            logging.warning("No CSV files could be processed")
            return False

    except Exception as e:
        logging.error(f"Error in process_csv_files: {e}")
        return False

class UploadHandler(FileSystemEventHandler):
    """ファイルアップロードを監視するハンドラー"""

    def __init__(self):
        self.last_processed = {}

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.csv'):
            # Avoid duplicate processing
            current_time = time.time()
            if event.src_path in self.last_processed:
                if current_time - self.last_processed[event.src_path] < 5:  # 5 second cooldown
                    return

            self.last_processed[event.src_path] = current_time
            logging.info(f"New CSV file detected: {os.path.basename(event.src_path)}")

            # Wait a moment for file to be completely written
            time.sleep(2)

            # Process CSV files
            if process_csv_files():
                logging.info("CSV processing completed successfully")
            else:
                logging.error("CSV processing failed")

def start_file_watcher():
    """ファイル監視を開始"""
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)

        event_handler = UploadHandler()
        observer = Observer()
        observer.schedule(event_handler, UPLOADS_DIR, recursive=False)
        observer.start()

        logging.info(f"File watcher started for: {UPLOADS_DIR}")
        return observer

    except Exception as e:
        logging.error(f"Error starting file watcher: {e}")
        return None

def fetch_from_csv():
    """CSVファイルからデータを取得"""
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

        # Fill NaN values with empty strings
        df = df.fillna('')
        bookings = df.to_dict('records')
        logging.info(f"Loaded {len(bookings)} bookings from CSV")
        return bookings

    except FileNotFoundError:
        logging.warning(f"Warning: {BOOKINGS_CSV} not found. No data to display.")
        return []
    except Exception as e:
        logging.error(f"Error loading CSV: {e}")
        return []

@app.route('/')
def serve_index():
    try:
        return send_from_directory(BASE_DIR, 'index.html')
    except FileNotFoundError:
        return "index.html not found", 404

@app.route('/api/config')
def get_config():
    try:
        config = load_config()
        if config is None:
            return jsonify({"error": "Failed to load config.json"}), 500
        return jsonify(config)
    except Exception as e:
        logging.error(f"Error in /api/config: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings')
def get_bookings():
    try:
        bookings = fetch_from_csv()
        logging.info(f"Returning {len(bookings)} bookings")
        return jsonify(bookings)
    except Exception as e:
        logging.error(f"Error in /api/bookings: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_files():
    """WebページからのCSVファイルアップロードを処理"""
    try:
        if 'files' not in request.files:
            return jsonify({
                "success": False,
                "message": "ファイルが選択されていません"
            }), 400

        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({
                "success": False,
                "message": "ファイルが選択されていません"
            }), 400

        # ファイル数制限チェック
        if len(files) > MAX_FILES_PER_REQUEST:
            logger.warning(f"Too many files uploaded: {len(files)}")
            return jsonify({
                "success": False,
                "message": f"ファイル数が多すぎます（最大{MAX_FILES_PER_REQUEST}ファイル）"
            }), 400

        uploaded_files = []
        failed_files = []

        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOADS_DIR, exist_ok=True)

        for file in files:
            if file and file.filename:
                # ファイル拡張子チェック
                if not allowed_file(file.filename):
                    failed_files.append(f"{file.filename}: CSVファイルのみ許可されています")
                    logger.warning(f"Invalid file type attempted: {file.filename}")
                    continue

                # ファイル名サニタイズ
                filename = sanitize_filename(file.filename)
                if not filename:
                    failed_files.append(f"{file.filename}: 無効なファイル名です")
                    continue

                # Check file size (16MB limit)
                file.seek(0, 2)  # Seek to end
                file_size = file.tell()
                file.seek(0)  # Reset to beginning

                if file_size > 16 * 1024 * 1024:  # 16MB
                    failed_files.append(f"{filename}: ファイルサイズが大きすぎます (16MB以下にしてください)")
                    continue

                # Save file to uploads directory
                file_path = os.path.join(UPLOADS_DIR, filename)

                # Handle filename conflicts
                counter = 1
                original_filename = filename
                while os.path.exists(file_path):
                    name, ext = os.path.splitext(original_filename)
                    filename = f"{name}_{counter}{ext}"
                    file_path = os.path.join(UPLOADS_DIR, filename)
                    counter += 1

                file.save(file_path)

                # CSVファイル内容検証
                is_valid, validation_message = validate_csv_content(file_path)
                if not is_valid:
                    os.remove(file_path)  # 無効なファイルを削除
                    failed_files.append(f"{filename}: {validation_message}")
                    logger.warning(f"CSV validation failed for {filename}: {validation_message}")
                    continue

                uploaded_files.append(filename)
                logger.info(f"File uploaded and validated: {filename} ({file_size} bytes)")

        # Process uploaded files immediately
        if uploaded_files:
            # Wait a moment for file to be saved properly
            time.sleep(0.5)

            # Trigger CSV processing
            if process_csv_files():
                processing_message = "CSVファイルが正常に処理されました"
            else:
                processing_message = "CSVファイルのアップロードは完了しましたが、処理中にエラーが発生しました"
        else:
            processing_message = "処理できるファイルがありませんでした"

        # Prepare response message
        if uploaded_files and not failed_files:
            message = f"{len(uploaded_files)}個のファイルが正常にアップロードされました。{processing_message}。"
        elif uploaded_files and failed_files:
            message = f"{len(uploaded_files)}個のファイルがアップロードされました。{processing_message}。{len(failed_files)}個のファイルでエラーが発生しました。"
        else:
            message = "アップロードできるファイルがありませんでした。"

        return jsonify({
            "success": len(uploaded_files) > 0,
            "message": message,
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "total_uploaded": len(uploaded_files),
            "total_failed": len(failed_files)
        })

    except Exception as e:
        logging.error(f"Error in file upload: {e}")
        return jsonify({
            "success": False,
            "message": f"アップロード中にエラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/status')
def server_status():
    """サーバーステータスを返す"""
    return jsonify({
        'status': 'running',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'uptime': time.time() - app.start_time if hasattr(app, 'start_time') else 0
    })


@app.route('/api/open-setup')
def open_easy_setup():
    """easy_setup.batを開く"""
    try:
        setup_path = os.path.join(BASE_DIR, 'easy_setup.bat')
        if os.path.exists(setup_path):
            # Windowsでbatファイルを実行する方法を複数試す
            try:
                # 方法1: subprocess.run
                subprocess.run([setup_path], shell=True, check=False)
                return jsonify({'success': True, 'message': 'easy_setup.batを起動しました'})
            except Exception as e1:
                try:
                    # 方法2: os.startfile
                    os.startfile(setup_path)
                    return jsonify({'success': True, 'message': 'easy_setup.batを起動しました'})
                except Exception as e2:
                    try:
                        # 方法3: os.system
                        os.system(f'start "" "{setup_path}"')
                        return jsonify({'success': True, 'message': 'easy_setup.batを起動しました'})
                    except Exception as e3:
                        return jsonify({'success': False, 'message': f'起動エラー - subprocess: {str(e1)}, startfile: {str(e2)}, system: {str(e3)}'})
        else:
            return jsonify({'success': False, 'message': 'easy_setup.batが見つかりません'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'エラー: {str(e)}'})

@app.route('/api/server-control', methods=['POST'])
def server_control():
    """サーバー制御（停止のみ実装）"""
    try:
        action = request.json.get('action')
        if action == 'stop':
            # Graceful shutdown
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
                return jsonify({'success': False, 'message': 'サーバーを停止できません'})
            func()
            return jsonify({'success': True, 'message': 'サーバーを停止しています...'})
        else:
            return jsonify({'success': False, 'message': '不明なアクション'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'エラー: {str(e)}'})

@app.route('/api/files-info')
def files_info():
    """ファイル情報を返す"""
    try:
        info = {
            'config_editor_exists': os.path.exists(os.path.join(BASE_DIR, 'config_editor.pyw')),
            'easy_setup_exists': os.path.exists(os.path.join(BASE_DIR, 'easy_setup.bat')),
            'config_exists': os.path.exists(os.path.join(BASE_DIR, 'config.json')),
            'bookings_csv_exists': os.path.exists(BOOKINGS_CSV),
            'uploads_count': len(glob.glob(os.path.join(UPLOADS_DIR, '*.csv'))),
            'processed_count': len(os.listdir(os.path.join(BASE_DIR, 'processed'))) if os.path.exists(os.path.join(BASE_DIR, 'processed')) else 0
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/test')
def test():
    return "Meeting Room System is working!"

def get_local_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def create_tray_icon():
    """システムトレイ用のアイコンを作成"""
    # Create a simple icon
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Draw a simple calendar icon
    draw.rectangle([10, 15, 54, 55], fill='lightblue', outline='blue', width=2)
    draw.rectangle([10, 15, 54, 25], fill='blue')
    draw.text((20, 30), "会議", fill='black')
    draw.text((20, 42), "室", fill='black')

    return image

def open_browser(icon, item):
    """ブラウザでアプリケーションを開く"""
    url = f"http://127.0.0.1:{server_port}"
    webbrowser.open(url)
    logging.info(f"Opened browser: {url}")

@app.route('/api/open-config')
def open_config_editor():
    """設定エディターを開く"""
    try:
        config_path = os.path.join(BASE_DIR, 'config_editor.pyw')
        if os.path.exists(config_path):
            # Windowsで.pywファイルを確実に起動する方法
            try:
                # 方法1: subprocess.Popen
                subprocess.Popen(['python', config_path])
                return jsonify({'success': True, 'message': 'カシカイ設定エディターを起動しました'})
            except Exception as e1:
                try:
                    # 方法2: os.startfile
                    os.startfile(config_path)
                    return jsonify({'success': True, 'message': 'カシカイ設定エディターを起動しました'})
                except Exception as e2:
                    try:
                        # 方法3: os.system
                        os.system(f'python "{config_path}"')
                        return jsonify({'success': True, 'message': 'カシカイ設定エディターを起動しました'})
                    except Exception as e3:
                        return jsonify({'success': False, 'message': f'起動エラー - subprocess: {str(e1)}, startfile: {str(e2)}, system: {str(e3)}'})
        else:
            return jsonify({'success': False, 'message': 'config_editor.pywが見つかりません'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'エラー: {str(e)}'})

def show_info(icon, item):
    """システム情報を表示"""
    import threading

    def show_dialog():
        import tkinter as tk
        from tkinter import messagebox

        host_ip = get_local_ip()
        info_text = f"""会議室予約システム

ローカルアクセス: http://127.0.0.1:{server_port}
ネットワークアクセス: http://{host_ip}:{server_port}

アップロードフォルダ: {UPLOADS_DIR}
データフォルダ: {DATA_DIR}
        """

        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.attributes('-topmost', True)  # Keep on top

        try:
            # Show info dialog
            messagebox.showinfo("システム情報", info_text)
        finally:
            # Clean up
            root.quit()
            root.destroy()

    # Run dialog in separate thread to avoid blocking
    thread = threading.Thread(target=show_dialog, daemon=True)
    thread.start()

    logging.info("System info displayed")

def open_config_editor_tray(icon, item):
    """タスクトレイから設定エディタを開く"""
    try:
        config_path = os.path.join(BASE_DIR, 'config_editor.pyw')
        if os.path.exists(config_path):
            try:
                subprocess.Popen(['python', config_path])
                logging.info("Config editor opened from tray")
            except Exception as e1:
                try:
                    os.startfile(config_path)
                    logging.info("Config editor opened from tray using startfile")
                except Exception as e2:
                    try:
                        os.system(f'python "{config_path}"')
                        logging.info("Config editor opened from tray using system")
                    except Exception as e3:
                        logging.error(f"Failed to open config editor: {e1}, {e2}, {e3}")
        else:
            logging.error("config_editor.pyw not found")
    except Exception as e:
        logging.error(f"Error opening config editor from tray: {e}")

def quit_application(icon, item):
    """アプリケーションを終了"""
    global observer
    logging.info("Shutting down application...")

    if observer:
        observer.stop()
        observer.join()
        logging.info("File watcher stopped")

    icon.stop()
    sys.exit(0)

def setup_system_tray():
    """システムトレイをセットアップ"""
    try:
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("ブラウザで開く", open_browser),
            pystray.MenuItem("設定エディタ", open_config_editor_tray),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("システム情報", show_info),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("終了", quit_application)
        )

        # Create icon
        icon = pystray.Icon(
            "meeting_room_system",
            create_tray_icon(),
            "会議室予約システム",
            menu
        )

        return icon
    except Exception as e:
        logging.error(f"Failed to setup system tray: {e}")
        return None

def find_available_port(start_port=5000, max_attempts=10):
    """利用可能なポート番号を探す"""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            continue

    # 利用可能なポートが見つからない場合
    logging.warning(f"No available port found between {start_port} and {start_port + max_attempts - 1}")
    return start_port

def run_server_with_tray():
    """サーバーをシステムトレイと一緒に実行"""
    global observer, server_port

    host_ip = get_local_ip()
    server_port = find_available_port(5000)  # 5000から利用可能なポートを自動選択

    print("--- Meeting Room System Starting ---")
    print(f"Access from this PC: http://127.0.0.1:{server_port}")
    print(f"Access from network: http://{host_ip}:{server_port}")
    print("-" * 40)

    # Test config loading
    config = load_config()
    if config is None:
        print("ERROR: Failed to load config.json")
        return
    print("[OK] Config loaded successfully")

    # Initialize directories
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    print("[OK] Directories initialized")

    # Process any existing CSV files in uploads
    if process_csv_files():
        print("[OK] Initial CSV processing completed")
    else:
        print("[INFO] No CSV files to process initially")

    # Start file watcher
    observer = start_file_watcher()
    if observer:
        print("[OK] File watcher started")
    else:
        print("[WARNING] File watcher failed to start")

    # Test CSV loading
    bookings = fetch_from_csv()
    print(f"[OK] CSV loaded: {len(bookings)} bookings")

    print("[OK] Starting Flask server...")
    print(f"[INFO] Upload CSV files to: {UPLOADS_DIR}")
    print(f"[INFO] Processed files moved to: {os.path.join(BASE_DIR, 'processed')}")

    # Start Flask server in a separate thread
    def run_flask():
        # Record server start time for uptime calculation
        app.start_time = time.time()
        app.run(host='0.0.0.0', port=server_port, debug=False, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    print("[OK] Flask server started in background")
    print("[OK] System tray icon created - Right-click for options")

    # Setup and run system tray
    icon = setup_system_tray()
    if icon:
        icon.run()  # This blocks until the application exits
    else:
        print("[ERROR] Failed to create system tray")
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            quit_application(None, None)

def run_server():
    host_ip = get_local_ip()
    port = find_available_port(5000)  # 5000から利用可能なポートを自動選択
    print("--- Meeting Room System Starting ---")
    print(f"Access from this PC: http://127.0.0.1:{port}")
    print(f"Access from network: http://{host_ip}:{port}")
    print("-" * 40)

    # Test config loading
    config = load_config()
    if config is None:
        print("ERROR: Failed to load config.json")
        return
    print("[OK] Config loaded successfully")

    # Initialize directories
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    print("[OK] Directories initialized")

    # Process any existing CSV files in uploads
    if process_csv_files():
        print("[OK] Initial CSV processing completed")
    else:
        print("[INFO] No CSV files to process initially")

    # Start file watcher
    observer = start_file_watcher()
    if observer:
        print("[OK] File watcher started")
    else:
        print("[WARNING] File watcher failed to start")

    # Test CSV loading
    bookings = fetch_from_csv()
    print(f"[OK] CSV loaded: {len(bookings)} bookings")

    print("[OK] Starting Flask server...")
    print(f"[INFO] Upload CSV files to: {UPLOADS_DIR}")
    print(f"[INFO] Processed files moved to: {os.path.join(BASE_DIR, 'processed')}")

    try:
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    finally:
        if observer:
            observer.stop()
            observer.join()
            print("[OK] File watcher stopped")

if __name__ == '__main__':
    # Use system tray version by default
    # Use run_server() for console-only mode
    run_server_with_tray()