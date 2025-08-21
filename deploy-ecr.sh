#!/bin/bash

# ECRデプロイスクリプト - watchme-admin
# このスクリプトはDockerイメージをビルドしてAWS ECRにプッシュします

set -e

echo "🚀 WatchMe Admin ECRデプロイ開始..."

# 変数設定
AWS_REGION="ap-southeast-2"
AWS_ACCOUNT_ID="754724220380"
ECR_REPOSITORY="watchme-admin"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

# 1. AWS ECRにログイン
echo "📝 ECRにログイン中..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# 2. Dockerイメージをビルド
echo "🔨 Dockerイメージをビルド中..."
docker build -t ${ECR_REPOSITORY} .

# 3. イメージにタグを付ける
echo "🏷️ イメージにタグ付け中..."
docker tag ${ECR_REPOSITORY}:latest ${ECR_URI}:latest
docker tag ${ECR_REPOSITORY}:latest ${ECR_URI}:$(date +%Y%m%d-%H%M%S)

# 4. ECRにプッシュ
echo "📤 ECRにプッシュ中..."
docker push ${ECR_URI}:latest
docker push ${ECR_URI}:$(date +%Y%m%d-%H%M%S)

echo "✅ ECRへのデプロイが完了しました！"
echo "📍 イメージURI: ${ECR_URI}:latest"
echo ""
echo "次のステップ:"
echo "1. EC2サーバーにSSH接続: ssh -i ~/watchme-key.pem ubuntu@3.24.16.82"
echo "2. 既存コンテナを停止: sudo docker stop watchme-admin"
echo "3. 既存コンテナを削除: sudo docker rm watchme-admin"
echo "4. 新しいイメージをプル: sudo docker-compose -f /home/ubuntu/watchme-admin/docker-compose.prod.yml pull"
echo "5. コンテナを起動: sudo docker-compose -f /home/ubuntu/watchme-admin/docker-compose.prod.yml up -d"