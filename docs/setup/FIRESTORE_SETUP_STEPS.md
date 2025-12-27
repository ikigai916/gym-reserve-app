# Firestore認証設定とサーバー再起動の手順

## ステップ1: Firestore認証を設定

ターミナルで以下のコマンドを実行してください：

```bash
gcloud auth application-default login
```

**実行後の流れ：**
1. ブラウザが自動的に開きます
2. Googleアカウントでログインします（GCPプロジェクトの所有者アカウント）
3. 「Google Cloud SDK wants to access your Google Account」という画面で「許可」をクリック
4. 「認証が完了しました」というメッセージが表示されます

---

## ステップ2: バックエンドサーバーを再起動

### 2-1. 現在のサーバーを停止

サーバーを起動しているターミナルで、`Ctrl + C` を押してサーバーを停止します。

### 2-2. サーバーを再起動

同じターミナルで以下のコマンドを実行：

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

**成功すると、以下のようなメッセージが表示されます：**

```
INFO:     Will watch for changes in these directories: ['/Users/tmk916u/reseve/backend']
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Firestore client initialized successfully
INFO:     Application startup complete.
```

「Firestore client initialized successfully」というメッセージが表示されればOKです。

---

## ステップ3: ログインを試す

1. ブラウザで http://localhost:8080/login.html にアクセス
2. 名前を入力（例: "tomoki"）
3. メールアドレスを入力（任意）
4. 「ログイン / 新規登録」ボタンをクリック
5. 数秒待つと、成功メッセージが表示され、メイン画面に遷移します

---

## ステップ4: Firestoreでコレクションを確認

1. [GCPコンソール](https://console.cloud.google.com/)にアクセス
2. 左メニューから「**Firestore Database**」をクリック
3. 「**データ**」タブ（または「**Firestore Studio**」）をクリック
4. 左側のコレクション一覧に「**users**」が表示されていることを確認
5. 「**users**」をクリックすると、作成されたユーザーが表示されます

---

## トラブルシューティング

### サーバーが起動しない

- ポート8080が使用中の場合は、ポート8000を使用：
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

### 認証エラーが出る

- 再度認証を設定：
  ```bash
  gcloud auth application-default login
  ```

### プロジェクトIDが違う

- 正しいプロジェクトIDを設定：
  ```bash
  gcloud config set project gym-reserve-app
  ```
  （`gym-reserve-app` は実際のプロジェクトIDに置き換えてください）


