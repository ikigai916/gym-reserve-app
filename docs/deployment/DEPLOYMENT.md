# Google Cloud Run デプロイ手順書

このドキュメントでは、Next.jsアプリをGoogle Cloud RunにデプロイするためのCI/CD環境構築手順を説明します。
Workload Identity連携を使用してGitHub Actionsから安全にデプロイします。

## 前提条件

- GCPアカウント（Google Cloud Platform）
- GitHubアカウント
- GCPプロジェクト（新規作成済み）

---

## ステップ1: GCPで必要なAPIを有効化する

### 1-1. GCPコンソールにアクセス
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを選択（または新規作成）

### 1-2. APIライブラリから有効化
1. 左メニューから「**APIとサービス**」→「**ライブラリ**」をクリック
2. 以下のAPIを検索して「**有効にする**」ボタンをクリック：

   **必須API:**
   - **Cloud Run API** (`run.googleapis.com`)
   - **Artifact Registry API** (`artifactregistry.googleapis.com`)
   - **Secret Manager API** (`secretmanager.googleapis.com`)
   - **IAM Service Account Credentials API** (`iamcredentials.googleapis.com`)
   - **Cloud Build API** (`cloudbuild.googleapis.com`)

   **確認方法:**
   - 検索バーで「Cloud Run」と入力 → 選択 → 「有効にする」
   - 同様に他のAPIも有効化

---

## ステップ2: Artifact Registryリポジトリの作成

### 2-1. Artifact Registryに移動
1. 左メニューから「**Artifact Registry**」をクリック
2. 「**リポジトリを作成**」ボタンをクリック

### 2-2. リポジトリ設定
- **名前**: `docker-repo`（任意の名前）
- **形式**: `Docker`
- **モード**: `標準`
- **リージョン**: `asia-northeast1`（東京、任意のリージョン）
- 「**作成**」をクリック

### 2-3. リポジトリのパスを確認
作成後、リポジトリの詳細ページで以下の形式のパスを確認：
```
asia-northeast1-docker.pkg.dev/[PROJECT-ID]/docker-repo
```
（この値は後で使用します）

---

## ステップ3: Secret Managerでシークレットを作成（オプション）

### 3-1. Secret Managerに移動
1. 左メニューから「**Secret Manager**」をクリック
2. 「**シークレットを作成**」をクリック

### 3-2. シークレット設定
- **名前**: `DATABASE_URL`（アプリで使用するシークレット名）
- **シークレット値**: 実際の値（例: `postgresql://...`）
- 「**シークレットを作成**」をクリック

**注意**: この例は参考です。実際のアプリで必要なシークレット（環境変数）を作成してください。

---

## ステップ4: GitHub Actions用のサービスアカウント作成

### 4-1. サービスアカウントの作成
1. 左メニューから「**IAMと管理**」→「**サービスアカウント**」をクリック
2. 「**サービスアカウントを作成**」をクリック
3. 設定を入力：
   - **サービスアカウント名**: `github-actions-deploy`
   - **説明**: `GitHub Actions for Cloud Run deployment`
   - 「**作成して続行**」をクリック

### 4-2. ロールの付与
以下のロールを追加：
1. 「**ロールを選択**」ドロップダウンから以下を追加：
   - `Cloud Run 開発者` (`roles/run.admin`)
   - `Artifact Registry ライター` (`roles/artifactregistry.writer`)
   - `サービスアカウント ユーザー` (`roles/iam.serviceAccountUser`)
   - `Secret Manager シークレット アクセス権` (`roles/secretmanager.secretAccessor`)
   - `Storage オブジェクト作成者` (`roles/storage.objectCreator`) - Cloud Buildで使用

2. 各ロールを追加したら「**続行**」をクリック
3. 「**完了**」をクリック

### 4-3. サービスアカウントのメールアドレスをコピー
作成されたサービスアカウントの一覧から、メールアドレス（例: `github-actions-deploy@[PROJECT-ID].iam.gserviceaccount.com`）をコピーしてメモしてください。

---

## ステップ5: Workload Identity連携の設定

### 5-1. Workload Identityプールの作成
1. 左メニューから「**IAMと管理**」→「**Workload Identity連携**」をクリック
2. 「**プールを作成**」をクリック
3. 設定を入力：
   - **プール名**: `github-actions-pool`
   - **説明**: `Pool for GitHub Actions`
   - 「**続行**」をクリック

