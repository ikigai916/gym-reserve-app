# Cloud RunからFirestoreへのアクセス権限設定

## 問題

Cloud RunにデプロイしたアプリケーションがFirestoreにアクセスできず、500エラーが発生する場合、サービスアカウントに適切な権限が付与されていない可能性があります。

## 解決方法

### ステップ1: Cloud Runのサービスアカウントを確認

1. [GCPコンソール](https://console.cloud.google.com/)にアクセス
2. 左メニュー → 「**Cloud Run**」をクリック
3. サービス一覧から「**gym-reserve-app**」をクリック
4. 「**修正と新しいリビジョンのデプロイ**」タブをクリック
5. 「**YAML**」タブをクリックして、`spec.serviceAccountName`を確認
   - 設定されていない場合、デフォルトのサービスアカウント（`PROJECT_NUMBER-compute@developer.gserviceaccount.com`）が使用されます
   - カスタムサービスアカウントが設定されている場合は、そのメールアドレスをメモしてください

### ステップ2: サービスアカウントにFirestore権限を付与

#### 方法1: IAMと管理から設定（推奨）

1. GCPコンソール → 左メニュー → 「**IAMと管理**」→「**IAM**」
2. サービスアカウントのメールアドレスを検索（または一覧から探す）
3. 行の右側にある「**鉛筆アイコン（編集）**」をクリック
4. 「**ロールを追加**」をクリック
5. 以下のロールを追加：
   - **Cloud Datastore User** (`roles/datastore.user`)
6. 「**保存**」をクリック

#### 方法2: gcloudコマンドで設定

デフォルトのサービスアカウントを使用している場合：

```bash
PROJECT_ID="gym-reserve-app"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/datastore.user"
```

カスタムサービスアカウントを使用している場合：

```bash
PROJECT_ID="gym-reserve-app"
SERVICE_ACCOUNT="your-service-account@gym-reserve-app.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/datastore.user"
```

### ステップ3: 動作確認

権限を付与した後、以下を確認：

1. Cloud Runサービスのログを確認：
   - Cloud Runサービス詳細ページ → 「**ログ**」タブ
   - エラーメッセージに「Permission denied」が表示されなくなっているか確認

2. アプリケーションを再テスト：
   - ログインページでユーザーを作成してみる
   - 500エラーが解消されているか確認

## 必要なロール

Cloud RunからFirestoreにアクセスするには、以下のロールが必要です：

- **Cloud Datastore User** (`roles/datastore.user`)
  - Firestoreへの読み書きアクセスを許可します

## トラブルシューティング

### 権限が反映されない場合

- 権限の反映には数分かかる場合があります
- Cloud Runサービスを再デプロイしてみてください
- IAMポリシーの変更が反映されているか確認してください

### その他のエラー

- Firestoreデータベースが作成されているか確認
- Firestore APIが有効化されているか確認
- セキュリティルールが適切に設定されているか確認（開発環境では一時的に全許可が可能）

