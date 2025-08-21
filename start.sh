#!/bin/bash

# シンプル管理画面起動スクリプト

echo "🚀 WatchMe シンプル管理画面を起動します..."

# 仮想環境のアクティベート（既存の場合）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 依存関係のインストール
pip3 install -r requirements.txt

# サーバー起動
echo "📡 サーバーを起動中..."
echo "🌐 ブラウザで http://localhost:9000 にアクセスしてください"
python3 main.py