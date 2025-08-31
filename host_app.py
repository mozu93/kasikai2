import os
import sys
import threading
from PIL import Image, ImageDraw
from pystray import MenuItem as item, Icon as icon

# --- 相対パスでモジュールをインポートするための設定 ---
# このスクリプトのあるディレクトリをモジュール検索パスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import run_web_server
    from upload_script import start_file_watcher
except ImportError as e:
    # エラーログをファイルに出力
    with open("host_app_error.log", "w", encoding="utf-8") as f:
        f.write(f"必要なモジュールのインポートに失敗しました: {e}\n")
        f.write("app.py または upload_script.py が見つからないか、内部でエラーが発生しています。\n")
    sys.exit(1)


# --- グローバル変数 ---
web_server_thread = None
file_watcher_thread = None
main_icon = None

def create_image(width, height, color1, color2):
    """アイコン用の画像を生成する"""
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image

def exit_action(icon, item):
    """終了処理"""
    print("アプリケーションを終了します...")
    icon.stop()
    os._exit(0)

def run_services_in_threads():
    """各サービスを別々のスレッドで起動する"""
    global web_server_thread, file_watcher_thread

    print("Webサーバーをスレッドで起動します。")
    web_server_thread = threading.Thread(target=run_web_server, daemon=True)
    web_server_thread.start()

    print("ファイル監視をスレッドで起動します。")
    file_watcher_thread = threading.Thread(target=start_file_watcher, daemon=True)
    file_watcher_thread.start()

def main():
    """メイン関数"""
    global main_icon
    
    menu = (item('終了', exit_action),)
    image = create_image(64, 64, 'darkblue', 'skyblue')
    main_icon = icon('kasikai_host', image, "会議室予約システム ホスト", menu)

    run_services_in_threads()
    
    print("システムトレイアイコンを起動します。")
    main_icon.run()

if __name__ == "__main__":
    main()
