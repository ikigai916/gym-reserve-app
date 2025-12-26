# 現在のセキュリティ問題

このドキュメントでは、現在のコードベースに存在するセキュリティ問題を説明します。

## 🔴 重大な問題

### 1. CORS設定で全オリジンを許可（`allow_origins=["*"]`）

**問題箇所:** `backend/app/main.py:15`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ セキュリティリスク
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**問題点:**
- **すべてのオリジンからのアクセスを許可**している
- 本番環境でこの設定を使用すると、**任意のウェブサイトからAPIを呼び出せる**
- CSRF（Cross-Site Request Forgery）攻撃のリスクが高い
- 悪意のあるサイトからユーザーの認証情報やデータを盗まれる可能性がある

**影響範囲:**
- すべてのAPIエンドポイント
- ユーザー認証情報
- 予約データ

**リスクレベル:** 🔴 **高**

**修正方法:**
```python
import os

# 環境変数から許可するオリジンを取得（開発環境のデフォルト値を設定）
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:8000,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # ✅ 許可されたオリジンのみ
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**本番環境での設定:**
```bash
# Cloud Runの環境変数
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

---

## 🟡 中程度の問題

### 2. 認証・認可の実装不足

**問題箇所:** すべてのAPIエンドポイント

**現在の実装:**
- ユーザーIDはローカルストレージで管理しているが、**サーバー側で認証を検証していない**
- クライアントが任意の`userId`を送信できる可能性がある
- 他のユーザーのデータにアクセスされるリスクがある

**問題点:**
```python
# 現在の実装例（予約取得API）
@app.get("/reservations")
async def get_reservations():
    # ⚠️ 認証チェックがない
    # ⚠️ すべての予約を返す（フィルタリングがない）
    docs = db.collection("reservations").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]
```

**影響範囲:**
- `/reservations` - すべての予約データが取得可能
- `/api/users/{user_id}` - 任意のユーザー情報が取得可能
- 予約作成・削除時に他のユーザーとして操作可能

**リスクレベル:** 🟡 **中**

**修正方法:**
- 認証トークンの検証を実装
- 各APIエンドポイントで認証チェックを追加
- ユーザーIDによる権限チェックを実装

---

### 3. 入力値のバリデーション不足

**問題箇所:** `backend/app/main.py` の各エンドポイント

**現在の実装:**
```python
class Reservation(BaseModel):
    user_name: str  # ⚠️ 最小長、最大長のチェックがない
    date: str  # ⚠️ 日付形式の検証がない
```

**問題点:**
- 日付形式の検証がない（不正な形式の日付を受け入れる可能性）
- 文字列の長さ制限がない（DoS攻撃のリスク）
- メールアドレスの形式検証がない

**リスクレベル:** 🟡 **中**

**修正方法:**
```python
from pydantic import BaseModel, validator, EmailStr
from datetime import datetime

class Reservation(BaseModel):
    user_name: str
    
    @validator('user_name')
    def validate_user_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('名前は必須です')
        if len(v) > 100:
            raise ValueError('名前は100文字以内で入力してください')
        return v.strip()
    
    date: str
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError('日付はYYYY-MM-DD形式で入力してください')
        return v
```

---

### 4. エラーハンドリングでの情報漏洩リスク

**問題箇所:** `backend/app/main.py` の各エンドポイント

**現在の実装:**
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # ⚠️ 詳細なエラー情報を返している
```

**問題点:**
- 内部エラーの詳細情報（スタックトレース、ファイルパスなど）がクライアントに返される可能性がある
- システムの内部構造が漏洩するリスクがある

**リスクレベル:** 🟡 **中**

**修正方法:**
```python
import logging

logger = logging.getLogger(__name__)

try:
    # 処理
except Exception as e:
    logger.error(f"Internal error: {e}", exc_info=True)  # ログに記録
    raise HTTPException(
        status_code=500, 
        detail="内部エラーが発生しました"  # クライアントには汎用的なメッセージのみ
    )
```

---

## 🟢 軽微な問題

### 5. Firestoreセキュリティルールの確認

**問題点:**
- 開発用の全許可ルール（`allow read, write: if true;`）が本番環境でも使用されている可能性がある

**確認が必要:**
- GCPコンソールでFirestoreセキュリティルールを確認
- 本番環境では適切なセキュリティルールを設定

---

## 📋 修正の優先順位

| 問題 | リスクレベル | 優先度 | 修正工数 |
|------|------------|--------|---------|
| CORS設定 | 🔴 高 | 最優先 | 30分 |
| 認証・認可 | 🟡 中 | 高 | 2-3時間 |
| 入力値バリデーション | 🟡 中 | 中 | 1-2時間 |
| エラーハンドリング | 🟡 中 | 中 | 1時間 |
| Firestoreルール確認 | 🟢 低 | 低 | 30分 |

---

## 🎯 次のアクション

### 即座に対応が必要（本番デプロイ前）

1. ✅ **CORS設定の修正**
   - 環境変数で管理するように変更
   - 本番環境では適切なオリジンのみを許可

### 短期（1週間以内）

2. ✅ **認証・認可の実装**
   - 認証トークンの検証
   - ユーザーIDによる権限チェック

3. ✅ **入力値バリデーションの強化**
   - Pydanticのバリデーターを追加
   - 日付、文字列長の検証

4. ✅ **エラーハンドリングの改善**
   - 詳細なエラー情報をログに記録
   - クライアントには汎用的なメッセージのみ返す

### 中期（1ヶ月以内）

5. ✅ **Firestoreセキュリティルールの確認・設定**
   - 本番環境用のセキュリティルールを設定
   - 定期的なセキュリティ監査

---

## 📚 参考資料

- `SECURITY_CHECKLIST.md` - セキュリティチェックリスト
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)

