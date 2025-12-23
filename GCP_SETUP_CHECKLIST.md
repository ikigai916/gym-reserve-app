# GCP設定チェックリスト

このチェックリストに従って、GCPコンソールで設定を進めてください。

## ✅ ステップ1: API有効化

- [ ] Cloud Run API (`run.googleapis.com`)
- [ ] Artifact Registry API (`artifactregistry.googleapis.com`)
- [ ] Secret Manager API (`secretmanager.googleapis.com`)
- [ ] IAM Service Account Credentials API (`iamcredentials.googleapis.com`)
- [ ] Cloud Build API (`cloudbuild.googleapis.com`)

**確認方法**: 「APIとサービス」→「ライブラリ」で検索して有効化

---

## ✅ ステップ2: Artifact Registryリポジトリ

- [ ] リポジトリ名: `docker-repo`（または任意の名前）
- [ ] 形式: `Docker`
- [ ] リージョン: `asia-northeast1`（メモ: _________）

**リポジトリパスをメモ**:
```
[リージョン]-docker.pkg.dev/[PROJECT-ID]/[リポジトリ名]
例: asia-northeast1-docker.pkg.dev/my-project-123456/docker-repo
```

---

## ✅ ステップ3: Secret Manager（必要な場合）

作成したシークレットをメモ:
- [ ] シークレット名: `_____________`
- [ ] その他: `_____________`

---

## ✅ ステップ4: サービスアカウント

- [ ] サービスアカウント名: `github-actions-deploy`
- [ ] メールアドレスをコピー: `________________________________@[PROJECT-ID].iam.gserviceaccount.com`

**付与したロール**:
- [ ] Cloud Run 開発者 (`roles/run.admin`)
- [ ] Artifact Registry ライター (`roles/artifactregistry.writer`)
- [ ] サービスアカウント ユーザー (`roles/iam.serviceAccountUser`)
- [ ] Secret Manager シークレット アクセス権 (`roles/secretmanager.secretAccessor`)
- [ ] Storage オブジェクト作成者 (`roles/storage.objectCreator`)

---

## ✅ ステップ5: Workload Identity連携

- [ ] プール名: `github-actions-pool`
- [ ] プロバイダー名: `github-provider`

**Workload Identityプールの完全名をコピー**:
```
projects/[PROJECT-NUMBER]/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider
```
メモ: `________________________________________________________`

- [ ] サービスアカウントに `Workload Identity ユーザー` ロールを付与

---

## ✅ ステップ6: GitHub Secrets設定

GitHubリポジトリの「Settings」→「Secrets and variables」→「Actions」で以下を設定:

- [ ] `WORKLOAD_IDENTITY_PROVIDER`: （ステップ5の完全名）
- [ ] `SERVICE_ACCOUNT`: （ステップ4のメールアドレス）
- [ ] `GCP_PROJECT_ID`: `_____________`
- [ ] `GCP_REGION`: `asia-northeast1`（または使用するリージョン）
- [ ] `ARTIFACT_REGISTRY_REPO`: `docker-repo`（ステップ2のリポジトリ名）
- [ ] `ARTIFACT_REGISTRY_LOCATION`: `asia-northeast1`（ステップ2のリージョン）
- [ ] `CLOUD_RUN_SERVICE`: `nextjs-app`（または任意のサービス名）

---

## ✅ ステップ7: Cloud Runサービス（初回のみ）

- [ ] サービス名: `nextjs-app`（GitHub Secretsと一致）
- [ ] リージョン: `asia-northeast1`
- [ ] 手動で作成（初回のみ）

---

## 📝 重要な値のメモ欄

| 項目 | 値 |
|------|-----|
| GCPプロジェクトID | |
| GCPプロジェクト番号 | |
| Artifact Registryリポジトリパス | |
| サービスアカウントメール | |
| Workload Identityプール完全名 | |
| Cloud RunサービスURL | |

---

## 🔍 確認コマンド（オプション）

GCP Cloud Shellで実行して設定を確認:

```bash
# プロジェクトIDの確認
gcloud config get-value project

# プロジェクト番号の確認
gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)'

# サービスアカウントの確認
gcloud iam service-accounts list

# Workload Identityプールの確認
gcloud iam workload-identity-pools list --location=global

# Artifact Registryリポジトリの確認
gcloud artifacts repositories list
```

