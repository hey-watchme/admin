# WatchMe 管理画面

シンプルで軽量な管理画面システムです。通知管理とデータベース管理に特化しています。

📍 **本番環境URL**: https://admin.hey-watch.me/  
🐳 **Dockerイメージ**: AWS ECR (`754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-admin`)

## 🎯 概要

WatchMe管理画面は、ユーザー、デバイス、通知を効率的に管理するためのWebインターフェースです。
APIマネージャーと連携し、データベースの基本的なCRUD操作を提供します。

## ✨ 主な機能

### 🔔 通知管理（トップページ）
- 通知の一覧表示（ページネーション対応）
- 新規通知の作成（グローバル通知・イベント通知の分離対応）
  - **グローバル通知**: 全ユーザーに一斉配信（user_id = null, type = 'global'）
  - **イベント通知**: 特定ユーザーに配信（user_id必須, type = 'event'）
- 既読/未読の管理
- 通知の削除
- リアルタイム統計表示

### 💾 データベース管理
#### 👥 ユーザー管理
- ユーザー一覧の表示
- ユーザー情報の編集・削除
- ステータス管理（guest/member/subscriber）
- サブスクリプションプラン管理

#### 🎤 デバイス管理
- デバイス一覧の表示
- デバイス情報の編集・削除
- デバイスステータス管理（active/inactive/syncing/error）
- 音声データ収集統計

## 📋 必要な環境

- Python 3.8以上
- Supabaseアカウント（データベース接続用）
- 環境変数設定（.envファイル）

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
cd /Users/kaya.matsumoto/projects/watchme/admin
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定：

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
PORT=9000
```

### 3. 仮想環境のセットアップ

```bash
# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 4. サーバーの起動

```bash
# 開発環境での起動（自動リロード有効）
python3 main.py

# またはバックグラウンドで起動
nohup python3 main.py > server.log 2>&1 &
```

### 5. アクセス

ブラウザで http://localhost:9000 にアクセス

## 📁 ディレクトリ構成

```
admin/
├── main.py              # FastAPIアプリケーションのメインファイル
├── api/
│   └── supabase_client.py  # Supabaseクライアント
├── templates/           # HTMLテンプレート
│   ├── base.html       # ベーステンプレート
│   ├── index.html      # 通知管理（トップページ）
│   ├── users.html      # ユーザー管理ページ
│   └── devices.html    # デバイス管理ページ
├── static/             # 静的ファイル（CSS、JS、画像）
├── venv/               # Python仮想環境
├── requirements.txt    # Python依存関係
├── server.log         # サーバーログ
├── .env               # 環境変数（要作成）
└── README.md          # このファイル
```

## 🔌 API エンドポイント

### 統計情報
| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/api/stats` | システム全体の統計情報を取得 |

### 通知管理
| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/api/notifications` | 通知一覧（ページネーション対応） |
| POST | `/api/notifications` | 新規通知作成 |
| PUT | `/api/notifications/{id}/read` | 通知を既読にする |
| DELETE | `/api/notifications/{id}` | 通知を削除 |

### ユーザー管理
| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/api/users` | ユーザー一覧（ページネーション対応） |
| POST | `/api/users` | 新規ユーザー作成 |
| PUT | `/api/users/{id}` | ユーザー情報更新 |
| DELETE | `/api/users/{id}` | ユーザー削除 |

### デバイス管理
| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/api/devices` | デバイス一覧（ページネーション対応） |
| POST | `/api/devices` | 新規デバイス登録 |
| PUT | `/api/devices/{id}` | デバイス情報更新 |
| DELETE | `/api/devices/{id}` | デバイス削除 |

## 🛠️ 開発

### ローカル開発の起動

```bash
# 仮想環境を有効化
source venv/bin/activate

# バックグラウンドで起動（推奨）
nohup python3 main.py > server.log 2>&1 &

# フォアグラウンドで起動（デバッグ時）
python3 main.py
```

