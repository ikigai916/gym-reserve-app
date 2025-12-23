# Secret Managerの使用方法

このドキュメントでは、Secret Managerを使用してシークレットをCloud Runサービスに渡す方法を説明します。

## 方法1: Cloud Runの環境変数としてシークレットをマウント（推奨）

Secret ManagerのシークレットをCloud Runサービスの環境変数として直接マウントできます。

### 手順

1. **Secret Managerでシークレットを作成**（GCPコンソールで）
   - シークレット名: `DATABASE_URL`
   - シークレット値: `postgresql://user:password@host:5432/dbname`

2. **サービスアカウントにSecret Managerへのアクセス権限を付与**
   - ステップ4で作成したサービスアカウント `github-actions-deploy` に
   - ロール: `Secret Manager シークレット アクセス権` (`roles/secretmanager.secretAccessor`)
   - （既に付与済みの場合があります）

3. **Cloud Runサービスにシークレットをマウント**

   `.github/workflows/deploy.yml` のデプロイステップで `--update-secrets` オプションを追加:

   ```yaml
   gcloud run deploy ${{ env.SERVICE_NAME }} \
     --image ${{ env.IMAGE }} \
     --region ${{ env.REGION }} \
     --update-secrets="DATABASE_URL=DATABASE_URL:latest" \
     # ... 他のオプション
   ```

   **構文**: `環境変数名=シークレット名:バージョン`
   - `環境変数名`: Cloud Runサービス内で使用する環境変数名
   - `シークレット名`: Secret Managerで作成したシークレット名
   - `バージョン`: `latest`（最新版）または特定のバージョン番号

4. **複数のシークレットを設定する場合**

   ```yaml
   --update-secrets="DATABASE_URL=DATABASE_URL:latest,API_KEY=API_KEY:latest,STRIPE_SECRET=STRIPE_SECRET:latest"
   ```

5. **アプリケーションで使用**

   Next.jsアプリケーションでは、環境変数として自動的に利用可能になります:

   ```javascript
   // pages/api/example.js または app/api/example/route.js
   const databaseUrl = process.env.DATABASE_URL;
   ```

## 方法2: デプロイ時にシークレットの値を取得して環境変数に設定

デプロイ時にシークレットの値を取得して、通常の環境変数として設定する方法です。

### 手順

1. **Secret Managerでシークレットを作成**（同上）

2. **ワークフローでシークレットの値を取得**

   `.github/workflows/deploy.yml` に以下を追加:

   ```yaml
   - name: Get secrets from Secret Manager
     run: |
       DATABASE_URL=$(gcloud secrets versions access latest --secret="DATABASE_URL")
       echo "DATABASE_URL=$DATABASE_URL" >> $GITHUB_ENV
   
   - name: Deploy to Cloud Run
     run: |
       gcloud run deploy ${{ env.SERVICE_NAME }} \
         --set-env-vars="DATABASE_URL=${{ env.DATABASE_URL }}" \
         # ... 他のオプション
   ```

   **注意**: この方法では、シークレットの値がGitHub Actionsのログに表示される可能性があります。
   方法1（マウント）の方が安全です。

## 方法1と方法2の比較

| 項目 | 方法1（マウント） | 方法2（値取得） |
|------|------------------|----------------|
| セキュリティ | 高い（値がログに表示されない） | 低い（ログに表示される可能性） |
| 更新の容易さ | シークレットを更新すれば自動反映 | 再デプロイが必要 |
| 推奨度 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## トラブルシューティング

### エラー: "Permission denied on secret"

- サービスアカウントに `Secret Manager シークレット アクセス権` ロールが付与されているか確認
- シークレット名が正しいか確認
- シークレットが存在するか確認

### エラー: "Secret not found"

- Secret Managerでシークレットが作成されているか確認
- シークレット名のタイポがないか確認
- プロジェクトIDが正しいか確認

## 参考リンク

- [Secret Manager のドキュメント](https://cloud.google.com/secret-manager/docs)
- [Cloud Run でのシークレットの使用](https://cloud.google.com/run/docs/configuring/secrets)