### 5-2. プロバイダーの追加
1. 「**プロバイダーを追加**」をクリック
2. 設定を入力：
   - **プロバイダー名**: `github-provider`
   - **プロバイダータイプ**: `OpenID Connect (OIDC)`
   - **属性マッピング**:
     - Google の属性: `attribute.repository` → **値**: `assertion.repository`
     - Google の属性: `attribute.audience` → **値**: `assertion.aud`（任意）
   - **承認済みの対象オーディエンス**: `https://token.actions.githubusercontent.com`
   - 「**続行**」をクリック
3. 「**保存**」をクリック

### 5-3. サービスアカウントへの権限付与
1. 作成したプール `github-actions-pool` をクリック
2. 「**権限を付与**」をクリック
3. 設定を入力：
   - **プリンシパル**: ステップ4-3でコピーしたサービスアカウントのメールアドレス
   - **ロール**: `Workload Identity ユーザー` (`roles/iam.workloadIdentityUser`)
   - 「**保存**」をクリック

### 5-4. Workload Identityプールの完全名をコピー
作成されたプールの詳細ページで、以下の形式の完全名をコピー：
```
projects/[PROJECT-NUMBER]/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider
```

または、GCPコンソールの上部に表示される形式：
```
projects/[PROJECT-ID]/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider
```

**メモ**: `[PROJECT-NUMBER]` と `[PROJECT-ID]` は異なる場合があります。完全名の形式を使用してください。

---

## ステップ6: GitHubリポジトリの設定

### 6-1. GitHub Secretsの設定
1. GitHubリポジトリにアクセス
2. 「**Settings**」→「**Secrets and variables**」→「**Actions**」をクリック
3. 「**New repository secret**」をクリック
4. 以下のシークレットを追加：

   **必須シークレット:**
   - `WORKLOAD_IDENTITY_PROVIDER`: ステップ5-4でコピーしたWorkload Identityプールの完全名
   - `SERVICE_ACCOUNT`: ステップ4-3でコピーしたサービスアカウントのメールアドレス
   - `GCP_PROJECT_ID`: GCPプロジェクトID（例: `my-project-123456`）
   - `GCP_REGION`: 使用するリージョン（例: `asia-northeast1`）
   - `ARTIFACT_REGISTRY_REPO`: Artifact Registryリポジトリ名（例: `docker-repo`）
   - `ARTIFACT_REGISTRY_LOCATION`: Artifact Registryのリージョン（例: `asia-northeast1`）
   - `CLOUD_RUN_SERVICE`: Cloud Runサービス名（例: `nextjs-app`）

### 6-2. GitHub Actionsの有効化
1. GitHubリポジトリの「**Settings**」→「**Actions**」→「**General**」
2. 「**Workflow permissions**」で「**Read and write permissions**」を選択
3. 「**Save**」をクリック

---

## ステップ7: Cloud Runサービスの作成（初回のみ）

### 7-1. Cloud Runに移動
1. 左メニューから「**Cloud Run**」をクリック
2. 「**サービスを作成**」をクリック

### 7-2. サービス設定（初回、手動で作成）
- **サービス名**: `nextjs-app`（GitHub Secretsと一致させる）
- **リージョン**: `asia-northeast1`（任意のリージョン）
- 「**次へ**」をクリック

**注意**: 初回のみ手動で作成します。以降はCI/CDで自動デプロイされます。

---

## ステップ8: デプロイの確認

### 8-1. GitHub Actionsの実行
1. `.github/workflows/deploy.yml` ファイルをリポジトリにプッシュ
2. GitHubリポジトリの「**Actions**」タブを開く
3. ワークフローが実行されていることを確認
4. 成功すれば、Cloud Runでサービスが更新されます

### 8-2. Cloud Runサービスの確認
1. GCPコンソールで「**Cloud Run**」に移動
2. 作成したサービスをクリック
3. 「**URL**」をクリックしてアプリにアクセス

---

## トラブルシューティング

### エラー: "Permission denied"
- サービスアカウントに必要なロールが付与されているか確認
- Workload Identity連携が正しく設定されているか確認

### エラー: "Repository not found"
- Artifact Registryリポジトリのパスが正しいか確認
- サービスアカウントに `artifactregistry.writer` ロールがあるか確認

### エラー: "Workload Identity Provider not found"
- GitHub Secretsの `WORKLOAD_IDENTITY_PROVIDER` の値が正しいか確認
- 完全名（projects/...の形式）を使用しているか確認

---

## 参考情報

- [Workload Identity連携のドキュメント](https://cloud.google.com/iam/docs/workload-identity-federation)
- [Cloud Run のドキュメント](https://cloud.google.com/run/docs)
- [Artifact Registry のドキュメント](https://cloud.google.com/artifact-registry/docs)

