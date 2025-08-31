import time
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

# --- 設定項目 ---
# Google Cloudの認証情報ファイル
CREDENTIALS_FILE = 'credentials.json'
# Googleスプレッドシートのシート名
SPREADSHEET_NAME = 'kasikai予約台帳' # ここは実際に作成したシート名に合わせる
# Google Drive for Desktopで同期しているローカルパス
# このパスはホストPCの環境に合わせて設定する必要がある
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # スクリプトのある場所を基準とする
INPUT_DIR = os.path.join(BASE_DIR, '申し込みデータ')
PROCESSED_DIR = os.path.join(BASE_DIR, '処理済み')

# スコープの設定
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# --- グローバル変数 ---
upload_timer = None
UPLOAD_DELAY = 60 # アップロードまでの待機時間（秒）

# --- メイン処理 ---
def process_files():
    """CSVファイルを処理してスプレッドシートにアップロードするメイン関数"""
    print(f'{time.ctime()}: 処理を開始します。', flush=True)
    
    try:
        # 古い処理済みファイルをクリーンアップ
        print("古い処理済みファイルをクリーンアップします...", flush=True)
        if os.path.exists(PROCESSED_DIR):
            for filename in os.listdir(PROCESSED_DIR):
                file_path = os.path.join(PROCESSED_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'ファイル削除中にエラーが発生しました: {file_path} - {e}', flush=True)
        print("クリーンアップが完了しました。", flush=True)

        # 認証
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # スプレッドシートとワークシートを開く
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.sheet1

        # 入力フォルダ内のCSVを全て読み込んで結合
        # 処理中にファイルが移動される可能性があるため、先にファイルリストを取得
        csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
        if not csv_files:
            print('処理対象のCSVファイルがありません。', flush=True)
            return

        all_data = pd.DataFrame()
        processed_file_paths = []
        for file in csv_files:
            file_path = os.path.join(INPUT_DIR, file)
            try:
                df = pd.read_csv(file_path, encoding='cp932')
                # O列「取消日(予約内容)」が空欄のデータ（キャンセルされていない予約）のみを抽出
                import time
import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

# app.pyからID生成ロジックをインポート
from app import parse_booking_data

# --- 設定項目 ---
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_NAME = 'kasikai予約台帳'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, '申し込みデータ')
PROCESSED_DIR = os.path.join(BASE_DIR, '処理済み')
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# --- グローバル変数 ---
upload_timer = None
UPLOAD_DELAY = 60

def process_files():
    """CSVファイルを処理してスプレッドシートにアップロードするメイン関数"""
    print(f'{time.ctime()}: 処理を開始します。', flush=True)
    
    try:
        # 1. 古い処理済みファイルをクリーンアップ
        print("古い処理済みファイルをクリーンアップします...", flush=True)
        if os.path.exists(PROCESSED_DIR):
            for filename in os.listdir(PROCESSED_DIR):
                file_path = os.path.join(PROCESSED_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'ファイル削除中にエラーが発生しました: {file_path} - {e}', flush=True)
        print("クリーンアップが完了しました。", flush=True)

        # 2. 入力フォルダ内のCSVを全て読み込んで結合
        csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
        if not csv_files:
            print('処理対象のCSVファイルがありません。', flush=True)
            return

        all_data_raw = pd.DataFrame()
        processed_file_paths = []
        for file in csv_files:
            file_path = os.path.join(INPUT_DIR, file)
            try:
                df = pd.read_csv(file_path, encoding='cp932')
                all_data_raw = pd.concat([all_data_raw, df], ignore_index=True)
                processed_file_paths.append(file_path)
            except Exception as e:
                print(f'ファイル読み込みエラー: {file_path} - {e}', flush=True)
                continue
        
        if all_data_raw.empty:
            print('読み込むデータがありませんでした。', flush=True)
            return

        # 3. キャンセル済み予約を除外
        print("キャンセル済み予約を除外しています...", flush=True)
        if '取消日(予約内容)' in all_data_raw.columns:
            valid_data_df = all_data_raw[all_data_raw['取消日(予約内容)'].isnull()].copy()
        else:
            valid_data_df = all_data_raw.copy()

        # 4. IDを付与し、重複を排除（同じIDなら後から読み込んだデータで上書き）
        print("予約の重複を排除しています...", flush=True)
        bookings_with_ids = parse_booking_data(valid_data_df)
        unique_bookings_map = {}
        for booking in bookings_with_ids:
            unique_bookings_map[booking['id']] = booking
        
        final_bookings = list(unique_bookings_map.values())
        print(f"重複排除後、ユニークな予約が {len(final_bookings)}件見つかりました。", flush=True)

        if not final_bookings:
            print("書き込むデータがありません。", flush=True)
            # 処理済みファイルは移動させる
            if not os.path.exists(PROCESSED_DIR):
                os.makedirs(PROCESSED_DIR)
            for path in processed_file_paths:
                file_name = os.path.basename(path)
                dst = os.path.join(PROCESSED_DIR, file_name)
                os.rename(path, dst)
            print(f'{len(processed_file_paths)}個のCSVファイルを処理済みフォルダに移動しました。', flush=True)
            return

        # 5. スプレッドシートに書き込むためにデータを整形
        final_df = pd.DataFrame(final_bookings)
        # スプレッドシートに不要なヘルパー列を削除
        columns_to_drop = ['id', 'roomId', 'date', 'slot', 'isSpecial']
        existing_columns_to_drop = [col for col in columns_to_drop if col in final_df.columns]
        final_df = final_df.drop(columns=existing_columns_to_drop)
        final_df = final_df.fillna('')
        
        # 6. スプレッドシートを更新
        print("スプレッドシートを更新しています...", flush=True)
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open(SPREADSHEET_NAME)
        worksheet = spreadsheet.sheet1
        
        worksheet.clear()
        worksheet.update([final_df.columns.values.tolist()] + final_df.values.tolist(), value_input_option='USER_ENTERED')
        print(f'{len(final_df)}行のデータをスプレッドシートに書き込みました。', flush=True)

        # 7. 処理済みファイルを移動
        if not os.path.exists(PROCESSED_DIR):
            os.makedirs(PROCESSED_DIR)
        for path in processed_file_paths:
            file_name = os.path.basename(path)
            dst = os.path.join(PROCESSED_DIR, file_name)
            os.rename(path, dst)
        print(f'{len(processed_file_paths)}個のCSVファイルを処理済みフォルダに移動しました。', flush=True)

    except Exception as e:
        print(f'エラーが発生しました: {e}', flush=True)
    finally:
        print(f'{time.ctime()}: 処理を終了します。', flush=True)


