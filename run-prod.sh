#!/bin/bash
set -e

# WatchMe Admin - 本番デプロイスクリプト
echo "🚀 Starting WatchMe Admin deployment..."

# 変数設定
AWS_REGION="ap-southeast-2"
AWS_ACCOUNT_ID="754724220380"
ECR_REPOSITORY="watchme-admin"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# ECRから最新イメージをプル
echo "📥 Pulling latest image from ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest

# 既存コンテナを停止して削除
echo "🛑 Stopping existing containers..."

# 1. 実行中のすべてのwatchme-adminコンテナを検索して停止
echo "   Checking for running containers..."
RUNNING_CONTAINERS=$(docker ps -q --filter "name=watchme-admin")
if [ ! -z "$RUNNING_CONTAINERS" ]; then
    echo "   Found running containers: $RUNNING_CONTAINERS"
    docker stop $RUNNING_CONTAINERS
    echo "   ✅ Stopped running containers"
else
    echo "   No running containers found"
fi

# 2. 停止済みも含めて、すべてのwatchme-adminコンテナを削除
echo "   Checking for existing containers..."
ALL_CONTAINERS=$(docker ps -aq --filter "name=watchme-admin")
if [ ! -z "$ALL_CONTAINERS" ]; then
    echo "   Found existing containers: $ALL_CONTAINERS"
    docker rm -f $ALL_CONTAINERS
    echo "   ✅ Removed existing containers"
else
    echo "   No existing containers found"
fi

# 3. docker-composeで管理されているコンテナも確実に停止
echo "   Stopping docker-compose managed containers..."
docker-compose -f docker-compose.prod.yml down || true

# コンテナを起動
echo "🚀 Starting new container..."
# 必要に応じてコンテナを再作成
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# 起動確認
echo "⏳ Waiting for container to start..."
sleep 5

# コンテナの状態確認
echo "📊 Container status:"
docker ps | grep watchme-admin || (echo "❌ Container not running!" && exit 1)

# ヘルスチェック（トップページにアクセス）
echo "🏥 Running health check..."
if curl -f http://localhost:9000/ -o /dev/null -s; then
    echo "✅ Health check passed!"
    echo "🎉 WatchMe Admin is running successfully!"
    echo "🌐 Access at: https://admin.hey-watch.me/"
else
    echo "❌ Health check failed!"
    docker logs watchme-admin --tail 50
    exit 1
fi