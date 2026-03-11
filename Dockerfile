# Python 3.12.3 slim版
FROM python:3.12.3-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# プロジェクト全体をコピー
COPY . .

# Streamlitで起動
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]
