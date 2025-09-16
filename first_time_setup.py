#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会議室予約システム - 初回設定ツール
ITに詳しくない方でも簡単に設定できるGUIツール
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import webbrowser

class FirstTimeSetup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 会議室予約システム - 初回設定")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 設定データ
        self.rooms = []
        self.csv_file_path = ""

        self.setup_ui()

    def setup_ui(self):
        """UIセットアップ"""

        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # タイトル
        title_label = ttk.Label(main_frame, text="🚀 会議室予約システム初回設定",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 説明
        desc_label = ttk.Label(main_frame,
                              text="簡単な設定でシステムを開始できます！\n以下の手順に従って設定してください。",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # ステップ1: 会議室設定
        step1_frame = ttk.LabelFrame(main_frame, text="ステップ1: 会議室を設定", padding="10")
        step1_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        ttk.Label(step1_frame, text="あなたの組織の会議室名を入力してください：").grid(row=0, column=0, columnspan=2, sticky="w")

        # 会議室追加フレーム
        room_frame = ttk.Frame(step1_frame)
        room_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(room_frame, text="会議室名:").grid(row=0, column=0, sticky="w")
        self.room_entry = ttk.Entry(room_frame, width=30)
        self.room_entry.grid(row=0, column=1, padx=(10, 5))

        ttk.Button(room_frame, text="追加", command=self.add_room).grid(row=0, column=2, padx=5)

        # 会議室リスト
        self.room_listbox = tk.Listbox(step1_frame, height=6)
        self.room_listbox.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        # 削除ボタン
        ttk.Button(step1_frame, text="選択した会議室を削除",
                  command=self.remove_room).grid(row=3, column=0, columnspan=2, pady=5)

        # サンプル追加ボタン
        sample_frame = ttk.Frame(step1_frame)
        sample_frame.grid(row=4, column=0, columnspan=2, pady=5)

        ttk.Button(sample_frame, text="📋 基本4部屋セット",
                  command=self.add_basic_rooms).grid(row=0, column=0, padx=5)
        ttk.Button(sample_frame, text="🏛️ ホール+会議室セット",
                  command=self.add_hall_rooms).grid(row=0, column=1, padx=5)

        # ステップ2: CSV設定（オプション）
        step2_frame = ttk.LabelFrame(main_frame, text="ステップ2: CSVファイル設定 (オプション)", padding="10")
        step2_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        ttk.Label(step2_frame, text="既存のCSVファイルがある場合は選択してください：").grid(row=0, column=0, columnspan=2, sticky="w")

        csv_frame = ttk.Frame(step2_frame)
        csv_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        self.csv_path_var = tk.StringVar(value="まだファイルが選択されていません")
        ttk.Label(csv_frame, textvariable=self.csv_path_var, width=50).grid(row=0, column=0, sticky="w")
        ttk.Button(csv_frame, text="ファイル選択", command=self.select_csv_file).grid(row=0, column=1, padx=(10, 0))

        # 完了ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="🚀 設定完了・システム開始",
                  command=self.complete_setup, style="Accent.TButton").grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="💾 設定のみ保存",
                  command=self.save_only).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="❌ キャンセル",
                  command=self.root.quit).grid(row=0, column=2, padx=10)

        # 初期データの読み込み
        self.load_existing_config()

    def add_room(self):
        """会議室を追加"""
        room_name = self.room_entry.get().strip()
        if room_name:
            if room_name not in [room['display_name'] for room in self.rooms]:
                room_id = room_name.lower().replace(' ', '-').replace('　', '-')
                self.rooms.append({
                    "csv_name": room_name,
                    "id": room_id,
                    "display_name": room_name
                })
                self.room_listbox.insert(tk.END, room_name)
                self.room_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("重複", "この会議室は既に追加されています。")
        else:
            messagebox.showwarning("入力エラー", "会議室名を入力してください。")

    def remove_room(self):
        """選択した会議室を削除"""
        selection = self.room_listbox.curselection()
        if selection:
            index = selection[0]
            self.room_listbox.delete(index)
            del self.rooms[index]
        else:
            messagebox.showwarning("選択エラー", "削除する会議室を選択してください。")

    def add_basic_rooms(self):
        """基本4部屋セットを追加"""
        basic_rooms = ["大会議室", "中会議室", "小会議室A", "小会議室B"]
        for room in basic_rooms:
            if room not in [r['display_name'] for r in self.rooms]:
                self.room_entry.delete(0, tk.END)
                self.room_entry.insert(0, room)
                self.add_room()

    def add_hall_rooms(self):
        """ホール+会議室セットを追加"""
        hall_rooms = ["メインホール", "ホール前半", "ホール後半", "会議室A", "会議室B"]
        for room in hall_rooms:
            if room not in [r['display_name'] for r in self.rooms]:
                self.room_entry.delete(0, tk.END)
                self.room_entry.insert(0, room)
                self.add_room()

    def select_csv_file(self):
        """CSVファイルを選択"""
        file_path = filedialog.askopenfilename(
            title="CSVファイルを選択",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.csv_file_path = file_path
            self.csv_path_var.set(f"選択済み: {os.path.basename(file_path)}")

    def load_existing_config(self):
        """既存の設定を読み込み"""
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.rooms = config.get('rooms', [])
                    for room in self.rooms:
                        self.room_listbox.insert(tk.END, room['display_name'])
            except Exception as e:
                print(f"設定読み込みエラー: {e}")

    def save_config(self):
        """設定を保存"""
        if not self.rooms:
            messagebox.showerror("エラー", "最低1つの会議室を設定してください。")
            return False

        config = {
            "rooms": self.rooms,
            "internal_room_ids": [],
            "csv_column_mapping": {
                "booking_datetime": "利用日時(予約内容)",
                "room_name": "会議室(予約内容)",
                "display_name": "案内表示名(予約内容)",
                "company_name": "事業所名",
                "contact_person": "担当者名",
                "total_amount": "合計金額(予約内容)",
                "equipment": "備品(予約内容)"
            },
            "modal_fields": {
                "利用日時(予約内容)": "利用日時(予約内容)",
                "会議室(予約内容)": "会議室(予約内容)",
                "案内表示名(予約内容)": "案内表示名(予約内容)",
                "事業所名": "事業所名",
                "担当者名": "担当者名",
                "備品(予約内容)": "備品(予約内容)",
                "延長(予約内容)": "延長(予約内容)",
                "会員種別(予約内容)": "会員種別(予約内容)",
                "メモ": "メモ",
                "都道府県": "都道府県",
                "市区町村": "市区町村"
            },
            "data_split_rules": [],
            "hidden_room_ids": []
        }

        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました：{e}")
            return False

    def save_only(self):
        """設定のみ保存"""
        if self.save_config():
            messagebox.showinfo("完了", "設定を保存しました。\nシステムを開始するには start_server.bat をダブルクリックしてください。")
            self.root.quit()

    def complete_setup(self):
        """設定完了・システム開始"""
        if self.save_config():
            messagebox.showinfo("完了", "設定が完了しました！\nシステムを開始します。")
            self.root.quit()

            # システム開始
            try:
                import subprocess
                subprocess.Popen(['python', 'app.py'])

                # ブラウザを開く
                import time
                time.sleep(2)
                webbrowser.open('http://localhost:5000')

            except Exception as e:
                messagebox.showerror("エラー", f"システムの開始に失敗しました：{e}")

def main():
    app = FirstTimeSetup()
    app.root.mainloop()

if __name__ == "__main__":
    main()