# 運用手順書 (OPERATIONS)

## 1. ローカル開発運用
詳細は `docs/development/DOCKER_USAGE.md` を参照。

### 基本コマンド
- **起動**: `docker run` (認証マウント必須)
- **停止・削除**: `docker rm -f reseve-container`

## 2. デプロイ手順 (Google Cloud Run)
詳細は `docs/deployment/DEPLOYMENT.md` を参照。

### CI/CD フロー
1. main ブランチへプッシュ。
2. GitHub Actions が起動。
3. Artifact Registry へビルド済みイメージをプッシュ。
4. Cloud Run サービスを更新。

### 手動デプロイ (緊急時)
```bash
gcloud builds submit --tag asia-northeast1-docker.pkg.dev/[PROJECT_ID]/docker-repo/reseve-app
gcloud run deploy gym-reserve-app --image asia-northeast1-docker.pkg.dev/[PROJECT_ID]/docker-repo/reseve-app --region asia-northeast1
```

## 3. 権限管理 (IAM)
Cloud Run サービスアカウントには以下のロールが必要です。
- `roles/datastore.user` (Firestore への読み書き)
- `roles/logging.logWriter` (ログ出力)

## 4. トラブル時の初動
1. **Google Cloud 認証の確認**: 「処置中...」から動かない、または `RefreshError` が出ている場合は `gcloud auth application-default login` を実行。
2. **GitHub Actions の確認**: デプロイが失敗していないか？
3. **Cloud Run ログの確認**: アプリケーションエラーが出ていないか？
4. **Firestore コンソールの確認**: データが正しく保存されているか？

