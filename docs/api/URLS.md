# 確認用URL一覧

## 開発環境（ローカル）

バックエンドを起動後、以下のURLで確認できます：

### メインページ
- **http://localhost:8000/** または **http://localhost:8000/index.html**
  - カレンダーと予約機能

### ログインページ
- **http://localhost:8000/login.html**
  - ユーザー登録・ログイン

### APIエンドポイント
- **http://localhost:8000/health**
  - ヘルスチェック

- **http://localhost:8000/reservations**
  - GET: 予約一覧を取得
  - POST: 予約を保存

## バックエンドの起動方法

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 本番環境（GCP Cloud Run）

Cloud Runにデプロイ後、サービスURLが表示されます。例：
- **https://[SERVICE-NAME]-[HASH]-an.a.run.app/**

GCPコンソールのCloud Runページで確認できます。