### 依存関係

主要なPythonパッケージ：
- `fastapi==0.104.1` - Webフレームワーク
- `uvicorn[standard]==0.24.0` - ASGIサーバー
- `python-dotenv==1.0.0` - 環境変数管理
- `httpx>=0.26,<0.29` - HTTPクライアント
- `jinja2==3.1.2` - テンプレートエンジン

### ログの確認

```bash
# リアルタイムログ監視
tail -f server.log

# 最新のログ20行を表示
tail -n 20 server.log
```

### プロセス管理

```bash
# 実行中のプロセスを確認
ps aux | grep "python3 main.py"

# プロセスを停止
kill <PID>

# ポート9000を使用しているプロセスを確認
lsof -i :9000
```

## 🐛 トラブルシューティング

### ポート9000が使用中の場合

```bash
# 使用中のプロセスを確認
lsof -i :9000

# プロセスを強制終了
kill -9 <PID>
```

### ModuleNotFoundError

```bash
# 仮想環境が有効化されているか確認
which python3
# 出力が venv/bin/python3 でない場合は再度有効化
source venv/bin/activate

# 依存関係を再インストール
pip install -r requirements.txt
```

### データベース接続エラー

1. `.env`ファイルが存在することを確認
2. `SUPABASE_URL`と`SUPABASE_KEY`が正しく設定されているか確認
3. Supabaseプロジェクトがアクティブであることを確認

### 仮想環境のリセット

```bash
# 仮想環境を削除して再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📝 使用方法

### 通知の作成

1. トップページの「➕ 新規通知」ボタンをクリック
2. 通知の種類を選択
   - 🌍 **グローバル通知**：全員に配信（user_id不要）
   - 👤 **イベント通知**：個人に配信（user_id必須）
3. 選択した種類に応じてフォームが動的に変化
4. タイトルとメッセージを入力
5. 「作成」ボタンをクリック

#### 通知タイプの仕様
| 種類 | user_id | type値 | triggered_by | 説明 |
|------|---------|--------|--------------|------|
| グローバル通知 | null | 'global' | 'manual' | 全ユーザーに一斉配信 |
| イベント通知 | 必須 | 'event' | 'manual' | 特定ユーザーに配信 |

### ユーザー管理

1. ナビゲーションバーの「データベース管理」→「ユーザー管理」を選択
2. ユーザー一覧が表示される
3. 各ユーザーの「編集」または「削除」ボタンで操作

### デバイス管理

1. ナビゲーションバーの「データベース管理」→「デバイス管理」を選択
2. デバイス一覧が表示される
3. デバイスステータスや音声データ数を確認

## 🚀 デプロイ（CI/CD自動化済み）

### 概要

**2025年9月よりGitHub Actionsを使用した完全自動CI/CDに移行しました。**

mainブランチにプッシュするだけで自動デプロイが実行されます。

### 🎯 自動デプロイフロー

1. **コードをプッシュ**
   ```bash
   git add .
   git commit -m "your changes"
   git push origin main
   ```

2. **GitHub Actionsが自動実行** 🤖
   - Dockerイメージをビルド
   - AWS ECRにプッシュ
   - EC2サーバーに自動デプロイ
   - 環境変数を自動設定
   - コンテナを再起動

3. **デプロイ完了** ✅
   - https://admin.hey-watch.me/ で新バージョンが稼働

### 🔧 CI/CD設定

#### GitHub Actionsワークフロー
- **ファイル**: `.github/workflows/deploy-to-ecr.yml`
- **トリガー**: mainブランチへのプッシュ
- **処理時間**: 約3-5分

#### 必要なGitHub Secrets（設定済み）
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `EC2_HOST`
- `EC2_SSH_PRIVATE_KEY`
- `EC2_USER`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Docker構成

本番環境はDocker化されており、AWS ECRからイメージを取得して実行します。

#### 必要なファイル

- `Dockerfile`: FastAPIアプリケーションのコンテナ化
- `docker-compose.prod.yml`: 本番環境用のDocker Compose設定
- `.dockerignore`: ビルド時の除外ファイル設定
- `deploy-ecr.sh`: ECRへのデプロイスクリプト

### 🔍 デプロイ状況の確認

1. **GitHub Actionsの状態確認**
   ```
   https://github.com/hey-watchme/admin/actions
   ```

2. **コンテナログの確認**（必要時）
   ```bash
   ssh -i ~/watchme-key.pem ubuntu@3.24.16.82
   docker logs watchme-admin --tail 50
   ```

### 🔄 手動デプロイ手順（緊急時のみ）

#### 1. ローカルでのイメージビルドとECRプッシュ

```bash
# adminディレクトリに移動
cd /Users/kaya.matsumoto/projects/watchme/admin