class DebounceEventHandler(FileSystemEventHandler):
    """
    ファイル変更を検知し、一定時間変更がなければ処理を実行するハンドラ
    """
    def on_any_event(self, event):
        if event.is_directory or not event.src_path.endswith('.csv'):
            return

        global upload_timer
        if upload_timer and upload_timer.is_alive():
            upload_timer.cancel()
        
        print(f"{time.ctime()}: ファイル変更を検知。タイマーをリセットします。", flush=True)
        upload_timer = threading.Timer(UPLOAD_DELAY, process_files)
        upload_timer.start()
        print(f"{time.ctime()}: {UPLOAD_DELAY}秒後にアップロード処理をスケジュールしました。", flush=True)

def start_file_watcher():
    # 必要なフォルダが存在するか確認・作成
    for directory in [INPUT_DIR, PROCESSED_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f'フォルダを作成しました: {directory}', flush=True)

    print(f'{time.ctime()}: 監視を開始します。監視対象: {INPUT_DIR}', flush=True)
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
                all_data = pd.concat([all_data, df], ignore_index=True)
                processed_file_paths.append(file_path)
            except Exception as e:
                print(f'ファイル読み込みエラー: {file_path} - {e}', flush=True)
                continue
        
        if all_data.empty:
            print('読み込むデータがありませんでした。', flush=True)
            return

        # スプレッドシートをクリア
        worksheet.clear()
        
        # NaN値を空文字列に変換
        all_data = all_data.fillna('')
        
        # ヘッダーを書き込み
        worksheet.update([all_data.columns.values.tolist()] + all_data.values.tolist())
        print(f'{len(all_data)}行のデータをスプレッドシートに書き込みました。', flush=True)

        # 処理済みファイルを移動
        if not os.path.exists(PROCESSED_DIR):
            os.makedirs(PROCESSED_DIR)
            
        for path in processed_file_paths:
            file_name = os.path.basename(path)
            dst = os.path.join(PROCESSED_DIR, file_name)
            os.rename(path, dst)
        print(f'{len(processed_file_paths)}個のCSVファイルを処理済みフォルダに移動しました。', flush=True)

    except Exception as e:
        print(f'エラーが発生しました: {e}', flush=True)
    finally:
        print(f'{time.ctime()}: 処理を終了します。', flush=True)


class DebounceEventHandler(FileSystemEventHandler):
    """
    ファイル変更を検知し、一定時間変更がなければ処理を実行するハンドラ
    """
    def on_any_event(self, event):
        if event.is_directory or not event.src_path.endswith('.csv'):
            return

        global upload_timer
        if upload_timer and upload_timer.is_alive():
            upload_timer.cancel()
        
        print(f"{time.ctime()}: ファイル変更を検知。タイマーをリセットします。", flush=True)
        upload_timer = threading.Timer(UPLOAD_DELAY, process_files)
        upload_timer.start()
        print(f"{time.ctime()}: {UPLOAD_DELAY}秒後にアップロード処理をスケジュールしました。", flush=True)


def start_file_watcher():
    # 必要なフォルダが存在するか確認・作成
    for directory in [INPUT_DIR, PROCESSED_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f'フォルダを作成しました: {directory}', flush=True)

    print(f'{time.ctime()}: 監視を開始します。監視対象: {INPUT_DIR}', flush=True)
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
