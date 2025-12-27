# Docker コマンド運用方法 (ローカル開発)

このドキュメントでは、本プロジェクトにおける Docker を使用したローカル開発および動作確認の手順について説明します。

## 1. 基本コマンド

### 1.1 イメージのビルド

プロジェクトのルートディレクトリで以下のコマンドを実行します。

```bash
docker build -t reseve-app .
```

### 1.2 コンテナの起動

ビルドしたイメージを使用してコンテナを起動します。
本プロジェクトは Cloud Run の仕様に合わせ、デフォルトでポート **8080** を使用します。

```bash
docker run -p 8080:8080 --name reseve-container reseve-app
```

起動後、ブラウザで `http://localhost:8080` にアクセスして動作を確認できます。

### 1.3 コンテナの停止と削除

```bash
# 停止
docker stop reseve-container

# 削除
docker rm reseve-container
```

---

## 2. 開発時の便利な運用方法

### 2.1 ホットリロードを有効にする (バインドマウント)

Dockerfile ではコードをイメージ内にコピーしていますが、開発中にコードの変更を即座に反映させたい場合は、ローカルの `app` ディレクトリをコンテナにマウントし、`uvicorn` の `--reload` オプションを有効にして起動します。

```bash
docker run -p 8080:8080 \
  -v $(pwd)/app:/app/app \
  --name reseve-container \
  reseve-app \
  uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 2.2 環境変数の指定

CORSの設定（`ALLOWED_ORIGINS`）などを変更したい場合は `-e` オプションを使用します。

```bash
docker run -p 8080:8080 \
  -e ALLOWED_ORIGINS="http://localhost:3000" \
  --name reseve-container \
  reseve-app
```

### 2.3 ログの確認

コンテナがバックグラウンドで動いている場合や、詳細なログを確認したい場合に使用します。

```bash
docker logs -f reseve-container
```

### 2.4 コンテナ内へのアクセス

デバッグのためにコンテナ内のシェルに入りたい場合に使用します。

```bash
docker exec -it reseve-container /bin/bash
```

---

## 3. トラブルシューティング

### 3.1 ポート競合

`Bind for 0.0.0.0:8080 failed: port is already allocated` と表示される場合は、他のプロセス（または以前のコンテナ）が 8080 ポートを使用しています。

```bash
# 実行中のコンテナを確認
docker ps

# 以前のコンテナが残っている場合は削除
docker rm -f reseve-container
```

### 3.2 イメージのクリーンアップ

ビルドを繰り返してディスク容量が不足した場合は、未使用のイメージを削除してください。

```bash
docker image prune
```

## 4. Google Cloud 認証設定 (重要)

FirestoreなどのGoogle Cloudサービスを利用する場合、ローカルの認証情報をコンテナにマウントする必要があります。

### 4.1 事前準備 (ホストマシン)
まず、ホストマシンで認証情報を生成しておきます。
```bash
gcloud auth application-default login
```

### 4.2 認証情報を含めた起動
生成された認証ファイルをコンテナにマウントして実行します。

```bash
docker run -p 8080:8080 \
  -v "$HOME/.config/gcloud:/root/.config/gcloud" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json \
  -e GOOGLE_CLOUD_PROJECT="gym-reserve-app" \
  --name reseve-container \
  reseve-app
```

### 4.3 認証切れ (RefreshError) の対応
`google.auth.exceptions.RefreshError: Reauthentication is needed.` というエラーが出た場合、または Firestore へのアクセスで処理が止まった場合は、ホストマシン（Mac）側で以下のコマンドを実行して再ログインしてください。

```bash
gcloud auth application-default login
```
ログイン完了後、Docker コンテナを再起動します。

---

## 5. よくあるエラーと解決策

- [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md)
- [SECURITY_CHECKLIST.md](../api/SECURITY_CHECKLIST.md)

