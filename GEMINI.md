# GEMINI.md

## プロジェクト概要

このプロジェクトは、会議室の予約状況をローカル環境で確認するためのWebアプリケーションです。Pythonベースで構築されており、指定されたフォルダに置かれたCSV形式の予約情報を自動的に処理し、Webブラウザ上のカレンダーに表示します。

**主要技術:**

*   **バックエンド:** Python, Flask
*   **フロントエンド:** HTML, Tailwind CSS, Vanilla JavaScript
*   **データ処理:** pandas

**アーキテクチャ:**

アプリケーションは、Webサーバーとファイル監視の役割を担う単一のPythonスクリプト (`server_fixed.py`) で構成されています。このスクリプトが、フロントエンドの全機能を含む単一のHTMLファイル (`index.html`) を提供します。バックエンドとフロントエンドはREST APIを介して通信します。

## ビルドと実行

**前提条件:**

*   Python 3.7以上

**インストール:**

1.  必要なPythonパッケージをインストールします。
    ```bash
    pip install -r requirements.txt
    ```

**アプリケーションの実行:**

1.  サーバーを起動します。
    ```bash
    python server_fixed.py
    ```
2.  Webブラウザを開き、 `http://localhost:5003` にアクセスします。

**テスト:**

このプロジェクトには `test_system.py` と `test_system_simple.py` の2つのテストファイルが含まれています。テストを実行するには、以下のコマンドを実行してください。

```bash
python test_system.py
```

```bash
python test_system_simple.py
```

## 開発規約

*   **コーディングスタイル:** Pythonコードは基本的にPEP 8スタイルガイドラインに準拠しています。
*   **フロントエンド:** フロントエンドは、Vanilla JavaScriptで書かれたシングルページアプリケーションです。スタイリングにはTailwind CSSを使用しています。
*   **API:** バックエンドは、フロントエンドが利用するためのシンプルなREST APIを提供します。
*   **設定:** アプリケーションの設定は `config.json` ファイルで行います。GUI設定エディタ (`config_editor.pyw`) も提供されています。
*   **依存関係:** Pythonの依存関係は `requirements.txt` ファイルで管理されています。
