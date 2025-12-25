# CORS設定ガイド

## 概要

CORS設定を環境変数で管理することで、開発環境と本番環境で適切なオリジンを設定できます。

## 開発環境

### デフォルト値

開発環境では、以下のオリジンがデフォルトで許可されます：

- `http://localhost:8000`
- `http://localhost:3000`
- `http://127.0.0.1:8000`
- `http://127.0.0.1:3000`

### 環境変数の設定（必要に応じて）

追加のオリジンを許可する場合：

```bash
export ALLOWED_ORIGINS="http://localhost:8000,http://localhost:3000,http://localhost:8080"
```

## 本番環境（Cloud Run）

### 環境変数の設定方法

Cloud Runにデプロイする際、`ALLOWED_ORIGINS`環境変数を設定する必要があります。

#### 方法1: GitHub Actionsワークフローで設定（推奨）

`.github/workflows/deploy.yml`に環境変数を追加：

```yaml
- name: 'Deploy to Cloud Run'
  run: |-
    gcloud run deploy ${{ env.SERVICE_NAME }} \
      --image "${{ env.GAR_LOCATION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPOSITORY }}/${{ env.SERVICE_NAME }}:${{ github.sha }}" \
      --region ${{ env.REGION }} \
      --platform managed \
      --allow-unauthenticated \
      --set-env-vars ALLOWED_ORIGINS="https://your-domain.com,https://www.your-domain.com" \
      --project ${{ env.PROJECT_ID }}
```

#### 方法2: GCPコンソールで設定

1. [GCPコンソール](https://console.cloud.google.com/)にアクセス
2. 「Cloud Run」を選択
3. サービス名（例: `gym-reserve-app`）をクリック
4. 「編集と新しいリビジョンをデプロイ」をクリック
5. 「変数とシークレット」タブを開く
6. 「環境変数を追加」をクリック
7. 以下を設定：
   - **名前**: `ALLOWED_ORIGINS`
   - **値**: `https://your-domain.com,https://www.your-domain.com`
8. 「デプロイ」をクリック

#### 方法3: gcloud CLIで設定

```bash
gcloud run services update gym-reserve-app \
  --region asia-northeast1 \
  --set-env-vars ALLOWED_ORIGINS="https://your-domain.com,https://www.your-domain.com"
```

### 設定例

#### 単一のドメインを許可

```bash
ALLOWED_ORIGINS="https://gym-reserve-app.example.com"
```

#### 複数のドメインを許可

```bash
ALLOWED_ORIGINS="https://gym-reserve-app.example.com,https://www.gym-reserve-app.example.com"
```

#### 開発環境と本番環境の両方を含める

```bash
ALLOWED_ORIGINS="https://gym-reserve-app.example.com,http://localhost:8000"
```

**注意**: 本番環境では開発環境のオリジンを含めないことを推奨します。

## 動作確認

### ローカル環境での確認

1. バックエンドサーバーを起動

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. ブラウザの開発者ツールでCORSヘッダーを確認

- NetworkタブでAPIリクエストを確認
- レスポンスヘッダーに `Access-Control-Allow-Origin` が含まれていることを確認
- 許可されていないオリジンからのリクエストでは、CORSエラーが発生することを確認

### 本番環境での確認

1. Cloud Runの環境変数が正しく設定されているか確認

```bash
gcloud run services describe gym-reserve-app \
  --region asia-northeast1 \
  --format="value(spec.template.spec.containers[0].env)"
```

2. ブラウザの開発者ツールでCORSヘッダーを確認

- 本番環境のURLからAPIリクエストを送信
- レスポンスヘッダーに `Access-Control-Allow-Origin` が含まれていることを確認
- 許可されていないオリジンからのリクエストでは、CORSエラーが発生することを確認

## トラブルシューティング

### CORSエラーが発生する

**原因:**
- リクエスト元のオリジンが `ALLOWED_ORIGINS` に含まれていない

**解決方法:**
1. リクエスト元のオリジンを確認
2. `ALLOWED_ORIGINS` 環境変数にオリジンを追加
3. サービスを再デプロイ

### 環境変数が反映されない

**原因:**
- 環境変数の設定後にサービスが再デプロイされていない

**解決方法:**
1. Cloud Runサービスを再デプロイ
2. 環境変数が正しく設定されているか確認

## セキュリティ上の注意

- **本番環境では `allow_origins=["*"]` を使用しない**
- **許可するオリジンは必要最小限に留める**
- **開発環境のオリジンを本番環境に含めない**
- **定期的に許可されているオリジンを見直す**

