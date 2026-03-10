# Google Sheets データスキーマ

このアプリは Google Sheets をデータベースとして利用する。

各機能ごとにシートを作成する。

---

# members

メンバー情報

columns

- id
- name
- room
- phone
- email
- role
- join_date

role

- admin
- member

---

# cleaning_tasks

掃除当番

columns

- id
- member_id
- location
- start_date
- end_date
- status

status

- pending
- done

---

# payments

集金

columns

- id
- title
- amount
- due_date
- description

---

# payment_status

支払い状況

columns

- id
- payment_id
- member_id
- paid

paid

- true
- false

---

# items

物品管理

columns

- id
- name
- quantity
- location
- status

---

# albums

アルバム投稿

columns

- id
- title
- description
- image_url
- author_id
- created_at

image_url は Cloudinary のURLを保存する。

---

# announcements

お知らせ

columns

- id
- title
- content
- author_id
- created_at

---

# boards

掲示板投稿

columns

- id
- title
- content
- author_id
- created_at

---

# comments

掲示板コメント

columns

- id
- board_id
- author_id
- content
- created_at

---

# rules

寮規約

columns

- id
- title
- content
- updated_at
