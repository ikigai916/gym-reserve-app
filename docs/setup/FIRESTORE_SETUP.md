# Firestore セットアップガイド

## 重要なポイント

**Firestoreでは、コレクションは自動的に作成されます。**
- 最初のドキュメントを保存するときに、コレクションが自動的に作成されます
- 手動でコレクションを作成する必要はありません

## セットアップ手順

### 1. Firestoreデータベースの作成（初回のみ）

1. [GCPコンソール](https://console.cloud.google.com/)にアクセス
2. プロジェクトを選択
3. 左メニューから「**Firestore Database**」をクリック
4. 「**データベースを作成**」をクリック

#### データベースの設定
- **モード**: **ネイティブモード**を選択（推奨）
- **場所**: `asia-northeast1`（東京）または任意のリージョン
- 「**有効にする**」をクリック

### 2. セキュリティルールの設定（開発用）

開発環境では、一時的にすべての読み書きを許可することもできます：

1. Firestore Database ページで「**ルール**」タブをクリック
2. 以下のルールを設定（**本番環境では適切なセキュリティルールを設定してください**）：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 開発用：すべての読み書きを許可（本番では変更が必要）
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

3. 「**公開**」をクリック

### 3. ローカル開発環境での認証設定

ローカル環境でFirestoreを使用するには、認証情報を設定する必要があります：

#### 方法1: サービスアカウントキーを使用（推奨）

1. GCPコンソールで「**IAMと管理**」→「**サービスアカウント**」
2. サービスアカウントを作成または選択
3. 「**キー**」タブ→「**キーを追加**」→「**JSONを作成**」
4. ダウンロードしたJSONファイルを `backend/` ディレクトリに配置
5. 環境変数を設定：

```bash
export GOOGLE_APPLICATION_CREDENTIALS="backend/service-account-key.json"
```

#### 方法2: gcloud CLIを使用

```bash
gcloud auth application-default login
```

### 4. コレクションの作成（自動）

コレクションは、アプリケーションが最初のドキュメントを保存するときに自動的に作成されます。

- **`users` コレクション**: `/api/users` エンドポイントでユーザーを作成したときに自動生成
- **`reservations` コレクション**: `/reservations` エンドポイントで予約を作成したときに自動生成

### 5. 動作確認

1. バックエンドサーバーを起動
2. ログインページでユーザーを作成
3. GCPコンソールのFirestore Databaseページで、`users`コレクションが作成されていることを確認

## トラブルシューティング

### エラー: "Permission denied"

- セキュリティルールを確認してください
- 認証情報が正しく設定されているか確認してください

### エラー: "Database not found"

- Firestoreデータベースが作成されているか確認してください
- プロジェクトIDが正しいか確認してください

### エラー: "Authentication failed"

- `GOOGLE_APPLICATION_CREDENTIALS` 環境変数が正しく設定されているか確認
- サービスアカウントキーファイルのパスが正しいか確認

## 参考リンク

- [Firestore のドキュメント](https://cloud.google.com/firestore/docs)
- [Firestore セキュリティルール](https://firebase.google.com/docs/firestore/security/get-started)


