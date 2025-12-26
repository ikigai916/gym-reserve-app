# トラブルシューティングガイド

## ログインが「処理中」のまま止まる

### 原因
Firestoreへの認証情報が設定されていない可能性があります。

### 解決方法

#### 1. Firestore認証を設定

```bash
gcloud auth application-default login
```

このコマンドを実行すると、ブラウザが開いてGoogleアカウントでログインを求められます。
ログイン後、認証情報が保存されます。

#### 2. プロジェクトIDを確認・設定

Firestoreを使用するGCPプロジェクトのIDが正しく設定されているか確認:

```bash
gcloud config get-value project
```

プロジェクトIDを設定する場合:

```bash
gcloud config set project gym-reserve-app
```

（`gym-reserve-app` は実際のプロジェクトIDに置き換えてください）

#### 3. バックエンドサーバーを再起動

認証設定後、バックエンドサーバーを再起動してください:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### 4. サーバーログを確認

サーバーを起動しているターミナルで、エラーメッセージを確認してください。
Firestoreクライアントの初期化でエラーが出ている場合は、上記の認証設定が必要です。

### 確認方法

以下のコマンドで認証が正しく設定されているか確認できます:

```bash
gcloud auth application-default print-access-token
```

トークンが表示されれば、認証は正常に設定されています。

## その他のよくある問題

### ポート8080が既に使用されている

別のプロセスがポート8080を使用している場合:

```bash
# 使用しているプロセスを確認
lsof -i :8080

# プロセスを停止（PIDを確認してから）
kill -9 <PID>
```

または、別のポートを使用:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 「Failed to fetch」エラー

- バックエンドサーバーが起動しているか確認
- ブラウザの開発者ツールのNetworkタブで、リクエストのステータスを確認
- CORSエラーが出ていないか確認


