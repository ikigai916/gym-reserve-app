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

---

## 5. bcrypt の 72バイト制限

### 問題
パスワードが長い場合にハッシュ化でエラーが発生。
`password cannot be longer than 72 bytes`

### 原因
bcrypt アルゴリズムの仕様により、入力可能なパスワードの長さが 72 バイトに制限されている。日本語などのマルチバイト文字を使用すると文字数以上にバイト数が膨らむ。

### 解決策
1. `app/core/auth.py` にて、ハッシュ化前にパスワードを 72 バイト（UTF-8エンコード）で切り捨てる処理を追加。
2. Pydantic スキーマにて `max_length=72` を設定し、クライアント側でもバリデーションを行う。

---

## 6. Firestore 複合インデックス不足による 500 エラー

### 問題
予約取得などで `where` と `order_by` を組み合わせた際、以下のエラーが発生。
`400 The query requires an index. You can create it here: ...`

### 原因
Firestore では複数のフィールドを組み合わせた複雑なクエリには「複合インデックス」が必要。

### 解決策
1. エラーメッセージに含まれるURLをクリックし、Google Cloud Console でインデックスを作成する。
2. （暫定対応）インデックス作成を待てない場合、バックエンドの `order_by` を削除し、フロントエンド側でソート処理を行う。

---

## 7. Cloud Run コンテナ起動失敗 (Port 8080 timeout)

### 問題
デプロイ時にコンテナがポート 8080 で起動せず、タイムアウトで失敗する。

### 原因
主な原因は以下の通り：
- `app/main.py` で削除済みのレガシー関数をインポートしようとして `ImportError` が発生。
- Firestore クライアントがインポート時に即座に接続を試み、認証情報がない場合にクラッシュしていた。
- `requirements.txt` に `aiofiles` が不足しており、静的ファイル配信の初期化で失敗。
- Dockerfile の `CMD` が正しく `$PORT` 環境変数を受け取れていなかった。

### 解決策
- インポートの整理と詳細なロギングの追加。
- `app/core/database.py` にて Firestore クライアントの遅延初期化（Lazy Initialization）を導入。
- 依存パッケージ（aiofiles）の追加。
- Dockerfile の `CMD` を `$PORT` 対応に修正。

---

## 8. 予約キャンセル時のトランザクション順序違反

### 問題
予約キャンセル時に 500 Internal Server Error が発生。ログに `Transactions must perform all gets before any puts` に相当する違反が記録された。

### 原因
Firestore のトランザクション制約により、同じトランザクション内では「読み取り(GET)」をすべて完了した後に「書き込み(UPDATE/SET)」を行う必要がある。既存コードでは予約情報の更新を先に、関連スロットの取得を後に行っていた。

### 解決策
`app/api/endpoints/reservations.py` 内のロジックを修正。
1. `avail_query.get(transaction=transaction)` による読み取りを最初に実施。
2. その後、`transaction.update()` による書き込みをまとめて実施。
