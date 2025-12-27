# 問題・解決・背景 (TROUBLESHOOTING HISTORY)

本ドキュメントは、開発中に発生した問題、その解決策、および背後にある原因を記録します。

## 1. Dockerコンテナ内からのFirestore接続エラー

### 問題
Dockerコンテナを起動した際、以下のエラーが発生してFirestoreに接続できなかった。
`google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found.`

### 原因
ホストマシンで `gcloud auth application-default login` を実行していても、Dockerコンテナは独立した環境であるため、その認証情報がコンテナ内に存在しなかった。

### 解決策
ホストマシンの認証ディレクトリをコンテナにマウントし、環境変数でそのパスを指定する。
```bash
docker run -v "$HOME/.config/gcloud:/root/.config/gcloud" \
           -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json \
           ...
```

---

## 2. Dockerコンテナ名の競合

### 問題
`docker run --name reseve-container ...` を実行した際、以下のエラーが発生。
`Conflict. The container name "/reseve-container" is already in use.`

### 原因
以前実行したコンテナが停止状態で残っており、同じ名前を再利用できなかった。

### 解決策
既存のコンテナを削除してから再実行する。
```bash
docker rm -f reseve-container
```
または、`docker run --rm` オプションを付けて、停止時に自動削除するようにする。

---

## 3. GCPプロジェクトIDの未設定

### 問題
認証情報はマウントしたが、以下のエラーが発生。
`OSError: Project was not passed and could not be determined from the environment.`

### 原因
FirestoreクライアントがどのGCPプロジェクトを使用すべきか判断できなかった。

### 解決策
環境変数 `GOOGLE_CLOUD_PROJECT` を指定して起動する。
```bash
-e GOOGLE_CLOUD_PROJECT="gym-reserve-app"
```

---

## 4. Google Cloud 認証切れ (RefreshError)

### 問題
コンテナ起動後、フロントエンドで「処置中...」のまま動かなくなり、サーバーログに以下のエラーが出力された。
`google.auth.exceptions.RefreshError: Reauthentication is needed.`

### 原因
ホストマシン側に保存されていた Google Cloud の認証トークンが期限切れになっており、Firestore との通信に必要なアクセス権を更新できなかった。

### 解決策
ホストマシン側で再認証を行い、トークンを更新してからコンテナを再起動する。
```bash
gcloud auth application-default login
```
その後、コンテナを削除・再起動。

