# システムアーキテクチャ

---

# 構成

ブラウザ  
↓  
Streamlitアプリ  
↓  
Google Sheets（データ保存）  
↓  
Cloudinary（画像保存）

---

# アプリ構成

Streamlit pages 機能を利用する。

pages

- dashboard.py
- members.py
- cleaning.py
- payments.py
- items.py
- albums.py
- announcements.py
- boards.py
- rules.py
- admin.py

---

# 認証

簡易ログイン方式。

Google Sheets の members シートを利用する。

role

- admin
- member

---

# 権限制御

admin

- 全機能アクセス可能

member

- 閲覧中心

---

# 多言語

翻訳ファイルを利用する。

locales

- ja.json
- en.json
- id.json
- my.json

---

# デプロイ

Streamlit Community Cloud

GitHubと連携して公開する。

---

# SaaS化設計

将来的に複数寮対応するため  
すべてのデータに以下カラム追加可能。

tenant_id
