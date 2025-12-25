# ブラウザでのCORS設定確認方法

## 確認手順

### 1. ログインページにアクセス

ブラウザで以下のURLを開いてください：

```
http://localhost:8000/login.html
```

### 2. 開発者ツールで確認

#### Chrome/Edgeの場合

1. **F12キー**または**右クリック → 検証**で開発者ツールを開く
2. **Network（ネットワーク）**タブを開く
3. ログインページで名前を入力して「ログイン / 新規登録」ボタンをクリック
4. ネットワークタブで `/api/users` リクエストをクリック
5. **Headers（ヘッダー）**タブで以下を確認：
   - **Request Headers（リクエストヘッダー）**:
     - `Origin: http://localhost:8000` が含まれていることを確認
   - **Response Headers（レスポンスヘッダー）**:
     - `Access-Control-Allow-Origin: http://localhost:8000` が含まれていることを確認
     - `Access-Control-Allow-Credentials: true` が含まれていることを確認

#### Firefoxの場合

1. **F12キー**で開発者ツールを開く
2. **ネットワーク**タブを開く
3. ログインページで名前を入力して「ログイン / 新規登録」ボタンをクリック
4. `/api/users` リクエストをクリック
5. **ヘッダー**タブで同様に確認

### 3. 正常動作の確認

以下の動作が正常にできることを確認：

- ✅ ログインページが表示される
- ✅ 名前を入力してログインできる
- ✅ メイン画面（予約カレンダー）に遷移する
- ✅ カレンダーが表示される
- ✅ 日付をクリックして予約モーダルが開く
- ✅ 予約を作成できる

### 4. CORSエラーの確認（オプション）

許可されていないオリジンからのリクエストでCORSエラーが発生することを確認：

1. ブラウザのコンソールを開く（開発者ツールのConsoleタブ）
2. 以下のコマンドを実行：

```javascript
fetch('http://localhost:8000/health', {
  headers: {
    'Origin': 'http://malicious-site.com'
  }
})
```

3. コンソールにCORSエラーが表示されることを確認

## 確認ポイント

### ✅ 正常な動作

- ログインページが正常に表示される
- APIリクエストが成功する
- レスポンスヘッダーに `Access-Control-Allow-Origin` が含まれている
- エラーが発生しない

### ⚠️ 問題がある場合

以下のような問題が発生する可能性があります：

1. **CORSエラーが表示される**
   - 原因: オリジンが許可されていない
   - 確認: `ALLOWED_ORIGINS` 環境変数に `http://localhost:8000` が含まれているか

2. **APIリクエストが失敗する**
   - 原因: サーバーが起動していない、または別の問題
   - 確認: サーバーのログを確認

3. **予約データが取得できない**
   - 原因: Firestore認証の問題
   - 確認: `gcloud auth application-default login` を実行

## トラブルシューティング

### サーバーが起動していない場合

ターミナルで以下を実行：

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Firestore認証エラーが発生する場合

```bash
gcloud auth application-default login
```

サーバーを再起動してください。

