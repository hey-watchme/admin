# WatchMe Admin デプロイ手順書

## 概要
このドキュメントは、リニューアルしたWatchMe管理画面を本番環境（EC2）にデプロイする手順を説明します。

## 前提条件
- AWS ECRにDockerイメージがプッシュ済み
- EC2サーバーへのSSHアクセス権限
- 本番環境のSupabase接続情報

## デプロイ手順

### 1. ローカルでのイメージビルドとECRプッシュ

```bash
# adminディレクトリに移動
cd /Users/kaya.matsumoto/projects/watchme/admin

# ECRデプロイスクリプトを実行
./deploy-ecr.sh
```

### 2. 必要なファイルを本番サーバーへ転送

```bash
# docker-compose.prod.ymlを転送
scp -i ~/watchme-key.pem docker-compose.prod.yml ubuntu@3.24.16.82:/home/ubuntu/admin/

# .envファイルが無い場合は環境変数の設定が必要
```

### 3. EC2サーバーでの作業

#### 3-1. サーバーにSSH接続

```bash
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82
```

#### 3-2. 既存のコンテナを停止・削除

```bash
# adminディレクトリに移動
cd /home/ubuntu/admin

# 現在のコンテナ状態を確認
docker ps | grep admin

# 既存のコンテナを停止
docker stop watchme-admin

# 既存のコンテナを削除
docker rm watchme-admin

# 古いイメージを削除（オプション）
docker images | grep admin
docker rmi admin-admin:latest
```

#### 3-3. ECRから新しいイメージをプル

```bash
# ECRにログイン
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com

# 新しいイメージをプル
docker-compose -f docker-compose.prod.yml pull
```

#### 3-4. 新しいコンテナを起動

```bash
# docker-compose.prod.ymlを使用して起動
docker-compose -f docker-compose.prod.yml up -d

# 起動確認
docker ps | grep admin

# ログ確認
docker logs watchme-admin --tail 50
```

#### 3-5. systemdサービスの更新（必要に応じて）

```bash
# systemdサービスファイルを更新
sudo nano /etc/systemd/system/watchme-admin.service

# 以下の内容に更新:
# ExecStartPre=/usr/bin/docker-compose -f docker-compose.prod.yml pull
# ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
# ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down

# systemdをリロード
sudo systemctl daemon-reload

# サービスを再起動
sudo systemctl restart watchme-admin.service

# サービス状態を確認
sudo systemctl status watchme-admin.service
```

### 4. 動作確認

#### 4-1. 内部から確認

```bash
# EC2サーバー内から確認
curl http://localhost:9000/
```

#### 4-2. 外部から確認

ブラウザで以下のURLにアクセス:
- https://admin.hey-watch.me/

### 5. トラブルシューティング

#### ポート9000が使用中の場合

```bash
# 使用中のプロセスを確認
lsof -i :9000

# プロセスを強制終了
kill -9 <PID>
```

#### コンテナが起動しない場合

```bash
# コンテナのログを確認
docker logs watchme-admin

# 環境変数を確認
cat .env

# docker-compose設定を確認
docker-compose -f docker-compose.prod.yml config
```

#### ロールバック手順

問題が発生した場合、以前のイメージに戻す:

```bash
# 現在のコンテナを停止・削除
docker stop watchme-admin
docker rm watchme-admin

# 以前のdocker-compose.ymlを使用
docker-compose up -d
```

## 重要な注意事項

1. **環境変数**: 本番環境の`.env`ファイルに正しいSupabase接続情報が設定されていることを確認
2. **ネットワーク**: コンテナが`watchme-network`に接続されていることを確認
3. **ログ**: `/home/ubuntu/admin/logs`ディレクトリにログが出力される
4. **バックアップ**: 既存の設定ファイルは必ずバックアップを取る

## ECRイメージ情報

- **リポジトリURI**: `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-admin`
- **リージョン**: `ap-southeast-2`
- **タグ**: `latest`および日付タグ（例：`20250821-182110`）

## 更新履歴

- 2025-08-21: 初版作成 - 完全リニューアル版のデプロイ手順