import pandas as pd
import os
import glob
from datetime import datetime

# 申し込みデータが保存されているフォルダを指定
DATA_FOLDER = '申し込みデータ'

def find_todays_booking_files():
    """
    指定されたフォルダ内で、本日更新された「申し込みデータ」を含む
    すべてのCSVファイルのパスのリストを返す。
    """
    today = datetime.now().date()
    todays_files = []
    # DATA_FOLDER内のCSVファイルを検索
    search_pattern = os.path.join(DATA_FOLDER, '*申し込みデータ*.csv')
    
    files = [f for f in glob.glob(search_pattern) if not os.path.basename(f).startswith('~$')]

    for file_path in files:
        modification_time = os.path.getmtime(file_path)
        modification_date = datetime.fromtimestamp(modification_time).date()
        
        if modification_date == today:
            todays_files.append(file_path)
            
    return todays_files

def create_bookings_csv(file_paths, output_csv_path):
    """
    指定されたCSVファイルのリストを読み込み、それらを結合して単一のCSVファイルに変換する。
    """
    if not file_paths:
        print(f"本日更新された '{DATA_FOLDER}' 内の「申し込みデータ」を含むCSVファイルが見つかりませんでした。")
        return

    print(f"本日更新された '{DATA_FOLDER}' 内の以下のファイルを結合して {os.path.basename(output_csv_path)} を作成します:")
    file_paths.sort(key=os.path.getmtime)
    for path in file_paths:
        print(f" - {os.path.basename(path)}")

    df_list = []
    for path in file_paths:
        try:
            # CSVファイルを読み込む (エンコーディングをcp932に変更)
            df = pd.read_csv(path, encoding='cp932')
            # ヘッダーの空白と制御文字を削除
            df.columns = df.columns.str.strip()
            df_list.append(df)
        except Exception as e:
            print(f"エラー: {path} の読み込み中に問題が発生しました: {e}")
            return

    if not df_list:
        print("エラー: 読み込み可能なデータがありませんでした。")
        return

    try:
        combined_df = pd.concat(df_list, ignore_index=True)
        combined_df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"\n変換成功: {output_csv_path} を作成しました。")
    except Exception as e:
        print(f"CSVファイルへの書き込み中にエラーが発生しました: {e}")

if __name__ == '__main__':
    if not os.path.exists(DATA_FOLDER):
        print(f"エラー: '{DATA_FOLDER}' フォルダが見つかりません。作成してください。")
    else:
        todays_files = find_todays_booking_files()
        create_bookings_csv(todays_files, 'bookings.csv')