# ECRデプロイスクリプトを実行
./deploy-ecr.sh
```

#### 2. 本番サーバーへの設定ファイル転送

```bash
# docker-compose.prod.ymlを転送
scp -i ~/watchme-key.pem docker-compose.prod.yml ubuntu@3.24.16.82:/home/ubuntu/admin/
```

#### 3. EC2サーバーでの作業

```bash
# サーバーにSSH接続
ssh -i ~/watchme-key.pem ubuntu@3.24.16.82

# adminディレクトリに移動
cd /home/ubuntu/admin

# 既存のコンテナを停止・削除
docker stop watchme-admin
docker rm watchme-admin

# ECRにログイン
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 754724220380.dkr.ecr.ap-southeast-2.amazonaws.com

# 新しいイメージをプル
docker-compose -f docker-compose.prod.yml pull

# コンテナを起動
docker-compose -f docker-compose.prod.yml up -d

# 起動確認
docker ps | grep admin
docker logs watchme-admin --tail 50
```

#### 4. 動作確認

```bash
# サーバー内から確認
curl http://localhost:9000/

# 外部から確認（ブラウザ）
# https://admin.hey-watch.me/
```

### systemdサービス管理

本番環境ではsystemdで自動起動が設定されています：

```bash
# サービス状態確認
sudo systemctl status watchme-admin.service

# サービス再起動
sudo systemctl restart watchme-admin.service

# ログ確認
journalctl -u watchme-admin.service -f
```

### ECR情報

- **リポジトリURI**: `754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-admin`
- **リージョン**: `ap-southeast-2`
- **タグ管理**: `latest`と日付タグ（例：`20250821-182110`）

### トラブルシューティング

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

```bash
# 現在のコンテナを停止・削除
docker stop watchme-admin
docker rm watchme-admin

# 以前のバージョンを指定して起動（タグを指定）
docker run -d --name watchme-admin \
  -p 9000:9000 \
  --env-file .env \
  --network watchme-network \
  754724220380.dkr.ecr.ap-southeast-2.amazonaws.com/watchme-admin:<previous-tag>
```

## 🔒 セキュリティ

- 本番環境では適切な認証機能の追加を推奨
- 環境変数は`.env`ファイルで管理（Gitには含めない）
- データベースの直接操作には十分注意
- ECRイメージは定期的に脆弱性スキャンを実施

## 📄 ライセンス

内部使用のみ

## 📞 サポート

問題が発生した場合は、プロジェクト管理者に連絡してください。

## 📅 更新履歴

### 2025年9月29日
- CI/CDパイプラインを実装（GitHub Actions）
- 既読・未読機能を削除（設計上の問題のため）
- UI改善：「WatchMe Admin」にタイトル統一
- 通知タイプの詳細仕様を文書化
- デプロイプロセスを完全自動化

### 2025年8月23日
- 通知機能をグローバル通知とイベント通知に分離
- 通知作成UIの改善（種類選択による動的フォーム切替）
- バックエンドAPIのバリデーション強化

### 2025年8月21日
- 初期リリース

---

最終更新: 2025年8月23日