import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, font
import tkinter.ttk as ttk
import json
import os
import pandas as pd

CONFIG_FILE = 'config.json'

class ConfigEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("🌈 カシカイ 設定エディター")
        
        # Set modern window size and style
        master.geometry("950x750")
        master.minsize(700, 500)
        master.configure(bg='#f8f9fa')
        
        # Modern fonts
        self.title_font = font.Font(family='Segoe UI', size=16, weight='bold')
        self.heading_font = font.Font(family='Segoe UI', size=12, weight='bold')
        self.body_font = font.Font(family='Segoe UI', size=10)
        
        # Set default font for better Japanese support
        try:
            self.default_font = font.nametofont("TkDefaultFont")
            self.default_font.configure(family="Yu Gothic UI", size=10)
            master.option_add("*Font", self.default_font)
        except:
            pass

        self.config = self.load_config()

        # Header with gradient-like effect
        header_frame = tk.Frame(master, bg='#007bff', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🌈 カシカイ 設定エディター", 
                              font=('Yu Gothic UI', 18, 'bold'), bg='#007bff', fg='white')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(header_frame, text="会議室予約システム設定", 
                                 font=('Yu Gothic UI', 10), bg='#007bff', fg='#cce5ff')
        subtitle_label.pack()

        # Create modern notebook with styled tabs
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Modern.TNotebook', background='#f8f9fa', borderwidth=0)
        # 選択時は大きく、非選択時は小さく
        style.configure('Modern.TNotebook.Tab', padding=[20, 8], font=('Yu Gothic UI', 10))
        style.map('Modern.TNotebook.Tab', 
                 background=[('selected', '#007bff'), ('!selected', '#e9ecef')],
                 foreground=[('selected', 'white'), ('!selected', '#495057')],
                 padding=[('selected', [20, 15]), ('!selected', [20, 8])],
                 font=[('selected', ('Yu Gothic UI', 11, 'bold')), ('!selected', ('Yu Gothic UI', 10))])

        # Notebook for tabs
        self.notebook = ttk.Notebook(master, style='Modern.TNotebook')
        self.notebook.pack(pady=15, padx=15, expand=True, fill='both')

        # Create modern tab frames
        self.data_split_tab_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.rooms_tab_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        self.modal_fields_tab_frame = tk.Frame(self.notebook, bg='#f8f9fa')
        
        # 会議室分割表示設定を一番左に配置
        self.notebook.add(self.rooms_tab_frame, text="🏢 会議室表示設定")
        self.notebook.add(self.data_split_tab_frame, text="🔄 会議室分割表示設定")
        self.notebook.add(self.modal_fields_tab_frame, text="📋 ポップアップ表示項目")

        # Setup scrollable frames for each tab
        self.setup_scrollable_frame(self.data_split_tab_frame, 'data_split')
        self.setup_scrollable_frame(self.rooms_tab_frame, 'rooms')
        self.setup_scrollable_frame(self.modal_fields_tab_frame, 'modal_fields')

        # Enable mouse wheel scrolling
        self.bind_mousewheel_to_canvas(self.data_split_canvas)
        self.bind_mousewheel_to_canvas(self.rooms_canvas)
        self.bind_mousewheel_to_canvas(self.modal_fields_canvas)

        # Setup tabs (rooms_tabを先に初期化してroom_entriesを作成)
        self.setup_rooms_tab()
        self.setup_modal_fields_tab()
        self.setup_data_split_tab()

        # Modern button frame
        button_frame = tk.Frame(master, bg='#f8f9fa')
        button_frame.pack(pady=20)

        # CSV読み込みボタン
        self.load_csv_button = tk.Button(button_frame, text="📊 会議室項目設定のためCSV読み込み", command=self.load_csv_config,
                                        font=('Yu Gothic UI', 11, 'bold'), bg='#4CAF50', fg='white',
                                        relief='flat', bd=0, padx=25, pady=12, cursor='hand2')
        self.load_csv_button.pack(side='left', padx=(0, 10))

        # ポップアップ項目のみCSV更新ボタン
        self.load_popup_only_button = tk.Button(button_frame, text="📋 ポップアップ項目設定のためCSV読み込み", command=self.load_csv_popup_fields_only,
                                               font=('Yu Gothic UI', 11, 'bold'), bg='#6f42c1', fg='white',
                                               relief='flat', bd=0, padx=25, pady=12, cursor='hand2')
        self.load_popup_only_button.pack(side='left', padx=(0, 10))

        self.save_button = tk.Button(button_frame, text="💾 設定を保存", command=self.save_config,
                                    font=('Yu Gothic UI', 12, 'bold'), bg='#28a745', fg='white',
                                    relief='flat', bd=0, padx=40, pady=12, cursor='hand2')
        self.save_button.pack(side='left')
        
        # Hover effects for buttons
        def on_enter_csv(e):
            self.load_csv_button.config(bg='#0056b3')
        def on_leave_csv(e):
            self.load_csv_button.config(bg='#007bff')
        def on_enter_popup(e):
            self.load_popup_only_button.config(bg='#5a32a3')
        def on_leave_popup(e):
            self.load_popup_only_button.config(bg='#6f42c1')
        def on_enter_save(e):
            self.save_button.config(bg='#218838')
        def on_leave_save(e):
            self.save_button.config(bg='#28a745')

        self.load_csv_button.bind('<Enter>', on_enter_csv)
        self.load_csv_button.bind('<Leave>', on_leave_csv)
        self.load_popup_only_button.bind('<Enter>', on_enter_popup)
        self.load_popup_only_button.bind('<Leave>', on_leave_popup)
        self.save_button.bind('<Enter>', on_enter_save)
        self.save_button.bind('<Leave>', on_leave_save)
    
    def get_processed_bookings_headers(self):
        """processed_bookings.csvのヘッダーを取得"""
        csv_path = os.path.join('data', 'processed_bookings.csv')
        if not os.path.exists(csv_path):
            # フォールバック：デフォルトヘッダーを返す
            return [
                '申込NO', '申込日', 'booking_datetime', 'room_name', 'company_name', 
                '支払種別', '支払額合計', '入金日(予約内容)', 'extension', 'equipment', 
                'purpose', 'display_name', 'member_type', 'total_amount', 'cancellation_date',
                '会議室料金', '備品料金', '延長料金', '冷房料金', '暖房料金', '調整金', 
                '消費税', '合計料金', 'キャンセル料', 'コンビニ種別', 'クレジット種別',
                '未払い合計料金', '支払い済み合計料金', '受付承認', '最終更新日', '入金日',
                '取消日', '取消申請', '確定日', 'memo', '顧客NO', '事業所名カナ',
                'department_name', 'contact_person', 'メール', '会員種別', '会員番号',
                'zip_code', 'prefecture', 'city', 'address_rest', 'phone_number',
                'FAX番号', '案内板に表示する時間を入力してください。　例）13：30～', 'notes',
                '請求書等の宛名を変更したい場合は、こちらにご入力ください。', '自由設定項目4', '自由設定項目5'
            ]
        
        # 複数エンコーディングでCSVヘッダーを読み込み
        encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis', 'iso-2022-jp']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding, nrows=0)
                return df.columns.tolist()
            except Exception:
                continue
        
        # 全て失敗した場合はデフォルトを返す
        return ['booking_datetime', 'room_name', 'company_name', 'display_name', 'notes']

    def setup_scrollable_frame(self, parent, name):
        """Setup scrollable frame for a tab"""
        canvas = tk.Canvas(parent, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store references
        setattr(self, f'{name}_canvas', canvas)
        setattr(self, f'{name}_scrollbar', scrollbar)
        setattr(self, f'{name}_frame', scrollable_frame)

    def bind_mousewheel_to_canvas(self, canvas):
        """Bind mouse wheel scrolling to canvas"""
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("エラー", f"設定ファイルの読み込み中にエラーが発生しました: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()

    def get_default_config(self):
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
            # ✨ 順序付きリスト形式（新形式）
            "modal_fields_list": [
                {"display_name": "利用日時", "csv_field": "booking_datetime"},
                {"display_name": "会議室", "csv_field": "room_name"},
                {"display_name": "案内表示名", "csv_field": "display_name"},
                {"display_name": "事業所名", "csv_field": "company_name"},
                {"display_name": "担当者名", "csv_field": "contact_person"},
                {"display_name": "延長", "csv_field": "extension"},
                {"display_name": "備品", "csv_field": "equipment"}
            ],
            # 後方互換性のため、従来の辞書形式も保持
            "modal_fields": {
                "利用日時": "booking_datetime",
                "会議室": "room_name",
                "案内表示名": "display_name",
                "事業所名": "company_name",
                "担当者名": "contact_person",
                "延長": "extension",
                "備品": "equipment"
            },
            "data_split_rules": [
                {
                    "source_room_id": "hall-combined",
                    "target_room_ids": ["hall-1", "hall-2"],
                    "enabled": True,
                    "description": "ホール全の予約をホールⅠとホールⅡにコピー"
                }
            ],
            "hidden_room_ids": ["hall-combined"]
        }

    def save_config(self):
        try:
            # Update config from GUI elements
            self.config['rooms'] = []
            for i, entry_vars in enumerate(self.room_entries):
                csv_name = entry_vars['csv_name'].get()
                display_name = entry_vars['display_name'].get()

                if csv_name and display_name:
                    room_id = entry_vars['id'].get() if entry_vars['id'].get() else f"room-{i+1}"
                    self.config['rooms'].append({
                        "csv_name": csv_name,
                        "id": room_id,
                        "display_name": display_name
                    })

                    is_hidden = entry_vars['is_hidden'].get()
                    if is_hidden:
                        if room_id not in self.config.setdefault('hidden_room_ids', []):
                            self.config['hidden_room_ids'].append(room_id)
                    else:
                        if room_id in self.config.get('hidden_room_ids', []):
                            self.config['hidden_room_ids'].remove(room_id)

            # ✨ Save modal fields in order - UI上の順番を正確に保存
            # modal_fields_listとして順序付きリストで保存
            modal_fields_list = []
            disabled_fields = {}

            for entry_vars in self.modal_field_entries:
                display_name = entry_vars['display_name'].get()
                csv_field = entry_vars['csv_field'].get()
                enabled = entry_vars['enabled'].get()

                if display_name and csv_field:
                    if enabled:
                        # 有効な項目は順序付きリストに追加
                        modal_fields_list.append({
                            "display_name": display_name,
                            "csv_field": csv_field
                        })
                    else:
                        # 無効化された項目は別途保存
                        disabled_fields[display_name] = csv_field

            # 順序を保持するため、configに両方の形式で保存
            # 後方互換性のため従来の辞書形式も保持
            self.config['modal_fields_list'] = modal_fields_list
            self.config['modal_fields'] = {item['display_name']: item['csv_field'] for item in modal_fields_list}

            if disabled_fields:
                self.config['disabled_modal_fields'] = disabled_fields

            # Save data split rules
            self.config['data_split_rules'] = []
            for rule_vars in self.data_split_entries:
                if rule_vars['enabled'].get():
                    source_room_name = rule_vars['source_room'].get()
                    # Convert display name back to room_id
                    source_room_id = rule_vars['room_id_map'].get(source_room_name, '')
                    target_room_ids = [room_id for room_id, var in rule_vars['target_rooms'].items() if var.get()]
                    description = rule_vars['description'].get()
                    
                    if source_room_name != "-- 選択 --" and source_room_id and target_room_ids and description:
                        self.config['data_split_rules'].append({
                            "source_room_id": source_room_id,
                            "target_room_ids": target_room_ids,
                            "enabled": True,
                            "description": description
                        })

            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("✅ 保存完了", "設定が正常に保存されました。\nアプリケーションを再起動すると反映されます。")
        except Exception as e:
            messagebox.showerror("❌ エラー", f"設定の保存中にエラーが発生しました:\n{e}")

    def load_csv_config(self):
        """CSVファイルから設定を読み込む"""
        try:
            file_path = filedialog.askopenfilename(
                title="カシカイ予約一覧CSVファイルを選択",
                filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")],
                initialdir=os.getcwd()
            )

            if not file_path:
                return

            # CSVファイルを読み込む
            self.process_csv_file(file_path)

        except Exception as e:
            messagebox.showerror("❌ エラー", f"CSVファイルの読み込み中にエラーが発生しました:\n{e}")

    def process_csv_file(self, file_path):
        """CSVファイルを処理して設定に反映"""
        try:
            # 複数エンコーディングでCSVを読み込み
            encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis', 'iso-2022-jp']
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except Exception:
                    continue

            if df is None:
                messagebox.showerror("❌ エラー", "CSVファイルを読み込めませんでした。エンコーディングを確認してください。")
                return

            # 確認ダイアログ
            result = messagebox.askyesno(
                "📥 CSV読み込み確認",
                f"CSVファイル: {os.path.basename(file_path)}\n"
                f"行数: {len(df)}行\n"
                f"列数: {len(df.columns)}列\n\n"
                "このCSVファイルから設定を更新しますか？\n"
                "(現在の設定は上書きされます)"
            )

            if not result:
                return

            # CSVデータから設定を更新
            self.update_config_from_csv(df)

            messagebox.showinfo(
                "✅ 読み込み完了",
                f"CSVファイルから会議室情報を読み込みました。\n"
                f"会議室: {len(self.config.get('rooms', []))}件\n\n"
                "✨ 詳細分析: 🔍 CSV分析ボタンで詳細情報を確認できます。\n"
                "設定を確認して保存してください。"
            )

        except Exception as e:
            messagebox.showerror("❌ エラー", f"CSV処理中にエラーが発生しました:\n{e}")

    def update_config_from_csv(self, df):
        """CSVデータから設定を更新"""
        # 会議室情報を更新
        self.update_rooms_from_csv(df)

        # UIを再構築（ポップアップ表示項目の自動更新は削除）
        self.refresh_ui()

    def update_rooms_from_csv(self, df):
        """CSVから会議室情報を更新（既存設定を保持）"""
        # room_nameカラムから会議室を抽出
        room_column = None
        for col in df.columns:
            if 'room' in col.lower() or '会議室' in col or 'ホール' in col:
                room_column = col
                break

        if room_column is None:
            # フォールバック: 最初の列を使用
            room_column = df.columns[0] if len(df.columns) > 0 else None

        if room_column:
            # ユニークな会議室名を取得
            unique_rooms = df[room_column].dropna().unique()

            # 既存の会議室設定を保持
            existing_rooms = {room['csv_name']: room for room in self.config.get('rooms', [])}
            new_rooms = []

            # 使用済みIDを追跡するセット
            used_ids = set()

            # CSVの各会議室について処理
            for i, room_name in enumerate(unique_rooms):
                if room_name and str(room_name).strip():
                    room_name_clean = str(room_name).strip()

                    # 既存の設定がある場合はそれを保持
                    if room_name_clean in existing_rooms:
                        room_data = existing_rooms[room_name_clean]
                        new_rooms.append(room_data)
                        used_ids.add(room_data['id'])
                    else:
                        # 新しい会議室にユニークなIDを割り当て
                        room_id = f"room-{i+1}"
                        counter = 1
                        while room_id in used_ids:
                            counter += 1
                            room_id = f"room-{i+counter}"

                        used_ids.add(room_id)

                        new_rooms.append({
                            "csv_name": room_name_clean,
                            "id": room_id,
                            "display_name": room_name_clean
                        })

            self.config['rooms'] = new_rooms

    def load_csv_popup_fields_only(self):
        """ポップアップ項目のみを更新するCSV読み込み"""
        try:
            file_path = filedialog.askopenfilename(
                title="ポップアップ項目更新用CSVファイルを選択",
                filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")],
                initialdir=os.getcwd()
            )

            if not file_path:
                return

            # CSVファイルを読み込む
            self.process_csv_popup_fields_only(file_path)

        except Exception as e:
            messagebox.showerror("❌ エラー", f"CSVファイルの読み込み中にエラーが発生しました:\n{e}")

    def process_csv_popup_fields_only(self, file_path):
        """ポップアップ項目のみCSVファイルを処理"""
        try:
            # 複数エンコーディングでCSVを読み込み
            encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis', 'iso-2022-jp']
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except Exception:
                    continue

            if df is None:
                messagebox.showerror("❌ エラー", "CSVファイルを読み込めませんでした。エンコーディングを確認してください。")
                return

            # 確認ダイアログ
            result = messagebox.askyesno(
                "📋 ポップアップ項目更新確認",
                f"CSVファイル: {os.path.basename(file_path)}\n"
                f"行数: {len(df)}行\n"
                f"列数: {len(df.columns)}列\n\n"
                "このCSVファイルからポップアップ項目を更新しますか？\n"
                "(会議室設定や他の設定は変更されません)"
            )

            if not result:
                return

            # ポップアップ項目のみを更新
            self.update_popup_fields_from_csv(df)

            messagebox.showinfo(
                "✅ ポップアップ項目更新完了",
                f"CSVヘッダーからポップアップ項目を更新しました。\n"
                f"表示項目: {len(df.columns)}個\n\n"
                "📋 「ポップアップ表示項目」タブで確認してください。\n"
                "設定を確認して保存してください。"
            )

        except Exception as e:
            messagebox.showerror("❌ エラー", f"ポップアップ項目処理中にエラーが発生しました:\n{e}")

    def update_popup_fields_from_csv(self, df):
        """CSVデータからポップアップ項目のみを更新（既存の順番を保護）"""
        # CSVの列名を取得
        csv_columns = df.columns.tolist()

        # ✨ 既存の順番付きリストを保護
        existing_modal_fields_list = self.config.get('modal_fields_list', [])
        existing_modal_fields_dict = self.config.get('modal_fields', {})

        # CSVのカラムに対応する既存項目を順番を保持したまま更新
        new_modal_fields_list = []

        # 既存の有効項目から、CSVに存在するものを優先順で追加
        for field_item in existing_modal_fields_list:
            display_name = field_item.get('display_name', '')
            csv_field = field_item.get('csv_field', '')
            # CSVのカラムに存在するかチェック
            if csv_field in csv_columns or display_name in csv_columns:
                # カラム名で統一（CSVの実際のカラム名を使用）
                actual_csv_field = csv_field if csv_field in csv_columns else display_name
                new_modal_fields_list.append({
                    "display_name": display_name,
                    "csv_field": actual_csv_field
                })

        # 既存の辞書形式からも確認（後方互換性）
        for display_name, csv_field in existing_modal_fields_dict.items():
            if csv_field in csv_columns and not any(item['display_name'] == display_name for item in new_modal_fields_list):
                new_modal_fields_list.append({
                    "display_name": display_name,
                    "csv_field": csv_field
                })

        # CSVに新しいカラムがある場合、末尾に追加
        for col in csv_columns:
            if not any(item['csv_field'] == col for item in new_modal_fields_list):
                new_modal_fields_list.append({
                    "display_name": col,
                    "csv_field": col
                })

        # 設定を更新
        self.config['modal_fields_list'] = new_modal_fields_list
        self.config['modal_fields'] = {item['display_name']: item['csv_field'] for item in new_modal_fields_list}
        self.config['disabled_modal_fields'] = {}

        # UIを再構築（ポップアップ表示項目タブのみ）
        self.populate_modal_fields()


    def suggest_split_rules(self):
        """CSV読み込み後に分割ルールの推奨を表示"""
        rooms = self.config.get('rooms', [])
        if len(rooms) <= 3:
            return

        # 組み合わせルールの推奨を作成
        room_names = [room['display_name'] for room in rooms[:6]]  # 最初の6件で推奨

        if len(room_names) >= 3:
            suggestions = [
                f"推奨: {room_names[0]}+{room_names[1]}+{room_names[2]} の組み合わせルール",
                f"推奨: {room_names[0]}+{room_names[1]} の組み合わせルール",
                f"推奨: {room_names[1]}+{room_names[2]} の組み合わせルール"
            ]

    def refresh_ui(self):
        """UI を再構築"""
        # 会議室タブを再構築
        for widget in self.rooms_frame.winfo_children():
            widget.destroy()
        self.setup_rooms_tab()

        # ポップアップ表示項目タブを再構築
        for widget in self.modal_fields_frame.winfo_children():
            widget.destroy()
        self.setup_modal_fields_tab()

        # 分割表示設定タブを再構築
        for widget in self.data_split_frame.winfo_children():
            widget.destroy()
        self.setup_data_split_tab()

        # マウスホイールのバインドを再設定
        self.bind_mousewheel_to_canvas(self.data_split_canvas)
        self.bind_mousewheel_to_canvas(self.rooms_canvas)
        self.bind_mousewheel_to_canvas(self.modal_fields_canvas)

        # 新しい会議室に基づいて分割ルールの推奨を表示
        self.suggest_split_rules()

    def setup_rooms_tab(self):
        self.room_entries = []
        self.room_frames = []

        # 説明フレームを他のタブと同じスタイルで追加
        description_frame = tk.Frame(self.rooms_frame, bg='#e8f5e8', relief='flat', bd=1)
        description_frame.pack(fill='x', pady=15, padx=20)
        
        icon_label = tk.Label(description_frame, text="🏢", font=('Segoe UI Emoji', 20), bg='#e8f5e8')
        icon_label.pack(pady=10)
        
        title_label = tk.Label(description_frame, text="会議室表示設定", 
                              font=('Yu Gothic UI', 14, 'bold'), bg='#e8f5e8', fg='#2e7d32')
        title_label.pack(pady=(0, 5))
        
        desc_label = tk.Label(description_frame,
                             text="カレンダーに表示・非表示、会議室名の編集をします。",
                             font=('Yu Gothic UI', 10), bg='#e8f5e8', fg='#424242',
                             justify='center')
        desc_label.pack(pady=(0, 5))

        # CSV注意書きフレーム
        csv_tip_frame = tk.Frame(description_frame, bg='#fff3cd', relief='solid', bd=1)
        csv_tip_frame.pack(fill='x', pady=(5, 10), padx=10)

        csv_tip_icon = tk.Label(csv_tip_frame, text="💡", font=('Segoe UI Emoji', 12), bg='#fff3cd')
        csv_tip_icon.pack(pady=(5, 0))

        csv_tip_label = tk.Label(csv_tip_frame,
                                text="CSVファイルにできるだけすべての会議室の予約データが含まれていると、\n追加作業なくスムーズに設定が完了します。",
                                font=('Yu Gothic UI', 9), bg='#fff3cd', fg='#856404',
                                justify='center')
        csv_tip_label.pack(pady=(0, 8))

        # Modern header with icons and styling
        header_frame = tk.Frame(self.rooms_frame, bg='#f8f9fa')
        header_frame.pack(fill='x', pady=10, padx=20)

        tk.Label(header_frame, text="CSV名", font=('Yu Gothic UI', 11, 'bold'), bg='#f8f9fa').grid(row=0, column=0, padx=10, pady=5)
        tk.Label(header_frame, text="カレンダー表示名", font=('Yu Gothic UI', 11, 'bold'), bg='#f8f9fa').grid(row=0, column=1, padx=10, pady=5)

        hidden_header = tk.Frame(header_frame, bg='#f8f9fa')
        hidden_header.grid(row=0, column=2, padx=10, pady=5)
        tk.Label(hidden_header, text="🚫 カレンダー非表示", font=('Yu Gothic UI', 10, 'bold'), bg='#f8f9fa').pack()
        tk.Label(hidden_header, text="(フィルターから除外)", font=('Yu Gothic UI', 8), fg='#6c757d', bg='#f8f9fa').pack()

        tk.Label(header_frame, text="順序操作", font=('Yu Gothic UI', 10, 'bold'), bg='#f8f9fa').grid(row=0, column=3, padx=10, pady=5)

        for i, room in enumerate(self.config.get('rooms', [])):
            self.add_room_entry(room, i + 1)
        
    

    def setup_modal_fields_tab(self):
        """ポップアップ表示項目タブのセットアップ"""
        self.modal_field_entries = []
        
        # Modern description with better typography
        description_frame = tk.Frame(self.modal_fields_frame, bg='#e3f2fd', relief='flat', bd=1)
        description_frame.pack(fill='x', pady=15, padx=20)
        
        icon_label = tk.Label(description_frame, text="📋", font=('Segoe UI Emoji', 20), bg='#e3f2fd')
        icon_label.pack(pady=10)
        
        title_label = tk.Label(description_frame, text="ポップアップ表示項目設定", 
                              font=('Yu Gothic UI', 14, 'bold'), bg='#e3f2fd', fg='#1976d2')
        title_label.pack(pady=(0, 5))
        
        desc_label = tk.Label(description_frame,
                             text="予約をクリックした時に表示される詳細ポップアップの項目を設定します。\nCSVファイルの全列から表示項目を自動検出し、表示順序を調整できます。",
                             font=('Yu Gothic UI', 10), bg='#e3f2fd', fg='#424242',
                             justify='center')
        desc_label.pack(pady=(0, 5))

        # CSV情報フレーム
        csv_info_frame = tk.Frame(description_frame, bg='#e8f5e9', relief='solid', bd=1)
        csv_info_frame.pack(fill='x', pady=(5, 10), padx=10)

        csv_info_icon = tk.Label(csv_info_frame, text="📁", font=('Segoe UI Emoji', 12), bg='#e8f5e9')
        csv_info_icon.pack(pady=(5, 0))

        csv_info_label = tk.Label(csv_info_frame,
                                text="CSV読み込み後、そのファイルの全列項目が自動的に表示されます。\n項目数は組織のCSVファイルによって変動します（20列、30列、50列など）。",
                                font=('Yu Gothic UI', 9), bg='#e8f5e9', fg='#2e7d32',
                                justify='center')
        csv_info_label.pack(pady=(0, 8))
        
        # Modal Fields List with modern styling
        fields_frame = tk.Frame(self.modal_fields_frame, bg='#f8f9fa')
        fields_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(fields_frame, text="🎛️ 表示項目設定", 
                font=('Yu Gothic UI', 12, 'bold'), bg='#f8f9fa').pack(anchor='w', pady=(0, 10))
        
        # Header for modal fields list
        header_frame = tk.Frame(fields_frame, bg='#dee2e6', relief='flat', bd=1)
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text="✓", font=('Yu Gothic UI', 10, 'bold'), bg='#dee2e6').pack(side='left', padx=(20, 40))
        tk.Label(header_frame, text="表示名", font=('Yu Gothic UI', 10, 'bold'), bg='#dee2e6').pack(side='left', padx=(0, 100))
        tk.Label(header_frame, text="順序操作", font=('Yu Gothic UI', 10, 'bold'), bg='#dee2e6').pack(side='left')
        
        # Container for modal field entries
        self.modal_fields_container = tk.Frame(fields_frame, bg='#f8f9fa')
        self.modal_fields_container.pack(fill='both', expand=True, pady=5)
        
        # Load existing fields or create defaults
        self.populate_modal_fields()


    def populate_modal_fields(self):
        """既存の設定からポップアップ表示項目を作成"""
        # Clear existing entries
        for widget in self.modal_fields_container.winfo_children():
            widget.destroy()
        self.modal_field_entries = []

        # ✨ 順序付きリストを優先的に使用（新形式）
        modal_fields_list = self.config.get('modal_fields_list', [])
        disabled_fields = self.config.get('disabled_modal_fields', {})

        # modal_fields_listが存在する場合（新形式）
        if modal_fields_list:
            for field_item in modal_fields_list:
                display_name = field_item.get('display_name', '')
                csv_field = field_item.get('csv_field', '')
                if display_name and csv_field:
                    self.add_modal_field_entry(display_name, csv_field, enabled=True)
        else:
            # フォールバック：従来の辞書形式を使用（後方互換性）
            existing_fields = self.config.get('modal_fields', {})
            if existing_fields:
                for display_name, csv_field in existing_fields.items():
                    self.add_modal_field_entry(display_name, csv_field, enabled=True)

        # 無効化された項目も復元（チェックボックスはオフ状態で）
        if disabled_fields:
            for display_name, csv_field in disabled_fields.items():
                # 有効な項目と重複しないもののみ追加
                existing_enabled = [item.get('display_name') for item in modal_fields_list]
                if display_name not in existing_enabled and display_name not in self.config.get('modal_fields', {}):
                    self.add_modal_field_entry(display_name, csv_field, enabled=False)

    def add_modal_field_entry(self, display_name="", csv_field="", enabled=False):
        """ポップアップ表示項目エントリを追加"""
        entry_frame = tk.Frame(self.modal_fields_container, bg='white', relief='solid', bd=1)
        entry_frame.pack(fill='x', pady=3, padx=5, ipady=5)
        
        # Enable checkbox with modern style
        enabled_var = tk.BooleanVar(value=enabled)
        check_frame = tk.Frame(entry_frame, bg='white')
        check_frame.pack(side='left', padx=(15, 30))
        tk.Checkbutton(check_frame, variable=enabled_var, bg='white',
                      activebackground='#e9ecef', font=('Yu Gothic UI', 10)).pack()
        
        # Display name entry with modern style
        display_name_var = tk.StringVar(value=display_name)
        display_entry = tk.Entry(entry_frame, textvariable=display_name_var, width=25,
                               font=('Yu Gothic UI', 10), relief='flat', bd=1,
                               highlightthickness=2, highlightcolor='#007bff',
                               bg='#f8f9fa', fg='#495057')
        display_entry.pack(side='left', padx=(0, 30), ipady=5)
        
        # CSV field is automatically set to display_name (no dropdown needed)
        csv_field_var = tk.StringVar(value=csv_field or display_name)
        
        # Order control buttons with modern style
        button_frame = tk.Frame(entry_frame, bg='white')
        button_frame.pack(side='left', padx=(0, 15))
        
        up_btn = tk.Button(button_frame, text="⬆", width=3, height=1,
                          font=('Yu Gothic UI', 10, 'bold'), bg='#6c757d', fg='white',
                          relief='flat', bd=0, cursor='hand2',
                          command=lambda: self.move_modal_field_up(entry_vars))
        up_btn.pack(side='left', padx=2)
        
        down_btn = tk.Button(button_frame, text="⬇", width=3, height=1,
                            font=('Yu Gothic UI', 10, 'bold'), bg='#6c757d', fg='white',
                            relief='flat', bd=0, cursor='hand2',
                            command=lambda: self.move_modal_field_down(entry_vars))
        down_btn.pack(side='left', padx=2)
        
        # Delete button with modern style
        delete_btn = tk.Button(entry_frame, text="🗑", width=3, height=1,
                              font=('Segoe UI Emoji', 12), bg='#dc3545', fg='white',
                              relief='flat', bd=0, cursor='hand2',
                              command=lambda: self.remove_modal_field_entry(entry_vars))
        delete_btn.pack(side='left', padx=(10, 15))
        
        # Hover effects
        def on_enter_up(e): up_btn.config(bg='#5a6268')
        def on_leave_up(e): up_btn.config(bg='#6c757d')
        def on_enter_down(e): down_btn.config(bg='#5a6268')
        def on_leave_down(e): down_btn.config(bg='#6c757d')
        def on_enter_delete(e): delete_btn.config(bg='#c82333')
        def on_leave_delete(e): delete_btn.config(bg='#dc3545')
        
        up_btn.bind('<Enter>', on_enter_up)
        up_btn.bind('<Leave>', on_leave_up)
        down_btn.bind('<Enter>', on_enter_down)
        down_btn.bind('<Leave>', on_leave_down)
        delete_btn.bind('<Enter>', on_enter_delete)
        delete_btn.bind('<Leave>', on_leave_delete)
        
        # Auto-sync display_name to csv_field
        def sync_fields(*args):
            csv_field_var.set(display_name_var.get())
        
        display_name_var.trace('w', sync_fields)
        sync_fields()  # Initialize sync
        
        entry_vars = {
            'frame': entry_frame,
            'enabled': enabled_var,
            'display_name': display_name_var,
            'csv_field': csv_field_var
        }
        
        self.modal_field_entries.append(entry_vars)
        self.update_add_field_button()

    def update_add_field_button(self):
        """新規項目追加ボタンを更新（削除済み）"""
        pass

    def move_modal_field_up(self, entry_vars):
        """ポップアップ表示項目を上に移動"""
        current_index = self.modal_field_entries.index(entry_vars)
        if current_index > 0:
            # 交換する前に参照を保存
            target_entry = self.modal_field_entries[current_index-1]

            # Swap positions
            self.modal_field_entries[current_index], self.modal_field_entries[current_index-1] = \
                self.modal_field_entries[current_index-1], self.modal_field_entries[current_index]

            # Repack frames
            entry_vars['frame'].pack_forget()
            entry_vars['frame'].pack(fill='x', pady=3, padx=5, ipady=5,
                                   before=target_entry['frame'])

    def move_modal_field_down(self, entry_vars):
        """ポップアップ表示項目を下に移動"""
        current_index = self.modal_field_entries.index(entry_vars)
        if current_index < len(self.modal_field_entries) - 1:
            # 交換する前に参照を保存
            target_entry = self.modal_field_entries[current_index+1]

            # Swap positions
            self.modal_field_entries[current_index], self.modal_field_entries[current_index+1] = \
                self.modal_field_entries[current_index+1], self.modal_field_entries[current_index]

            # Repack frames
            entry_vars['frame'].pack_forget()
            entry_vars['frame'].pack(fill='x', pady=3, padx=5, ipady=5,
                                   after=target_entry['frame'])

    def remove_modal_field_entry(self, entry_vars):
        """ポップアップ表示項目エントリを削除"""
        if messagebox.askyesno("確認", "この表示項目を削除してもよろしいですか？"):
            entry_vars['frame'].destroy()
            self.modal_field_entries.remove(entry_vars)

    def add_room_entry(self, room=None, row_position=None):
        """会議室エントリを追加"""
        if row_position is None:
            row_position = len(self.room_entries) + 1

        # Create modern room entry frame
        room_frame = tk.Frame(self.rooms_frame, bg='white', relief='solid', bd=1)
        room_frame.pack(fill='x', pady=3, padx=20, ipady=5)

        # CSV name
        csv_name_var = tk.StringVar(value=room.get('csv_name', '') if room else '')
        csv_entry = tk.Entry(room_frame, textvariable=csv_name_var, width=15,
                           font=('Yu Gothic UI', 10), bg='#f8f9fa', relief='flat', bd=1)
        csv_entry.pack(side='left', padx=(10, 15), pady=5)

        # Display name
        display_name_var = tk.StringVar(value=room.get('display_name', '') if room else '')
        display_entry = tk.Entry(room_frame, textvariable=display_name_var, width=20,
                                font=('Yu Gothic UI', 10), bg='#f8f9fa', relief='flat', bd=1)
        display_entry.pack(side='left', padx=(0, 15), pady=5)

        # Hidden checkbox
        is_hidden = tk.BooleanVar(value=room.get('id', '') in self.config.get('hidden_room_ids', []) if room else False)
        hidden_check = tk.Checkbutton(room_frame, variable=is_hidden, bg='white')
        hidden_check.pack(side='left', padx=(15, 20))

        # Order control buttons
        button_frame = tk.Frame(room_frame, bg='white')
        button_frame.pack(side='left', padx=(15, 10))

        up_btn = tk.Button(button_frame, text="⬆", width=3, height=1,
                          font=('Yu Gothic UI', 10, 'bold'), bg='#6c757d', fg='white',
                          relief='flat', bd=0, cursor='hand2',
                          command=lambda: self.move_room_up(entry_vars))
        up_btn.pack(side='left', padx=2)

        down_btn = tk.Button(button_frame, text="⬇", width=3, height=1,
                            font=('Yu Gothic UI', 10, 'bold'), bg='#6c757d', fg='white',
                            relief='flat', bd=0, cursor='hand2',
                            command=lambda: self.move_room_down(entry_vars))
        down_btn.pack(side='left', padx=2)

        # Delete button
        delete_btn = tk.Button(room_frame, text="🗑", font=('Segoe UI Emoji', 10),
                              bg='#dc3545', fg='white', relief='flat', bd=0,
                              cursor='hand2', width=3,
                              command=lambda: self.remove_room_entry(room_frame, entry_vars))
        delete_btn.pack(side='left', padx=(10, 15))

        # Hover effects for order buttons
        def on_enter_up(e): up_btn.config(bg='#5a6268')
        def on_leave_up(e): up_btn.config(bg='#6c757d')
        def on_enter_down(e): down_btn.config(bg='#5a6268')
        def on_leave_down(e): down_btn.config(bg='#6c757d')

        up_btn.bind('<Enter>', on_enter_up)
        up_btn.bind('<Leave>', on_leave_up)
        down_btn.bind('<Enter>', on_enter_down)
        down_btn.bind('<Leave>', on_leave_down)

        # Store reference
        room_id_var = tk.StringVar(value=room.get('id', '') if room else '')
        entry_vars = {
            'frame': room_frame,
            'csv_name': csv_name_var,
            'display_name': display_name_var,
            'is_hidden': is_hidden,
            'id': room_id_var
        }
        
        self.room_entries.append(entry_vars)
        self.room_frames.append(room_frame)

        # Add new room button
        self.update_add_room_button()

    def update_add_room_button(self):
        """新規会議室追加ボタンを更新"""
        if hasattr(self, 'add_room_button_frame'):
            self.add_room_button_frame.destroy()
        
        self.add_room_button_frame = tk.Frame(self.rooms_frame, bg='#f8f9fa')
        self.add_room_button_frame.pack(fill='x', pady=15, padx=20)
        
        add_button = tk.Button(self.add_room_button_frame, text="➕ 新しい会議室を追加",
                              font=('Yu Gothic UI', 10, 'bold'), bg='#17a2b8', fg='white',
                              relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                              command=self.add_room_and_update_splits)
        add_button.pack()
        
        def on_enter_add(e): add_button.config(bg='#138496')
        def on_leave_add(e): add_button.config(bg='#17a2b8')
        add_button.bind('<Enter>', on_enter_add)
        add_button.bind('<Leave>', on_leave_add)

    def add_room_and_update_splits(self):
        """会議室を追加し、分割設定を自動更新"""
        # 会議室を追加
        self.add_room_entry()

        # 少し待ってから分割設定を更新（UIの更新完了を待つ）
        self.root.after(100, self.update_split_settings_if_exists)

    def update_split_settings_if_exists(self):
        """分割設定が存在する場合のみ更新"""
        if hasattr(self, 'data_split_entries') and self.data_split_entries:
            try:
                self.refresh_all_data_split_entries()
            except Exception as e:
                # エラーが発生した場合は無視（分割設定画面が開かれていない可能性がある）
                pass

    def move_room_up(self, entry_vars):
        """会議室を上に移動"""
        current_index = self.room_entries.index(entry_vars)
        if current_index > 0:
            # 交換する前に参照を保存
            target_entry = self.room_entries[current_index-1]

            # リスト内で位置を交換
            self.room_entries[current_index], self.room_entries[current_index-1] = \
                self.room_entries[current_index-1], self.room_entries[current_index]

            # フレームの表示順序を変更
            entry_vars['frame'].pack_forget()
            entry_vars['frame'].pack(fill='x', pady=3, padx=20, ipady=5,
                                   before=target_entry['frame'])

    def move_room_down(self, entry_vars):
        """会議室を下に移動"""
        current_index = self.room_entries.index(entry_vars)
        if current_index < len(self.room_entries) - 1:
            # 交換する前に参照を保存
            target_entry = self.room_entries[current_index+1]

            # リスト内で位置を交換
            self.room_entries[current_index], self.room_entries[current_index+1] = \
                self.room_entries[current_index+1], self.room_entries[current_index]

            # フレームの表示順序を変更
            entry_vars['frame'].pack_forget()
            entry_vars['frame'].pack(fill='x', pady=3, padx=20, ipady=5,
                                   after=target_entry['frame'])

    def remove_room_entry(self, frame, entry_vars):
        """会議室エントリを削除"""
        if messagebox.askyesno("確認", "この会議室を削除してもよろしいですか？"):
            frame.destroy()
            self.room_entries.remove(entry_vars)
            self.room_frames.remove(frame)


    def setup_data_split_tab(self):
        """会議室分割表示設定タブのセットアップ"""
        self.data_split_entries = []
        
        # 説明テキスト
        description_frame = tk.Frame(self.data_split_frame, bg='#fff3e0', relief='flat', bd=1)
        description_frame.pack(fill='x', pady=15, padx=20)
        
        icon_label = tk.Label(description_frame, text="🔄", font=('Segoe UI Emoji', 20), bg='#fff3e0')
        icon_label.pack(pady=10)
        
        title_label = tk.Label(description_frame, text="会議室分割表示設定", 
                              font=('Yu Gothic UI', 14, 'bold'), bg='#fff3e0', fg='#f57c00')
        title_label.pack(pady=(0, 5))
        
        desc_label = tk.Label(description_frame,
                             text="特定の会議室の予約データを複数の会議室にコピーして表示することができます。\n例：「ホール全」の予約を「ホールⅠ」と「ホールⅡ」の両方に表示する",
                             font=('Yu Gothic UI', 10), bg='#fff3e0', fg='#424242',
                             justify='center')
        desc_label.pack(pady=(0, 5))

        # 注意書きフレーム
        warning_frame = tk.Frame(description_frame, bg='#ffebee', relief='solid', bd=1)
        warning_frame.pack(fill='x', pady=(5, 10), padx=10)

        warning_icon = tk.Label(warning_frame, text="⚠️", font=('Segoe UI Emoji', 12), bg='#ffebee')
        warning_icon.pack(pady=(5, 0))

        warning_label = tk.Label(warning_frame,
                               text="【重要】分割設定を行う前に、まず「会議室表示設定」タブで\nすべての会議室の設定を完了してください。",
                               font=('Yu Gothic UI', 9, 'bold'), bg='#ffebee', fg='#c62828',
                               justify='center')
        warning_label.pack(pady=(0, 8))
        
        # 既存のルールを表示
        existing_rules = self.config.get('data_split_rules', [])
        for rule in existing_rules:
            self.add_data_split_entry_new(rule)
        
        # デフォルトルールがない場合はサンプルを追加
        if not existing_rules:
            default_rule = {
                "source_room_id": "hall-combined",
                "target_room_ids": ["hall-1", "hall-2"],
                "enabled": True,
                "description": "ホール全の予約をホールⅠとホールⅡにコピー"
            }
            self.add_data_split_entry_new(default_rule)
        
        # ボタンフレーム
        button_frame = tk.Frame(self.data_split_frame, bg='#f8f9fa')
        button_frame.pack(pady=15, fill='x', padx=20)

        # 追加ボタン
        add_button = tk.Button(button_frame, text="➕ 新しい分割ルールを追加",
                              font=('Yu Gothic UI', 10, 'bold'), bg='#17a2b8', fg='white',
                              relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                              command=self.add_new_data_split_entry_new)
        add_button.pack(side='left', padx=(0, 10))

        # 全更新ボタン
        refresh_all_button = tk.Button(button_frame, text="🔄 全会議室リスト更新",
                                     font=('Yu Gothic UI', 10, 'bold'), bg='#28a745', fg='white',
                                     relief='flat', bd=0, cursor='hand2', padx=20, pady=8,
                                     command=self.refresh_all_data_split_entries)
        refresh_all_button.pack(side='left')

        def on_enter_add(e): add_button.config(bg='#138496')
        def on_leave_add(e): add_button.config(bg='#17a2b8')
        add_button.bind('<Enter>', on_enter_add)
        add_button.bind('<Leave>', on_leave_add)

        def on_enter_refresh(e): refresh_all_button.config(bg='#218838')
        def on_leave_refresh(e): refresh_all_button.config(bg='#28a745')
        refresh_all_button.bind('<Enter>', on_enter_refresh)
        refresh_all_button.bind('<Leave>', on_leave_refresh)

    def add_data_split_entry_new(self, rule_data=None):
        """会議室分割表示エントリを追加（縦並びレイアウト）"""
        if rule_data is None:
            rule_data = {
                "source_room_id": "",
                "target_room_ids": [],
                "enabled": False,
                "description": ""
            }

        entry_frame = tk.Frame(self.data_split_frame, bg='white', relief='solid', bd=1)
        entry_frame.pack(pady=5, padx=20, fill='x', ipady=10)

        # 有効/無効チェックボックスと説明を上部に配置
        top_frame = tk.Frame(entry_frame, bg='white')
        top_frame.pack(fill='x', pady=5, padx=10)

        enabled_var = tk.BooleanVar(value=rule_data.get('enabled', False))
        tk.Checkbutton(top_frame, text="有効", variable=enabled_var, font=('Yu Gothic UI', 10, 'bold'), bg='white').pack(side='left', padx=5)

        # 説明テキスト
        description_var = tk.StringVar(value=rule_data.get('description', ''))
        tk.Label(top_frame, text="説明:", font=('Yu Gothic UI', 10), bg='white').pack(side='left', padx=(20, 5))
        description_entry = tk.Entry(top_frame, textvariable=description_var, width=40, font=('Yu Gothic UI', 10), bg='#f8f9fa')
        description_entry.pack(side='left', padx=5)

        # 削除ボタンを右端に配置
        delete_button = tk.Button(top_frame, text="🗑", fg='white', bg='#dc3545', font=('Segoe UI Emoji', 10),
                                command=lambda: self.remove_data_split_entry_new(entry_frame, rule_vars),
                                relief='flat', bd=0, cursor='hand2', width=3)
        delete_button.pack(side='right', padx=5)

        # 更新ボタンを追加
        refresh_button = tk.Button(top_frame, text="🔄", fg='white', bg='#28a745', font=('Segoe UI Emoji', 10),
                                 command=lambda: self.refresh_data_split_entry(rule_vars),
                                 relief='flat', bd=0, cursor='hand2', width=3)
        refresh_button.pack(side='right', padx=5)

        # コピー元会議室選択（縦並び）
        source_frame = tk.Frame(entry_frame, bg='white')
        source_frame.pack(fill='x', pady=5, padx=20)

        tk.Label(source_frame, text="コピー元会議室:", font=('Yu Gothic UI', 10, 'bold'), bg='white').pack(anchor='w')

        # 会議室名を日本語で表示（現在の会議室リストを取得）
        current_rooms = self.get_current_rooms_list()
        room_options = ["-- 選択 --"]
        room_id_map = {}

        for room in current_rooms:
            display_name = room['display_name']
            room_options.append(display_name)
            room_id_map[display_name] = room['id']

        source_room_var = tk.StringVar()
        # 既存のroom_idから対応するdisplay_nameを見つける
        current_source_id = rule_data.get('source_room_id', '')
        current_source_name = next((room['display_name'] for room in current_rooms
                                  if room['id'] == current_source_id), "-- 選択 --")
        source_room_var.set(current_source_name)

        source_menu = ttk.OptionMenu(source_frame, source_room_var,
                                    source_room_var.get(), *room_options)
        source_menu.pack(anchor='w', pady=2)

        # コピー先会議室選択（縦並び）
        target_frame = tk.Frame(entry_frame, bg='white')
        target_frame.pack(fill='x', pady=5, padx=20)

        tk.Label(target_frame, text="コピー先会議室:", font=('Yu Gothic UI', 10, 'bold'), bg='white').pack(anchor='w')

        target_room_vars = {}
        target_room_ids = rule_data.get('target_room_ids', [])

        target_checkboxes_frame = tk.Frame(target_frame, bg='white')
        target_checkboxes_frame.pack(anchor='w', pady=2)

        for room in current_rooms:
            room_id = room['id']
            if room_id != rule_data.get('source_room_id'):  # 元会議室は除外
                var = tk.BooleanVar(value=room_id in target_room_ids)
                room_name = room['display_name']
                cb = tk.Checkbutton(target_checkboxes_frame, text=room_name, variable=var, font=('Yu Gothic UI', 10), bg='white')
                cb.pack(anchor='w')
                target_room_vars[room_id] = var
        
        # エントリ情報を保存（room_id_mapも含める）
        rule_vars = {
            'frame': entry_frame,
            'enabled': enabled_var,
            'source_room': source_room_var,
            'target_rooms': target_room_vars,
            'description': description_var,
            'room_id_map': room_id_map
        }
        
        self.data_split_entries.append(rule_vars)

    def get_current_rooms_list(self):
        """現在の会議室リストを取得（画面上の入力値も含む）"""
        current_rooms = []

        # 既存のconfig.jsonから会議室を取得
        for room in self.config.get('rooms', []):
            current_rooms.append(room)

        # 画面上で追加された会議室も取得（room_entriesが初期化されている場合のみ）
        if hasattr(self, 'room_entries'):
            for entry_vars in self.room_entries:
                csv_name = entry_vars['csv_name'].get().strip()
                display_name = entry_vars['display_name'].get().strip()

                if csv_name and display_name:
                    # 既存の会議室IDを探す
                    existing_room = next((room for room in current_rooms
                                        if room.get('csv_name') == csv_name), None)

                    if existing_room:
                        # 既存の会議室の場合は更新
                        existing_room['display_name'] = display_name
                    else:
                        # 新しい会議室の場合は追加
                        room_id = f"room-{len(current_rooms) + 1}"
                        # 重複しないIDを生成
                        while any(room['id'] == room_id for room in current_rooms):
                            room_id = f"room-{len(current_rooms) + len(self.room_entries) + 1}"

                        current_rooms.append({
                            'id': room_id,
                            'csv_name': csv_name,
                            'display_name': display_name
                        })

        return current_rooms

    def refresh_data_split_entry(self, rule_vars):
        """分割表示エントリの会議室リストを更新"""
        # 現在の設定値を保存
        current_source = rule_vars['source_room'].get() if 'source_room' in rule_vars else "-- 選択 --"
        current_targets = {}
        if 'target_rooms' in rule_vars:
            for room_id, var in rule_vars['target_rooms'].items():
                current_targets[room_id] = var.get()

        # フレーム内の選択肢部分を再構築
        entry_frame = rule_vars['frame']

        # 既存の選択肢フレームを削除して再構築
        for widget in entry_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                # source_frameとtarget_frameを特定して更新
                for child in widget.winfo_children():
                    if isinstance(child, ttk.OptionMenu):
                        # ソース選択の更新
                        self.refresh_source_room_options(widget, rule_vars, current_source)
                        break
                    elif isinstance(child, tk.Frame) and child.winfo_children():
                        # ターゲット選択の更新
                        first_child = child.winfo_children()[0]
                        if isinstance(first_child, tk.Checkbutton):
                            self.refresh_target_room_options(widget, rule_vars, current_targets)
                            break

    def refresh_source_room_options(self, source_frame, rule_vars, current_source):
        """ソース会議室選択の更新"""
        # 既存のOptionMenuを削除
        for widget in source_frame.winfo_children():
            if isinstance(widget, ttk.OptionMenu):
                widget.destroy()

        # 新しい会議室リストで再構築
        current_rooms = self.get_current_rooms_list()
        room_options = ["-- 選択 --"]
        room_id_map = {}

        for room in current_rooms:
            display_name = room['display_name']
            room_options.append(display_name)
            room_id_map[display_name] = room['id']

        source_room_var = rule_vars['source_room']
        if current_source in room_options:
            source_room_var.set(current_source)
        else:
            source_room_var.set("-- 選択 --")

        source_menu = ttk.OptionMenu(source_frame, source_room_var,
                                    source_room_var.get(), *room_options)
        source_menu.pack(anchor='w', pady=2)

        # room_id_mapを更新
        rule_vars['room_id_map'] = room_id_map

    def refresh_target_room_options(self, target_frame, rule_vars, current_targets):
        """ターゲット会議室選択の更新"""
        # 既存のチェックボックスフレームを削除
        for widget in target_frame.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_children():
                first_child = widget.winfo_children()[0]
                if isinstance(first_child, tk.Checkbutton):
                    widget.destroy()
                    break

        # 新しいチェックボックスフレームを作成
        target_checkboxes_frame = tk.Frame(target_frame, bg='white')
        target_checkboxes_frame.pack(anchor='w', pady=2)

        current_rooms = self.get_current_rooms_list()
        new_target_room_vars = {}

        for room in current_rooms:
            room_id = room['id']
            var = tk.BooleanVar(value=current_targets.get(room_id, False))
            room_name = room['display_name']
            cb = tk.Checkbutton(target_checkboxes_frame, text=room_name, variable=var,
                              font=('Yu Gothic UI', 10), bg='white')
            cb.pack(anchor='w')
            new_target_room_vars[room_id] = var

        # target_roomsを更新
        rule_vars['target_rooms'] = new_target_room_vars

    def refresh_all_data_split_entries(self):
        """すべての分割表示エントリの会議室リストを更新"""
        for rule_vars in self.data_split_entries:
            self.refresh_data_split_entry(rule_vars)

        # 更新完了のメッセージ
        messagebox.showinfo("更新完了", "すべての分割ルールの会議室リストを更新しました。")

    def add_new_data_split_entry_new(self):
        """新しい会議室分割表示エントリを追加"""
        self.add_data_split_entry_new()

    def remove_data_split_entry_new(self, frame, rule_vars):
        """会議室分割表示エントリを削除"""
        if messagebox.askyesno("確認", "この分割ルールを削除してもよろしいですか？"):
            frame.destroy()
            self.data_split_entries.remove(rule_vars)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditorApp(root)
    root.mainloop()