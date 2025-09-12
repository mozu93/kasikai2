import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import tkinter.ttk as ttk
import json
import os
import pandas as pd

CONFIG_FILE = 'config.json'

class ConfigEditorApp:
    def __init__(self, master):
        self.master = master
        master.title("会議室予約システム 設定エディタ")
        
        # Set window size and make it resizable
        master.geometry("800x600")
        master.minsize(600, 400)
        
        # Set font for better Japanese character support on Windows
        try:
            import tkinter.font as tkFont
            self.default_font = tkFont.nametofont("TkDefaultFont")
            self.default_font.configure(family="Yu Gothic UI", size=9)
            master.option_add("*Font", self.default_font)
        except:
            pass  # Fallback to system default if font setting fails

        self.config = self.load_config()

        # All possible internal field names for CSV mapping
        self.all_internal_fields = [
            "booking_datetime", "room_name", "total_amount", "cancellation_date",
            "display_name", "company_name", "extension", "equipment", "notes",
            "memo", "purpose", "member_type", "department_name", "contact_person",
            "zip_code", "prefecture", "city", "address_rest", "phone_number"
        ]

        # Notebook for tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, expand=True, fill='both')

        # Rooms Tab with scrollable frame
        self.rooms_tab_frame = tk.Frame(self.notebook)
        self.notebook.add(self.rooms_tab_frame, text='会議室設定')
        self.rooms_canvas = tk.Canvas(self.rooms_tab_frame)
        self.rooms_scrollbar = ttk.Scrollbar(self.rooms_tab_frame, orient="vertical", command=self.rooms_canvas.yview)
        self.rooms_scrollable_frame = tk.Frame(self.rooms_canvas)
        
        self.rooms_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.rooms_canvas.configure(scrollregion=self.rooms_canvas.bbox("all"))
        )
        
        self.rooms_canvas.create_window((0, 0), window=self.rooms_scrollable_frame, anchor="nw")
        self.rooms_canvas.configure(yscrollcommand=self.rooms_scrollbar.set)
        
        self.rooms_canvas.pack(side="left", fill="both", expand=True)
        self.rooms_scrollbar.pack(side="right", fill="y")
        
        self.rooms_frame = self.rooms_scrollable_frame
        self.setup_rooms_tab()


        # Modal Fields Tab with scrollable frame
        self.modal_fields_tab_frame = tk.Frame(self.notebook)
        self.notebook.add(self.modal_fields_tab_frame, text='ポップアップ表示項目')
        self.modal_fields_canvas = tk.Canvas(self.modal_fields_tab_frame)
        self.modal_fields_scrollbar = ttk.Scrollbar(self.modal_fields_tab_frame, orient="vertical", command=self.modal_fields_canvas.yview)
        self.modal_fields_scrollable_frame = tk.Frame(self.modal_fields_canvas)
        
        self.modal_fields_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.modal_fields_canvas.configure(scrollregion=self.modal_fields_canvas.bbox("all"))
        )
        
        self.modal_fields_canvas.create_window((0, 0), window=self.modal_fields_scrollable_frame, anchor="nw")
        self.modal_fields_canvas.configure(yscrollcommand=self.modal_fields_scrollbar.set)
        
        self.modal_fields_canvas.pack(side="left", fill="both", expand=True)
        self.modal_fields_scrollbar.pack(side="right", fill="y")
        
        self.modal_fields_frame = self.modal_fields_scrollable_frame
        self.setup_modal_fields_tab()

        # Data Split Settings Tab with scrollable frame
        self.data_split_tab_frame = tk.Frame(self.notebook)
        self.notebook.add(self.data_split_tab_frame, text='データ分割設定')
        self.data_split_canvas = tk.Canvas(self.data_split_tab_frame)
        self.data_split_scrollbar = ttk.Scrollbar(self.data_split_tab_frame, orient="vertical", command=self.data_split_canvas.yview)
        self.data_split_scrollable_frame = tk.Frame(self.data_split_canvas)
        
        self.data_split_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.data_split_canvas.configure(scrollregion=self.data_split_canvas.bbox("all"))
        )
        
        self.data_split_canvas.create_window((0, 0), window=self.data_split_scrollable_frame, anchor="nw")
        self.data_split_canvas.configure(yscrollcommand=self.data_split_scrollbar.set)
        
        self.data_split_canvas.pack(side="left", fill="both", expand=True)
        self.data_split_scrollbar.pack(side="right", fill="y")
        
        self.data_split_frame = self.data_split_scrollable_frame
        self.setup_data_split_tab()

        # Enable mouse wheel scrolling
        self.bind_mousewheel_to_canvas(self.rooms_canvas)
        self.bind_mousewheel_to_canvas(self.modal_fields_canvas)
        self.bind_mousewheel_to_canvas(self.data_split_canvas)

        # Save Button
        self.save_button = tk.Button(master, text="設定を保存", command=self.save_config)
        self.save_button.pack(pady=10)

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
        if not os.path.exists(CONFIG_FILE):
            messagebox.showwarning("警告", f"{CONFIG_FILE} が見つかりません。デフォルト設定を作成します。")
            default_config = {
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
                "internal_room_ids": ["large-room", "executive-room"],
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
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            return default_config
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("エラー", f"{CONFIG_FILE} の読み込みに失敗しました。JSON形式が不正です。")
            master.destroy()
            return None
        except Exception as e:
            messagebox.showerror("エラー", f"{CONFIG_FILE} の読み込み中にエラーが発生しました: {e}")
            master.destroy()
            return None

    def save_config(self):
        try:
            # Update config from GUI elements
            self.config['rooms'] = []
            for i, entry_vars in enumerate(self.room_entries):
                csv_name = entry_vars['csv_name'].get()
                display_name = entry_vars['display_name'].get()
                is_internal = entry_vars['is_internal'].get()
                
                if csv_name and display_name:
                    room_id = entry_vars['id'].get() if entry_vars['id'].get() else f"room-{i+1}" # Use existing ID or generate new
                    self.config['rooms'].append({
                        "csv_name": csv_name,
                        "id": room_id,
                        "display_name": display_name
                    })
                    if is_internal:
                        if room_id not in self.config['internal_room_ids']:
                            self.config['internal_room_ids'].append(room_id)
                    else:
                        if room_id in self.config['internal_room_ids']:
                            self.config['internal_room_ids'].remove(room_id)
                    
                    is_hidden = entry_vars['is_hidden'].get()
                    if is_hidden:
                        if room_id not in self.config.setdefault('hidden_room_ids', []):
                            self.config['hidden_room_ids'].append(room_id)
                    else:
                        if room_id in self.config.get('hidden_room_ids', []):
                            self.config['hidden_room_ids'].remove(room_id)

            # Ensure internal_room_ids and hidden_room_ids only contain valid room IDs
            valid_room_ids = [room['id'] for room in self.config['rooms']]
            self.config['internal_room_ids'] = [id for id in self.config['internal_room_ids'] if id in valid_room_ids]
            self.config['hidden_room_ids'] = [id for id in self.config.get('hidden_room_ids', []) if id in valid_room_ids]


            # Save modal fields in order
            self.config['modal_fields'] = {}
            for entry_vars in self.modal_field_entries:
                if entry_vars['enabled'].get():  # Only save enabled fields
                    display_name = entry_vars['display_name'].get()
                    csv_field = entry_vars['csv_field'].get()
                    
                    if display_name and csv_field and csv_field != "-- 選択 --":
                        self.config['modal_fields'][display_name] = csv_field

            # Save data split rules
            self.config['data_split_rules'] = []
            for rule_vars in self.data_split_entries:
                if rule_vars['enabled'].get():  # Only save enabled rules
                    source_room_id = rule_vars['source_room'].get()
                    target_room_ids = [room_id for room_id, var in rule_vars['target_rooms'].items() if var.get()]
                    description = rule_vars['description'].get()
                    
                    if source_room_id != "-- 選択 --" and target_room_ids and description:
                        self.config['data_split_rules'].append({
                            "source_room_id": source_room_id,
                            "target_room_ids": target_room_ids,
                            "enabled": True,
                            "description": description
                        })

            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("保存完了", "設定が正常に保存されました。アプリケーションを再起動すると反映されます。")
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存中にエラーが発生しました: {e}")

    def setup_rooms_tab(self):
        self.room_entries = []
        self.room_frames = []

        # Headers with explanations
        tk.Label(self.rooms_frame, text="CSV名", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.rooms_frame, text="カレンダー表示名", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        
        internal_header = tk.Frame(self.rooms_frame)
        internal_header.grid(row=0, column=2, padx=5, pady=5)
        tk.Label(internal_header, text="内部用", font=('TkDefaultFont', 10, 'bold')).pack()
        tk.Label(internal_header, text="(黄色ハイライト)", font=('TkDefaultFont', 8), fg='gray').pack()
        
        hidden_header = tk.Frame(self.rooms_frame)
        hidden_header.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(hidden_header, text="カレンダー非表示", font=('TkDefaultFont', 10, 'bold')).pack()
        tk.Label(hidden_header, text="(フィルターから除外)", font=('TkDefaultFont', 8), fg='gray').pack()
        
        tk.Label(self.rooms_frame, text="操作", font=('TkDefaultFont', 10, 'bold')).grid(row=0, column=4, padx=5, pady=5)

        for i, room in enumerate(self.config.get('rooms', [])):
            self.add_room_entry(room, i + 1)

        self.add_room_button = tk.Button(self.rooms_frame, text="会議室を追加", command=self.add_new_room_entry)
        self.add_room_button.grid(row=len(self.config.get('rooms', [])) + 1, column=0, columnspan=5, pady=10)

    def add_room_entry(self, room_data, row_idx):
        frame = tk.Frame(self.rooms_frame)
        frame.grid(row=row_idx, column=0, columnspan=5, sticky='ew')
        self.room_frames.append(frame)

        csv_name_var = tk.StringVar(value=room_data.get('csv_name', ''))
        display_name_var = tk.StringVar(value=room_data.get('display_name', ''))
        id_var = tk.StringVar(value=room_data.get('id', '')) # Store ID but don't display for direct edit
        is_internal_var = tk.BooleanVar(value=room_data['id'] in self.config.get('internal_room_ids', []))
        is_hidden_var = tk.BooleanVar(value=room_data['id'] in self.config.get('hidden_room_ids', []))

        entry_vars = {
            'csv_name': csv_name_var,
            'display_name': display_name_var,
            'id': id_var,
            'is_internal': is_internal_var,
            'is_hidden': is_hidden_var
        }
        self.room_entries.append(entry_vars)

        tk.Entry(frame, textvariable=csv_name_var, width=20).pack(side='left', padx=5, pady=2)
        tk.Entry(frame, textvariable=display_name_var, width=20).pack(side='left', padx=5, pady=2)
        tk.Checkbutton(frame, variable=is_internal_var).pack(side='left', padx=5, pady=2)
        tk.Checkbutton(frame, variable=is_hidden_var).pack(side='left', padx=5, pady=2)
        
        delete_button = tk.Button(frame, text="削除", command=lambda: self.remove_room_entry(frame, entry_vars))
        delete_button.pack(side='left', padx=5, pady=2)

    def add_new_room_entry(self):
        new_room_data = {"csv_name": "", "id": "", "display_name": ""}
        self.add_room_entry(new_room_data, len(self.room_frames) + 1)
        self.add_room_button.grid(row=len(self.room_frames) + 1, column=0, columnspan=5, pady=10) # Move button down

    def remove_room_entry(self, frame, entry_vars):
        if messagebox.askyesno("確認", "この会議室エントリを削除してもよろしいですか？"):
            frame.destroy()
            self.room_entries.remove(entry_vars)
            # Re-render to clean up layout (simpler than re-gridding everything)
            self.refresh_rooms_tab()

    def refresh_rooms_tab(self):
        for frame in self.room_frames:
            frame.destroy()
        self.room_frames = []
        self.room_entries = []
        for i, room in enumerate(self.config.get('rooms', [])):
            self.add_room_entry(room, i + 1)
        self.add_room_button.grid(row=len(self.config.get('rooms', [])) + 1, column=0, columnspan=5, pady=10)





    def setup_modal_fields_tab(self):
        """ポップアップ表示項目タブのセットアップ"""
        self.modal_field_entries = []
        self.csv_headers = []
        
        # 説明テキスト
        description_text = """
ポップアップ表示項目設定
予約をクリックした時に表示される詳細ポップアップの項目を設定します。
表示したい項目名を入力して、表示順序を調整できます。
        """
        
        tk.Label(self.modal_fields_frame, text=description_text.strip(), 
                justify='left', wraplength=600, font=('TkDefaultFont', 10)).pack(pady=15, padx=15, anchor='w')
        
        # Modal Fields List with Reordering
        fields_frame = tk.Frame(self.modal_fields_frame)
        fields_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        tk.Label(fields_frame, text="表示項目 (上から順に表示されます)", font=('TkDefaultFont', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Header for modal fields list
        header_frame = tk.Frame(fields_frame)
        header_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(header_frame, text="表示", font=('TkDefaultFont', 10, 'bold')).pack(side='left', padx=(0, 20))
        tk.Label(header_frame, text="表示名", font=('TkDefaultFont', 10, 'bold')).pack(side='left', padx=(0, 120))
        tk.Label(header_frame, text="順序操作", font=('TkDefaultFont', 10, 'bold')).pack(side='left')
        
        # Container for modal field entries
        self.modal_fields_container = tk.Frame(fields_frame)
        self.modal_fields_container.pack(fill='x')
        
        # Load existing fields or create defaults
        self.populate_modal_fields()



    def populate_modal_fields(self):
        """既存の設定からポップアップ表示項目を作成"""
        # Clear existing entries
        for widget in self.modal_fields_container.winfo_children():
            widget.destroy()
        self.modal_field_entries = []
        
        # Load from existing config
        existing_fields = self.config.get('modal_fields', {})
        
        if existing_fields:
            for display_name, csv_field in existing_fields.items():
                self.add_modal_field_entry(display_name, csv_field, enabled=True)
        else:
            # Add some default entries
            self.add_modal_field_entry("利用日時", "booking_datetime", enabled=True)
            self.add_modal_field_entry("会議室", "room_name", enabled=True)
            self.add_modal_field_entry("事業所名", "company_name", enabled=True)


    def add_modal_field_entry(self, display_name="", csv_field="", enabled=False):
        """ポップアップ表示項目エントリを追加"""
        entry_frame = tk.Frame(self.modal_fields_container, relief='raised', bd=1)
        entry_frame.pack(fill='x', pady=1, padx=5)
        
        # Enable checkbox
        enabled_var = tk.BooleanVar(value=enabled)
        tk.Checkbutton(entry_frame, variable=enabled_var).pack(side='left', padx=(5, 20))
        
        # Display name entry
        display_name_var = tk.StringVar(value=display_name)
        display_entry = tk.Entry(entry_frame, textvariable=display_name_var, width=20)
        display_entry.pack(side='left', padx=(0, 20))
        
        # CSV field is automatically set to display_name (no dropdown needed)
        csv_field_var = tk.StringVar(value=csv_field or display_name)
        
        # Order control buttons
        button_frame = tk.Frame(entry_frame)
        button_frame.pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="↑", width=2, 
                command=lambda: self.move_modal_field_up(entry_vars)).pack(side='left')
        tk.Button(button_frame, text="↓", width=2,
                command=lambda: self.move_modal_field_down(entry_vars)).pack(side='left')
        
        # Delete button
        tk.Button(entry_frame, text="削除", fg='red',
                command=lambda: self.remove_modal_field_entry(entry_vars)).pack(side='left', padx=5)
        
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
        
        # Add new entry button at the end
        self.update_add_field_button()
        
    def update_add_field_button(self):
        """新規項目追加ボタンを更新"""
        # Remove existing button if any
        if hasattr(self, 'add_field_button_frame'):
            self.add_field_button_frame.destroy()
            
        self.add_field_button_frame = tk.Frame(self.modal_fields_container)
        self.add_field_button_frame.pack(pady=10)
        tk.Button(self.add_field_button_frame, text="項目を追加", 
                command=self.add_new_modal_field_entry).pack()

    def add_new_modal_field_entry(self):
        """新しいポップアップ表示項目エントリを追加"""
        self.add_modal_field_entry()
        
    def remove_modal_field_entry(self, entry_vars):
        """ポップアップ表示項目エントリを削除"""
        if messagebox.askyesno("確認", "この表示項目を削除してもよろしいですか？"):
            entry_vars['frame'].destroy()
            self.modal_field_entries.remove(entry_vars)
            self.update_add_field_button()

    def move_modal_field_up(self, entry_vars):
        """項目を上に移動"""
        index = self.modal_field_entries.index(entry_vars)
        if index > 0:
            # Swap in list
            self.modal_field_entries[index], self.modal_field_entries[index-1] = self.modal_field_entries[index-1], self.modal_field_entries[index]
            # Refresh display
            self.refresh_modal_fields()

    def move_modal_field_down(self, entry_vars):
        """項目を下に移動"""
        index = self.modal_field_entries.index(entry_vars)
        if index < len(self.modal_field_entries) - 1:
            # Swap in list
            self.modal_field_entries[index], self.modal_field_entries[index+1] = self.modal_field_entries[index+1], self.modal_field_entries[index]
            # Refresh display
            self.refresh_modal_fields()

    def refresh_modal_fields(self):
        """ポップアップ表示項目の表示を更新"""
        # Save current values
        saved_entries = []
        for entry_vars in self.modal_field_entries:
            saved_entries.append({
                'display_name': entry_vars['display_name'].get(),
                'csv_field': entry_vars['csv_field'].get(),
                'enabled': entry_vars['enabled'].get()
            })
        
        # Clear and recreate
        for widget in self.modal_fields_container.winfo_children():
            widget.destroy()
        self.modal_field_entries = []
        
        for entry_data in saved_entries:
            self.add_modal_field_entry(
                entry_data['display_name'],
                entry_data['csv_field'], 
                entry_data['enabled']
            )

    def setup_data_split_tab(self):
        """データ分割設定タブのセットアップ"""
        self.data_split_entries = []
        
        # 説明テキスト
        description_text = """
データ分割設定
特定の会議室の予約データを複数の会議室にコピーして表示することができます。
例：「ホール全」の予約を「ホールⅠ」と「ホールⅡ」の両方に表示する
        """
        
        tk.Label(self.data_split_frame, text=description_text.strip(), 
                justify='left', wraplength=600).pack(pady=10, padx=10, anchor='w')
        
        # ヘッダー
        header_frame = tk.Frame(self.data_split_frame)
        header_frame.pack(pady=5, padx=10, fill='x')
        
        tk.Label(header_frame, text="有効", font=('TkDefaultFont', 10, 'bold')).pack(side='left', padx=(0, 20))
        tk.Label(header_frame, text="元会議室", font=('TkDefaultFont', 10, 'bold')).pack(side='left', padx=(0, 20))
        tk.Label(header_frame, text="コピー先会議室", font=('TkDefaultFont', 10, 'bold')).pack(side='left', padx=(0, 20))
        tk.Label(header_frame, text="説明", font=('TkDefaultFont', 10, 'bold')).pack(side='left', padx=(0, 20))
        tk.Label(header_frame, text="操作", font=('TkDefaultFont', 10, 'bold')).pack(side='left')
        
        # 既存のルールを表示
        existing_rules = self.config.get('data_split_rules', [])
        for rule in existing_rules:
            self.add_data_split_entry(rule)
        
        # デフォルトルールがない場合はサンプルを追加
        if not existing_rules:
            default_rule = {
                "source_room_id": "hall-combined",
                "target_room_ids": ["hall-1", "hall-2"],
                "enabled": True,
                "description": "ホール全の予約をホールⅠとホールⅡにコピー"
            }
            self.add_data_split_entry(default_rule)
        
        # 追加ボタン
        add_button_frame = tk.Frame(self.data_split_frame)
        add_button_frame.pack(pady=10, fill='x')
        tk.Button(add_button_frame, text="分割ルールを追加", 
                command=self.add_new_data_split_entry).pack()

    def add_data_split_entry(self, rule_data=None):
        """データ分割エントリを追加"""
        if rule_data is None:
            rule_data = {
                "source_room_id": "",
                "target_room_ids": [],
                "enabled": False,
                "description": ""
            }
        
        entry_frame = tk.Frame(self.data_split_frame, relief='raised', bd=1)
        entry_frame.pack(pady=2, padx=10, fill='x')
        
        # 有効/無効チェックボックス
        enabled_var = tk.BooleanVar(value=rule_data.get('enabled', False))
        tk.Checkbutton(entry_frame, variable=enabled_var).pack(side='left', padx=(5, 20))
        
        # 元会議室選択
        room_ids = [room['id'] for room in self.config.get('rooms', [])]
        room_options = ["-- 選択 --"] + room_ids
        
        source_room_var = tk.StringVar()
        source_room_var.set(rule_data.get('source_room_id', "-- 選択 --"))
        source_menu = ttk.OptionMenu(entry_frame, source_room_var, 
                                    source_room_var.get(), *room_options)
        source_menu.pack(side='left', padx=(0, 20))
        
        # コピー先会議室選択（複数選択可能）
        target_frame = tk.Frame(entry_frame)
        target_frame.pack(side='left', padx=(0, 20))
        
        target_room_vars = {}
        target_room_ids = rule_data.get('target_room_ids', [])
        
        for room_id in room_ids:
            if room_id != rule_data.get('source_room_id'):  # 元会議室は除外
                var = tk.BooleanVar(value=room_id in target_room_ids)
                room_name = next((r['display_name'] for r in self.config.get('rooms', []) 
                                if r['id'] == room_id), room_id)
                cb = tk.Checkbutton(target_frame, text=room_name, variable=var)
                cb.pack(anchor='w')
                target_room_vars[room_id] = var
        
        # 説明テキスト
        description_var = tk.StringVar(value=rule_data.get('description', ''))
        description_entry = tk.Entry(entry_frame, textvariable=description_var, width=30)
        description_entry.pack(side='left', padx=(0, 20))
        
        # 削除ボタン
        delete_button = tk.Button(entry_frame, text="削除", fg='red',
                                command=lambda: self.remove_data_split_entry(entry_frame, rule_vars))
        delete_button.pack(side='left', padx=5)
        
        # エントリ情報を保存
        rule_vars = {
            'frame': entry_frame,
            'enabled': enabled_var,
            'source_room': source_room_var,
            'target_rooms': target_room_vars,
            'description': description_var
        }
        
        self.data_split_entries.append(rule_vars)
        
    def add_new_data_split_entry(self):
        """新しいデータ分割エントリを追加"""
        self.add_data_split_entry()
        
    def remove_data_split_entry(self, frame, rule_vars):
        """データ分割エントリを削除"""
        if messagebox.askyesno("確認", "この分割ルールを削除してもよろしいですか？"):
            frame.destroy()
            self.data_split_entries.remove(rule_vars)


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditorApp(root)
    root.mainloop()
