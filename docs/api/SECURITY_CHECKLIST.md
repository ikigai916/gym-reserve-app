# セキュリティチェックリスト

実装前に必ずこのチェックリストを確認してください。本番環境へのデプロイ前に、すべての項目を確認することが重要です。

## 1. CORS設定

### 開発環境

```python
# ❌ 本番環境では使用不可
allow_origins=["*"]
```

### 本番環境

```python
# ✅ 本番環境では適切なオリジンを指定
allow_origins=[
    "https://your-domain.com",
    "https://www.your-domain.com"
]
```

**チェック項目：**
- [ ] 本番環境では `allow_origins=["*"]` を使用していない
- [ ] 環境変数でCORS設定を管理している
- [ ] 必要なオリジンのみを許可している

**実装方法：**
```python
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 2. 認証・認可

### APIエンドポイント

**チェック項目：**
- [ ] 認証が必要なエンドポイントには認証チェックを実装している
- [ ] ユーザーIDによる適切な権限チェックを実装している
- [ ] 他のユーザーのデータにアクセスできないように制限している

**実装例：**
```python
@app.get("/api/users/{user_id}")
async def get_user(user_id: str, current_user_id: str = Depends(get_current_user)):
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="権限がありません")
    # ...
```

## 3. 環境変数とシークレット

### 機密情報の管理

**チェック項目：**
- [ ] パスワード、APIキー、秘密鍵などをコードに直接記述していない
- [ ] 環境変数またはSecret Managerを使用している
- [ ] `.env` ファイルを `.gitignore` に追加している
- [ ] 本番環境ではGCP Secret Managerを使用している

**実装方法：**
```python
import os
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    project_id = os.getenv("GCP_PROJECT_ID")
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

## 4. データベースセキュリティ

### Firestoreセキュリティルール

**チェック項目：**
- [ ] 開発用の全許可ルール（`allow read, write: if true;`）を本番環境で使用していない
- [ ] 適切なセキュリティルールを設定している
- [ ] ユーザーIDによるアクセス制御を実装している

**本番環境用セキュリティルール例：**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /reservations/{reservationId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && 
        resource.data.userId == request.auth.uid;
    }
  }
}
```

## 5. 入力値検証

### バリデーション

**チェック項目：**
- [ ] すべての入力値に適切なバリデーションを実装している
- [ ] SQLインジェクション対策（Firestoreは自動的に対応）
- [ ] XSS対策（出力時のエスケープ）
- [ ] 日付、数値などの型チェック

**実装例：**
```python
from pydantic import BaseModel, validator, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('名前は必須です')
        if len(v) > 100:
            raise ValueError('名前は100文字以内で入力してください')
        return v.strip()
```

## 6. エラーハンドリング

### エラーメッセージ

**チェック項目：**
- [ ] 機密情報を含むエラーメッセージを返していない
- [ ] 詳細なエラーメッセージをクライアントに返していない（ログに記録）
- [ ] 適切なHTTPステータスコードを返している

**実装例：**
```python
try:
    # 処理
except Exception as e:
    logger.error(f"Internal error: {e}", exc_info=True)
    raise HTTPException(
        status_code=500, 
        detail="内部エラーが発生しました"  # 詳細なエラー情報は返さない
    )
```

## 7. Cloud Run設定

### IAMとアクセス制御

**チェック項目：**
- [ ] 本番環境では `--allow-unauthenticated` を適切に設定している
- [ ] 必要に応じて認証を要求している
- [ ] 最小権限の原則に従ってIAMロールを設定している

### 環境変数

**チェック項目：**
- [ ] 機密情報はSecret Managerから読み込んでいる
- [ ] 環境変数は適切に設定されている

## 8. ログと監視

### ログ出力

**チェック項目：**
- [ ] 機密情報（パスワード、トークンなど）をログに出力していない
- [ ] 適切なログレベルを使用している
- [ ] エラーログを適切に記録している

**実装例：**
```python
import logging

logger = logging.getLogger(__name__)

# ✅ 良い例
logger.info(f"User {user_id} created")

# ❌ 悪い例（パスワードをログに出力）
logger.info(f"User created with password: {password}")
```

## 9. 依存関係のセキュリティ

### パッケージ管理

**チェック項目：**
- [ ] 依存関係のバージョンを固定している（`requirements.txt`）
- [ ] 定期的に依存関係の脆弱性をチェックしている
- [ ] 最新のセキュリティパッチを適用している

**確認コマンド：**
```bash
# Python依存関係の脆弱性チェック（safetyを使用）
pip install safety
safety check -r requirements.txt
```

## 10. デプロイ前の最終確認

### デプロイ前チェックリスト

- [ ] 上記すべてのセキュリティ項目を確認した
- [ ] ローカル環境で動作確認した
- [ ] セキュリティ設定が本番環境で適切に設定されている
- [ ] 機密情報がコードに含まれていない
- [ ] セキュリティルールが適切に設定されている
- [ ] ログに機密情報が出力されていない

## 参考資料

- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/advanced/security/)
- [GCP Security Best Practices](https://cloud.google.com/security/best-practices)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)

