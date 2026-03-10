# PERMISSION_SPEC.md

# 権限仕様

本アプリには以下の2つのユーザーロールが存在する。

- admin
- member

権限は Google Sheets の members シートの role カラムで管理する。

---

# admin

寮管理者。

すべての機能にアクセス可能。

利用可能機能

- ダッシュボード閲覧
- メンバー管理
- 掃除当番管理
- 集金管理
- 物品管理
- アルバム投稿
- お知らせ投稿
- 掲示板投稿
- 規約編集

---

# member

寮メンバー。

管理機能にはアクセスできない。

利用可能機能

- ダッシュボード閲覧
- 掃除当番確認
- 集金状況確認
- 物品一覧閲覧
- アルバム閲覧・投稿
- 掲示板投稿
- お知らせ閲覧
- 規約閲覧

---

# アクセス制御

admin のみアクセス可能なページ

- admin.py
- members.py
- payments.py
- items.py

member は閲覧のみ

- cleaning.py
- announcements.py
- boards.py
- albums.py
- rules.py

---

# UI制御

admin ユーザーのみ以下ボタンを表示する

- メンバー追加
- 集金作成
- 物品追加
- お知らせ投稿
- 規約編集

member には表示しない。

---

# 認証

ログイン時に members シートからユーザーを検索する。

一致するユーザーが存在する場合ログイン成功。

ユーザー情報

- id
- name
- email
- role

を session_state に保存する。

---

# セッション管理

ログイン成功後

session_state.user

にユーザー情報を保存する。

例

session_state.user = {
  "id": "1",
  "name": "Taro",
  "role": "admin"
}

role によって画面表示を制御する。
